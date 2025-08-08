import argparse
import concurrent.futures
import datetime
import hashlib
import json
import logging
import os
import shutil
import time
from abc import ABC, abstractmethod
from urllib.parse import parse_qs

from mysql.connector import MySQLConnection, connect


def sha256sum(filepath: str) -> str:
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest()


def write_table_data_to_file(con: MySQLConnection, database, table, datafile):
    with con.cursor(dictionary=True) as cursor, open(datafile, "w", encoding="utf8") as file:
        cursor.execute(f"SELECT * FROM {database}.{table}")
        while True:
            rows = cursor.fetchmany(1000)
            if not rows:
                break
            for row in rows:
                file.write(f"{row}\n")


def hash_dict(d):
    # return frozenset(d.items())
    return frozenset((k, frozenset(v) if isinstance(v, set) else v) for k, v in d.items())


def find_missing_in_b(a, b):
    b_hashes = {hash_dict(d) for d in b}

    missing_in_b = [d for d in a if hash_dict(d) not in b_hashes]

    return missing_in_b


def mysql_query_tables(dsn: dict, db: str):
    with connect(**dsn) as con:
        cur = con.cursor()
        cur.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema = %s ORDER BY 1, 2", (db,))
        for db, tab in cur.fetchall():
            yield db, tab


def get_current_datetime():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def convert_value(value: str):
    if value.lower() == "true":
        return True
    elif value.lower() == "false":
        return False
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def mysql_parse_dsn(dsn: str) -> dict:
    if "?" in dsn:
        dsn, query_string = dsn.split("?", 1)
        params = parse_qs(query_string)
    else:
        params = {}

    _userpass, _hostport = dsn.split("@")
    _user, _pass = _userpass.split(":")
    _host, _port = _hostport.split(":")

    parsed_params = {key: convert_value(value[0]) if len(value) == 1 else [convert_value(v) for v in value] for key, value in params.items()}

    return {"host": _host, "port": _port, "user": _user, "password": _pass, "time_zone": "+00:00", **parsed_params}


def mysql_query_table_rows_number(con: MySQLConnection, database: str, table: str) -> int:
    with con.cursor() as cur:
        cur.execute("SELECT table_rows FROM information_schema.tables WHERE table_schema = %s AND table_name = %s", (database, table))
        (rows,) = cur.fetchone()
        return rows


def mysql_query_table_structure(con: MySQLConnection, database: str, table: str) -> list[tuple[str, str]]:
    with con.cursor() as cur:
        cur.execute(
            "SELECT column_name, CAST(data_type as char(255)) FROM information_schema.columns WHERE table_schema = %s AND table_name = %s ORDER BY ordinal_position",
            (database, table),
        )
        return cur.fetchall()


def mysql_delete_row(logger: logging.Logger, con: MySQLConnection, database: str, table: str, diff_row: dict) -> dict:
    where_clause = " AND ".join([f"`{col}` = %s" for col in diff_row.keys()])

    sql = f"DELETE FROM `{database}`.`{table}` WHERE {where_clause}"
    params = diff_row.values()

    logger.info(f"delete sql: {sql}, values: {params}")

    with con.cursor() as cur:
        cur.execute(sql, tuple(params))
        affected_rows = cur.rowcount
        logger.info(f"delete rows: {affected_rows}")
    con.commit()


def mysql_query_table_keys(con: MySQLConnection, database: str, table: str):
    operation = """
        SELECT tis.index_name, titc.constraint_type, tic.column_name, tic.data_type
        FROM information_schema.table_constraints titc
        JOIN information_schema.statistics tis ON titc.table_schema = tis.table_schema AND titc.table_name = tis.table_name AND titc.constraint_name = tis.index_name
        JOIN information_schema.columns tic ON tis.table_schema = tic.table_schema AND tis.table_name = tic.table_name AND tis.column_name = tic.column_name
        WHERE titc.constraint_type IN ('PRIMARY KEY', 'UNIQUE')
        AND titc.table_schema = %s
        AND titc.table_name = %s
    """

    with con.cursor() as cur:
        cur.execute(operation, (database, table))
        rows = cur.fetchall()

    pkeys = [(row[2], row[3]) for row in rows if row[1] == "PRIMARY KEY"]
    ukeys = [(row[2], row[3]) for row in rows if row[1] == "UNIQUE" and row[0] == rows[0][0]]

    return ukeys if len(pkeys) == 0 else pkeys


