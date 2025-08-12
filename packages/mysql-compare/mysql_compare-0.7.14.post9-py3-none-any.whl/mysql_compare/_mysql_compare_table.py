import concurrent.futures
import logging
import time

from mysql.connector import MySQLConnection, connect

import mysql_compare.patch


def init_logger(name: str | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(f"{name}.log")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    return logger


def get_elapsed_time(st: float, ndigits=None) -> int | float:
    return round(time.time() - st, ndigits)


def mysql_query(con: MySQLConnection, query_statement: str, query_params) -> list[dict]:
    with con.cursor(dictionary=True) as cur:
        cur.execute(query_statement, tuple(query_params))
        return cur.fetchall()


def mysql_query_table_structure(con: MySQLConnection, database: str, table: str) -> list[tuple[str, str]]:
    with con.cursor() as cur:
        cur.execute(
            "SELECT column_name, CAST(data_type as char(255)) FROM information_schema.columns WHERE table_schema = %s AND table_name = %s ORDER BY ordinal_position",
            (database, table),
        )
        return cur.fetchall()


def mysql_query_table_rows_number(con: MySQLConnection, database: str, table: str) -> int:
    with con.cursor() as cur:
        cur.execute("SELECT table_rows FROM information_schema.tables WHERE table_schema = %s AND table_name = %s", (database, table))
        (rows,) = cur.fetchone()
        return rows


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


def extract_keyvals(row: dict, keys: list[tuple[str, str]]):
    _keys = [item[0] for item in keys]
    new_dict = {}
    for key in row:
        if key in _keys:
            new_dict[key] = row[key]

    return new_dict


def hash_dict(d: dict):
    # return frozenset(d.items())
    return frozenset((k, frozenset(v) if isinstance(v, set) else v) for k, v in d.items())


def find_missing_in_b(a, b):
    b_hashes = {hash_dict(d) for d in b}
    missing_in_b = [d for d in a if hash_dict(d) not in b_hashes]
    return missing_in_b


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


def mysql_repair_row(logger: logging.Logger, con: MySQLConnection, database: str, table: str, diff_row: dict):
    columns = ", ".join([f"`{col}`" for col in diff_row.keys()])
    values_placeholder = ", ".join(["%s"] * len(diff_row))

    sql = f"REPLACE INTO `{database}`.`{table}` ({columns}) VALUES ({values_placeholder});"
    params = tuple(diff_row.values())

    logger.debug(f"repair: sql: {sql}, values: {params}")
    with con.cursor() as cur:
        cur.execute(sql, params)
        affected_rows = cur.rowcount
        logger.debug(f"repair: affected rows: {affected_rows}")
    con.commit()


class MysqlCompareTable:
    table_keys: list = []
    table_rows_total: int = 0
    error: str | None = None
    diff_rows_total: int = 0
    proc_keyval: None = None
    state: str = "done"
    diff_rows_cnt: int = 0
    repair_rows_cnt: int = 0

    def __init__(
        self,
        compare_name: str,
        batch_size: int,
        batch_timeout: int,
        is_repair: int,
        dis_diff: bool,
        exact: bool,
        src_dsn: dict,
        dst_dsn: dict,
        src_db: str,
        src_tab: str,
        dst_db: str,
        dst_tab: str,
    ) -> None:
        self.compare_name = compare_name
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.is_repair = is_repair
        self.dis_diff = dis_diff
        self.exact = exact
        self.src_dsn = src_dsn
        self.dst_dsn = dst_dsn
        self.src_db = src_db
        self.src_tab = src_tab
        self.dst_db = dst_db
        self.dst_tab = dst_tab

    def running_compare(self):
        with connect(**self.src_dsn) as source_con, connect(**self.dst_dsn) as target_con:
            source_table_struct: list[tuple[str, str]] = mysql_query_table_structure(source_con, self.src_db, self.src_tab)
            target_table_struct: list[tuple[str, str]] = mysql_query_table_structure(target_con, self.dst_db, self.dst_tab)

            self.logger.debug(f"source table structure: {source_table_struct}.")
            self.logger.debug(f"target table structure: {target_table_struct}.")

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

            self.table_rows_total = max(1, mysql_query_table_rows_number(source_con, self.src_db, self.src_tab))
            self.logger.debug(f"source table rows number: {self.table_rows_total}.")

            _batch_id = 1
            _process_rows = 0

            while True:
                query_statement_src, query_params_src = get_query_full_table_statement_params(self.src_db, self.src_tab, self.table_keys, ["*"], self.batch_size, self.proc_keyval)
                query_statement_dst, query_params_dst = get_query_full_table_statement_params(self.dst_db, self.dst_tab, self.table_keys, ["*"], self.batch_size, self.proc_keyval)

                self.logger.debug(f"batch_id[{_batch_id}] source query statment: '{query_statement_src}', params '{query_params_src}'")
                self.logger.debug(f"batch_id[{_batch_id}] target query statment: '{query_statement_dst}', params '{query_params_dst}'")

                source_rows = []
                target_rows = []

                _start1 = time.time()

                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    source_rows = executor.submit(mysql_query, source_con, query_statement_src, query_params_src).result(timeout=self.batch_timeout)
                    target_rows = executor.submit(mysql_query, target_con, query_statement_dst, query_params_dst).result(timeout=self.batch_timeout)

                self.logger.debug(f"batch_id[{_batch_id}] source rows: {len(source_rows)}")
                self.logger.debug(f"batch_id[{_batch_id}] target rows: {len(target_rows)}")

                if len(source_rows) == 0:
                    break

                _process_rows += len(source_rows)

                _diff_rows = find_missing_in_b(source_rows, target_rows)

                if len(_diff_rows) >= 1:
                    self.logger.debug(f"batch_id[{_batch_id}] find diff rows: {len(_diff_rows)}")
                    if not self.exact:
                        self.diff_rows_cnt += len(_diff_rows)
                        for diff_row in _diff_rows:
                            self.logger.debug(f"diff row: {diff_row}")

                self.proc_keyval = extract_keyvals(source_rows[-1], self.table_keys)

                processed_progress = round(_process_rows / self.table_rows_total * 100, 2)
                self.logger.debug(f"batch_id[{_batch_id}] source rows: {len(source_rows)}, target rows: {len(target_rows)}.")
                self.logger.debug(f"batch_id[{_batch_id}] processed rows number: {_process_rows}/{self.table_rows_total}, progress: {processed_progress}%, elapsed time: {get_elapsed_time(_start1, 2)}s.")
                _batch_id += 1

                if self.exact and len(_diff_rows) >= 1:
                    # self.logger.debug(f"batch_id[{_batch_id}] repair sleep: {self.is_repair}s, repair rows: {len(_diff_rows)}")
                    self.logger.debug(f"batch_id[{_batch_id}] exact sleep: {self.is_repair}s")
                    time.sleep(self.is_repair)
                    time.sleep(10)
                    for diff_row in _diff_rows:
                        self.logger.debug(f"batch_id[{_batch_id}] exact row: src[{diff_row}]")
                        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                            src_row = executor.submit(mysql_query_row, source_con, self.src_db, self.src_tab, self.table_keys, diff_row).result()
                            dst_row = executor.submit(mysql_query_row, target_con, self.dst_db, self.dst_tab, self.table_keys, diff_row).result()
                            patch_diff_row = mysql_compare.patch.check_litb_diff_row(self.logger, self.src_db, self.src_tab, src_row, dst_row)
                            if not patch_diff_row:
                                self.diff_rows_cnt += 1
                                self.logger.debug(f"batch_id[{_batch_id}] diff row: src[{diff_row}]")
                                self.logger.debug(f"batch_id[{_batch_id}] diff row: dst[{dst_row}]")
                                if self.is_repair >= 1:
                                    mysql_repair_row(self.logger, target_con, self.dst_db, self.dst_tab, src_row)
                                    self.repair_rows_cnt += 1

                self.logger.debug(f"batch_id[{_batch_id}] find diff rows: {len(_diff_rows)} repair diff rows: {self.repair_rows_cnt}")

            if self.diff_rows_cnt >= 1:
                self.state = "diff"

    def start(self):
        self.logger = init_logger(self.compare_name)

        self.logger.debug("running_compare")

        for _ in range(3):
            self.error = None

            try:
                self.running_compare()
                break
            except Exception as e:
                self.error = str(e)
                self.logger.error(self.error)

        if self.error is not None:
            self.state = "error"

        with open(f"{self.compare_name}.state", "w") as f:
            f.write(self.state)

        self.logger.debug(f"table compare done, diff count: {self.diff_rows_cnt}, repair count: {self.repair_rows_cnt}")