def mysql_query(con: MySQLConnection, query_statement: str, query_params) -> list[dict]:
    with con.cursor(dictionary=True, buffered=True) as cur:
        cur.execute(query_statement, tuple(query_params))
        return cur.fetchall()


def parse_args(external_args=None):
    parser = argparse.ArgumentParser(description="Parse databases and tables")

    parser.add_argument("--forward", action="store_true", help="Execute the forward script")
    parser.add_argument("--reverse", action="store_true", help="Execute the reverse script")

    parser.add_argument("--forward-nokey", action="store_true", help="Execute the reverse script")

    parser.add_argument("--forward-repair", action="store_true", help="Execute the forward script")
    parser.add_argument("--reverse-clear", action="store_true", help="Execute the reverse script")

    parser.add_argument("--src-dsn", type=str, required=True, help="List of tables")
    parser.add_argument("--dst-dsn", type=str, required=True, help="List of tables")

    parser.add_argument("--databases", nargs="+", default=[], help="List of databases")
    parser.add_argument("--tables", nargs="+", default=[], help="List of tables")
    parser.add_argument("--exclude-tables", nargs="+", default=[], help="List of tables")

    parser.add_argument("--batch-size", type=int, default=1000, help="List of tables")

    parser.add_argument("--parallel", type=int, default=1, help="Repair the tables")

    parser.add_argument("--delay-check", type=int, default=0, help="Repair the tables")

    parser.add_argument("--work-dir", type=str, default=datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"), help="Repair the tables")
    parser.add_argument("--work-dir-clear", action="store_true", help="Repair the tables")

    args = parser.parse_args(external_args)

    if not (args.forward or args.reverse):
        parser.error("At least one of --forward or --reverse must be provided")

    print(f"args: {args}")
    return args


def init_logger(name: str | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    handler = logging.FileHandler(f"{name}.log")
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


def get_elapsed_time(st: float, ndigits=None) -> int | float:
    return round(time.time() - st, ndigits)


def extract_keyvals(row: dict, keys: list[tuple[str, str]]):
    _keys = [item[0] for item in keys]
    new_dict = {}
    for key in row:
        if key in _keys:
            new_dict[key] = row[key]

    return new_dict


def mysql_repair_row(logger: logging.Logger, con: MySQLConnection, database: str, table: str, diff_row: dict):
    columns = ", ".join([f"`{col}`" for col in diff_row.keys()])
    values_placeholder = ", ".join(["%s"] * len(diff_row))

    sql = f"REPLACE INTO `{database}`.`{table}` ({columns}) VALUES ({values_placeholder});"
    params = tuple(diff_row.values())

    logger.info(f"repair sql: {sql}, values: {params}")
    with con.cursor() as cur:
        cur.execute(sql, params)
        affected_rows = cur.rowcount
        logger.info(f"repair rows: {affected_rows}")
    con.commit()


def mysql_query_row(con: MySQLConnection, database, table, table_keys, diff_row) -> dict | None:
    whereval = []
    params: list = []
    for coln, colt in table_keys:
        if "int" in colt or "char" in colt or "date" in colt or "decimal" in colt:
            whereval.append(f"`{coln}` = %s")
            params.append(diff_row[coln])
        else:
            raise Exception(f"data type: {colt} not suppert yet.")

    _stmt = f"SELECT * FROM `{database}`.`{table}` WHERE {' AND '.join(whereval)}"

    with con.cursor(dictionary=True) as cur:
        cur.execute(_stmt, params=tuple(params))
        return cur.fetchone()


def get_query_full_table_statement_params(database: str, table: str, table_keys, select_cols: list[str], limit_size: int, ckpt_row: dict = None):
    _keyval = ckpt_row
    # select * from where 1 = 1 and ((a > xxx) or (a = xxx and b > yyy) or (a = xxx and b = yyy and c > zzz)) order by a,b,c limit checksize
    orderby_clause = ", ".join([f"`{col[0]}`" for col in table_keys])

    select_clause = ", ".join(select_cols)

    for _, column_type in table_keys:
        if column_type in ["int", "double", "char", "date", "decimal", "varchar", "bigint", "tinyint", "smallint"]:
            pass
        else:
            raise ValueError(f"Data type: [{column_type}] is not supported yet.")

    where_conditions = []
    for end_idx in range(len(table_keys)):
        condition_parts = []
        for i, (column_name, _) in enumerate(table_keys[: end_idx + 1]):
            operator = ">" if i == end_idx else "="
            condition_parts.append(f"`{column_name}` {operator} %s")
        where_conditions.append(" and ".join(condition_parts))
    where_clause = "(" + ") or (".join(where_conditions) + ")"

    statement_with_condition = f"SELECT {select_clause} FROM `{database}`.`{table}` WHERE {where_clause} ORDER BY {orderby_clause} LIMIT {limit_size}"
    statement_without_condition = f"SELECT {select_clause} FROM `{database}`.`{table}` ORDER BY {orderby_clause} LIMIT {limit_size}"

    _params: list = []
    if _keyval:
        for end_idx in range(len(table_keys)):
            for i, (column_name, _) in enumerate(table_keys[: end_idx + 1]):
                _params.append(_keyval[column_name])

    statement = statement_with_condition if _params else statement_without_condition

    return statement, _params


class MysqlTableCompare(ABC):
    def __init__(
        self,
        compare_name: str,
        src_dsn: dict,
        dst_dsn: dict,
        src_db: str,
        src_tab: str,
        dst_db: str,
        dst_tab: str,
        limit_size: int = 2000,
        repair: bool = False,
        delay_check: int = 0,
    ) -> None:
        self.compare_name = compare_name

        self.source_dsn = src_dsn
        self.target_dsn = dst_dsn

        self.limit_size = limit_size

        self.src_db = src_db
        self.src_tab = src_tab
        self.dst_db = dst_db
        self.dst_tab = dst_tab

        self.table_keys = []
        self.source_table_ukeys = []

        self.is_repair = repair
        self.delay_check_wait = delay_check

        self.processed_rows_number = 0
        self.different_rows_number = 0

        self.compare_cols = []

    @abstractmethod
    def extract_next_keyval(self, source_rows, target_rows):
        pass

    @abstractmethod
    def process_diff_rows(self, source_con: MySQLConnection, target_con: MySQLConnection, source_rows: list[dict], target_rows: list[dict]):
        pass

    @abstractmethod
    def get_query_full_table_statement_params(self, keyval: dict = None):
        pass

    # def run(self):
    #     try:
    #         self._run()
    #     except Exception as e:
    #         self.logger.error(str(e))

    def run(self):
        self.logger = init_logger(self.compare_name)

        with connect(**self.source_dsn) as source_con, connect(**self.target_dsn) as target_con:
            source_table_struct: list[tuple[str, str]] = mysql_query_table_structure(source_con, self.src_db, self.src_tab)
            target_table_struct: list[tuple[str, str]] = mysql_query_table_structure(target_con, self.dst_db, self.dst_tab)

            self.logger.debug(f"source table structure: { source_table_struct}.")
            self.logger.debug(f"target table structure: { target_table_struct}.")

            if len(source_table_struct) == 0:
                self.logger.error("source table not exists.")
                raise Exception()

            if set(source_table_struct) != set(target_table_struct):
                self.logger.error("source and target table structure diff.")
                raise Exception()

            source_table_keys = mysql_query_table_keys(source_con, self.src_db, self.src_tab)
            target_table_keys = mysql_query_table_keys(target_con, self.dst_db, self.dst_tab)

            self.logger.debug(f"source table keys: {source_table_keys}.")

            self.logger.debug(f"target table keys: {target_table_keys}.")

            if len(source_table_keys) == 0:
                self.logger.error("The primary keys or unique keys not exists.")
                raise Exception()

            if set(source_table_keys) != set(target_table_keys):
                self.logger.error("The primary key or unique keys are not the same.")
                self.logger.debug(f"source table keys: {source_table_keys}.")
                self.logger.debug(f"target table keys: {target_table_keys}.")
                raise Exception()

            self.table_keys = source_table_keys.copy()

            self.logger.debug(f"table keys: {self.table_keys}.")

            self.source_table_rows_number = max(1, mysql_query_table_rows_number(source_con, self.src_db, self.src_tab))
            self.logger.debug(f"source table rows number: {self.source_table_rows_number}.")

        _keyval = None
        batch_id = 1
        with connect(**self.source_dsn) as source_con, connect(**self.target_dsn) as target_con:
            while True:
                query_statement_src, query_params_src = self.get_query_full_table_statement_params(_keyval)
                query_statement_dst, query_params_dst = self.get_query_full_table_statement_params(_keyval)

                self.logger.info(f"batch_id[{batch_id}] source query statment: '{query_statement_src}', params '{query_params_src}'")
                self.logger.info(f"batch_id[{batch_id}] target query statment: '{query_statement_dst}', params '{query_params_dst}'")

                source_rows = []
                target_rows = []

                _start1 = time.time()

                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    source_rows = executor.submit(mysql_query, source_con, query_statement_src, query_params_src).result()
                    target_rows = executor.submit(mysql_query, target_con, query_statement_dst, query_params_dst).result()

                if len(target_rows) == 0:
                    break

                self.processed_rows_number += len(source_rows)

                self.process_diff_rows(source_con, target_con, source_rows, target_rows)

                _keyval = self.extract_next_keyval(source_rows, target_rows)

                processed_progress = round(self.processed_rows_number / self.source_table_rows_number * 100, 2)
                self.logger.info(f"batch_id[{batch_id}] source rows: {len(source_rows)}, target rows: {len(target_rows)}.")
                self.logger.info(
                    f"batch_id[{batch_id}] processed rows number: {self.processed_rows_number}/{self.source_table_rows_number}, progress: {processed_progress}%, elapsed time: {get_elapsed_time(_start1, 2)}s."
                )


class MysqlTableCompareForwardNoKey:
    def __init__(self, compare_name: str, src_dsn: dict, dst_dsn: dict, src_db: str, src_tab: str, dst_db: str, dst_tab: str) -> None:
        self.source_dsn = src_dsn
        self.target_dsn = dst_dsn

        self.src_db = src_db
        self.src_tab = src_tab
        self.dst_db = dst_db
        self.dst_tab = dst_tab

    def run(self):
        src_file = f"{self.src_db}.{self.src_tab}.src.nokey.log"
        dst_file = f"{self.dst_db}.{self.dst_tab}.dst.nokey.log"

        with connect(**self.source_dsn) as source_con, connect(**self.target_dsn) as target_con:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                executor.submit(write_table_data_to_file, source_con, self.src_db, self.src_tab, src_file)
                executor.submit(write_table_data_to_file, target_con, self.dst_db, self.dst_tab, dst_file)

        # with create_connection(source_dsn) as source_con:
        #     write_table_data_to_file(source_con, database, table, src_file)

        # with create_connection(target_dsn) as target_con:
        #     write_table_data_to_file(target_con, database, table, dst_file)

        if sha256sum(src_file) != sha256sum(dst_file):
            print(f"nokey table compare: {self.src_db}.{self.src_tab} different.")
        else:
            print(f"nokey table compare: {self.dst_db}.{self.src_tab} same.")


class MysqlTableCompareForward(MysqlTableCompare):
    def get_query_full_table_statement_params(self, keyval: dict = None):
        return get_query_full_table_statement_params(self.src_db, self.src_tab, self.table_keys, ["*"], self.limit_size, keyval)

    def extract_next_keyval(self, source_rows, target_rows):
        return extract_keyvals(source_rows[-1], self.table_keys)

    def process_diff_rows(self, source_con: MySQLConnection, target_con: MySQLConnection, source_rows: list[dict], target_rows: list[dict]):
        diff_rows = find_missing_in_b(source_rows, target_rows)

        if len(diff_rows) >= 1:
            self.logger.debug(f"find diff rows: {len(diff_rows)}.")
            self.logger.debug(f"verify after sleep {self.delay_check_wait}s")
            time.sleep(self.delay_check_wait)

        for diff_row in diff_rows:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                src_row = executor.submit(mysql_query_row, source_con, self.src_db, self.src_tab, self.table_keys, diff_row).result()
                dst_row = executor.submit(mysql_query_row, target_con, self.dst_db, self.dst_tab, self.table_keys, diff_row).result()

                if src_row is not None and src_row != dst_row:
                    self.different_rows_number += 1

                    self.logger.debug(f"different rows number {self.different_rows_number}")

                    if self.is_repair:
                        mysql_repair_row(self.logger, target_con, self.dst_db, self.dst_tab, src_row)


class MysqlTableCompareReverse(MysqlTableCompare):
    def get_query_full_table_statement_params(self, keyval: dict = None):
        select_cols = [f"`{col[0]}`" for col in self.table_keys]
        return get_query_full_table_statement_params(self.src_db, self.src_tab, self.table_keys, select_cols, self.limit_size, keyval)

    def extract_next_keyval(self, source_rows, target_rows):
        return extract_keyvals(target_rows[-1], self.table_keys)

    def process_diff_rows(self, source_con: MySQLConnection, target_con: MySQLConnection, source_rows: list[dict], target_rows: list[dict]):
        diff_rows = find_missing_in_b(target_rows, source_rows)

        if len(diff_rows) >= 1:
            self.logger.debug(f"find diff rows: {len(diff_rows)}.")
            self.logger.debug(f"verify after sleep {self.delay_check_wait}s")
            time.sleep(self.delay_check_wait)

        for diff_row in diff_rows:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                src_row = executor.submit(mysql_query_row, source_con, self.src_db, self.src_tab, self.table_keys, diff_row).result()
                dst_row = executor.submit(mysql_query_row, target_con, self.dst_db, self.dst_tab, self.table_keys, diff_row).result()

                if src_row is not None and src_row != dst_row:
                    self.different_rows_number += 1

                    if self.is_repair:
                        mysql_repair_row(self.logger, target_con, self.dst_db, self.dst_tab, src_row)


def running_compare(compare_workdir: str, compare_parallel: int, compare_mode: str, compare_exec: list[MysqlTableCompare]):
    summary_diff = {}
    summary_running = {}

    summary_running_file = f"{compare_workdir}/__progress.{compare_mode}.json"

    summary_diff_file = f"{compare_workdir}/__different.{compare_mode}.json"

    future_to_task = {}
    compare_complate = 0
    with concurrent.futures.ProcessPoolExecutor(max_workers=compare_parallel) as executor:
        for mtc in compare_exec:
            compare_name = mtc.compare_name

            summary_running[compare_name] = "progress"

            if os.path.exists(f"{compare_name}.log.done"):
                compare_complate += 1
                summary_running[compare_name] = "done"

                continue

            if os.path.exists(f"{compare_name}.err.log.done"):
                os.remove(f"{compare_name}.err.log.done")

            future_to_task[executor.submit(mtc.run)] = mtc

        with open(summary_running_file, "w", encoding="utf8") as f:
            json.dump(summary_running, f)

        for future in concurrent.futures.as_completed(future_to_task):
            mtc: MysqlTableCompare = future_to_task[future]
            compare_name = mtc.compare_name

            compare_complate += 1
            try:
                future.result()
                if mtc.different_rows_number >= 1:
                    summary_diff[compare_name] = mtc.different_rows_number
                    summary_running[compare_name] = "diff"
                else:
                    summary_running[compare_name] = "done"

                if os.path.exists(f"{compare_name}.log"):
                    os.rename(f"{compare_name}.log", f"{compare_name}.log.done")

                with open(summary_running_file, "w", encoding="utf8") as f:
                    json.dump(summary_running, f)
            except Exception as e:
                with open(f"{compare_name}.log", "a+") as f:
                    f.write(str(e) + "\n")

                if os.path.exists(f"{compare_name}.log"):
                    os.rename(f"{compare_name}.log", f"{compare_name}.err.log.done")

                summary_running[compare_name] = "error"

                with open(summary_running_file, "w", encoding="utf8") as f:
                    json.dump(summary_running, f)

            finally:
                print(f"{get_current_datetime()} compare complate: '{compare_name}' progress: {compare_complate}/{len(compare_exec)}")

    with open(summary_diff_file, "w", encoding="utf8") as f:
        json.dump(summary_diff, f)


def run(args=None):
    args = parse_args(args)

    arg_src_dsn: str = args.src_dsn
    arg_dst_dsn: str = args.dst_dsn
    arg_databases: list[str] = args.databases
    arg_tables: list[str] = args.tables
    arg_exclude_tables: list[str] = args.exclude_tables
    arg_parallel: int = args.parallel
    arg_delay_check: int = args.delay_check

    arg_batch_size: int = args.batch_size
    arg_work_dir: int = args.work_dir
    arg_work_dir_clear: int = args.work_dir_clear

    arg_mode_forward = args.forward
    arg_mode_forward_repair = args.forward_repair

    arg_mode_forward_nokey = args.forward_nokey

    arg_mode_reverse = args.reverse
    arg_mode_reverse_clear = args.reverse_clear

    src_dsn = mysql_parse_dsn(arg_src_dsn)
    dst_dsn = mysql_parse_dsn(arg_dst_dsn)

    print("src dsn", src_dsn)
    print("dst dsn", dst_dsn)

    process_tables: list[tuple[str, str, str, str]] = []

    if arg_databases:
        for arg_db in arg_databases:
            if ":" in arg_db:
                src_db, dst_db = arg_db.split(":")
            else:
                src_db = arg_db
                dst_db = arg_db
            for db, tab in mysql_query_tables(src_dsn, src_db):
                if f"{db}.{tab}" not in arg_exclude_tables:
                    process_tables.append((src_db, tab, dst_db, tab))

    if arg_tables:
        for arg_dbtab in arg_tables:
            if ":" in arg_dbtab:
                src_dbtab, dst_dbtab = arg_dbtab.split(":")
            else:
                dst_dbtab = arg_dbtab
                src_dbtab = arg_dbtab

            src_db, src_tab = src_dbtab.split(".")
            dst_db, dst_tab = dst_dbtab.split(".")

            if f"{src_db}.{src_tab}" not in arg_exclude_tables:
                process_tables.append((src_db, src_tab, dst_db, dst_tab))

    process_tables = list(set(process_tables))

    mtcs_reverse = []
    mtcs_forward = []
    mtcs_reverse_nokey = []

    with connect(**src_dsn) as source_con:
        for src_db, src_tab, dst_db, dst_tab in process_tables:
            src_table_keys = mysql_query_table_keys(source_con, src_db, src_tab)
            if len(src_table_keys) >= 1:
                # dst_table_keys = mysql_query_table_keys(target_con, dst_db, dst_tab)

                # if len(src_table_keys) == 0:
                #     compare_name = f"{arg_work_dir}/{src_db}.{src_tab}__{dst_db}.{dst_tab}.nokey"

                if arg_mode_reverse:
                    compare_name = f"{arg_work_dir}/{src_db}.{src_tab}__{dst_db}.{dst_tab}.reverse"
                    mtcs_reverse.append(
                        MysqlTableCompareReverse(
                            compare_name, src_dsn, dst_dsn, src_db, src_tab, dst_db, dst_tab, arg_batch_size, arg_mode_reverse_clear, arg_delay_check
                        )
                    )
                if arg_mode_forward:
                    compare_name = f"{arg_work_dir}/{src_db}.{src_tab}__{dst_db}.{dst_tab}.forward"
                    mtcs_forward.append(
                        MysqlTableCompareForward(
                            compare_name, src_dsn, dst_dsn, src_db, src_tab, dst_db, dst_tab, arg_batch_size, arg_mode_forward_repair, arg_delay_check
                        )
                    )
            else:
                if arg_mode_forward_nokey:
                    compare_name = f"{arg_work_dir}/{src_db}.{src_tab}__{dst_db}.{dst_tab}.nokey"
                    mtcs_reverse_nokey.append(MysqlTableCompareForwardNoKey(compare_name, src_dsn, dst_dsn, src_db, src_tab, dst_db, dst_tab))

    if arg_work_dir_clear and os.path.exists(arg_work_dir):
        shutil.rmtree(arg_work_dir)

    os.makedirs(arg_work_dir, exist_ok=True)

    running_compare(arg_work_dir, arg_parallel, "reverse", mtcs_reverse)
    running_compare(arg_work_dir, arg_parallel, "forward", mtcs_forward)
    # running_compare(arg_work_dir, arg_parallel, "forward-nokey", mtcs_reverse_nokey)
