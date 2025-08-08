import argparse
import concurrent.futures
import datetime
import json
import logging
import multiprocessing
import os
import shutil
import time
from dataclasses import dataclass
from urllib.parse import parse_qs

from _mysql_compare_table import MysqlCompareTable
from mysql.connector import MySQLConnection, connect, pooling


def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def init_logger(name: str | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(f"{name}.log")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    return logger


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


def get_elapsed_time(st: float, ndigits=None) -> int | float:
    return round(time.time() - st, ndigits)


def mysql_query(con: MySQLConnection, query_statement: str, query_params) -> list[dict]:
    with con.cursor(dictionary=True, buffered=True) as cur:
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


def mysql_query_tables(dsn: dict, db: str):
    with connect(**dsn) as con:
        cur = con.cursor()
        cur.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema = %s ORDER BY 1, 2", (db,))
        for db, tab in cur.fetchall():
            yield db, tab


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


def mysql_repair_row(logger: logging.Logger, con: MySQLConnection, database: str, table: str, diff_row: dict):
    columns = ", ".join([f"`{col}`" for col in diff_row.keys()])
    values_placeholder = ", ".join(["%s"] * len(diff_row))

    sql = f"REPLACE INTO `{database}`.`{table}` ({columns}) VALUES ({values_placeholder});"
    params = tuple(diff_row.values())

    logger.info(f"repair sql: {sql}, values: {params}")
    with con.cursor() as cur:
        cur.execute(sql, params)
        affected_rows = cur.rowcount
        logger.info(f"affected rows: {affected_rows}")
    con.commit()


@dataclass
class CompareArgs:
    repair: bool
    src_dsn: str
    dst_dsn: str
    databases: list[str]
    tables: list[str]
    exclude_tables: list[str]
    batch_size: int
    parallel: int
    delay_check: int
    work_dir: str
    work_dir_clear: bool
    repair: bool


def parse_args() -> CompareArgs:
    parser = argparse.ArgumentParser(description="Parse databases and tables")

    parser.add_argument("--src-dsn", type=str, required=True, help="List of tables")
    parser.add_argument("--dst-dsn", type=str, required=True, help="List of tables")

    parser.add_argument("--databases", nargs="+", default=[], help="List of databases")
    parser.add_argument("--tables", nargs="+", default=[], help="List of tables")
    parser.add_argument("--exclude-tables", nargs="+", default=[], help="List of tables")

    parser.add_argument("--batch-size", type=int, default=1000, help="List of tables")

    parser.add_argument("--parallel", type=int, default=1, help="Repair the tables")

    parser.add_argument("--delay-check", type=int, default=0, help="Repair the tables")
    parser.add_argument("--repair", action="store_true", help="Execute the forward script")

    parser.add_argument("--display-diff", action="store_true", help="Execute the forward script")

    parser.add_argument("--work-dir", type=str, default=datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"), help="Repair the tables")
    parser.add_argument("--work-dir-clear", action="store_true", help="Repair the tables")

    args = parser.parse_args()
    return CompareArgs(**vars(args))


@dataclass
class CompareRunningData:
    name: str
    # compare_name: str
    batch_size: int
    delay_check: bool
    is_repair: bool
    src_dsn: dict
    dst_dsn: dict
    src_db: str
    src_tab: str
    dst_db: str
    dst_tab: str
    table_keys: list
    table_rows_total: int
    temp_diff_rows: list[dict]
    error: str | None
    diff_rows_total: int
    proc_keyval: None


def running_compare_0(logger: logging.Logger, crd: CompareRunningData):
    with connect(**crd.src_dsn) as source_con, connect(**crd.dst_dsn) as target_con:
        source_table_struct: list[tuple[str, str]] = mysql_query_table_structure(source_con, crd.src_db, crd.src_tab)
        target_table_struct: list[tuple[str, str]] = mysql_query_table_structure(target_con, crd.dst_db, crd.dst_tab)

        logger.debug(f"source table structure: { source_table_struct}.")
        logger.debug(f"target table structure: { target_table_struct}.")

        if len(source_table_struct) == 0:
            logger.error("source table not exists.")
            raise Exception()

        if set(source_table_struct) != set(target_table_struct):
            logger.error("source and target table structure diff.")
            raise Exception()

        source_table_keys = mysql_query_table_keys(source_con, crd.src_db, crd.src_tab)
        target_table_keys = mysql_query_table_keys(target_con, crd.dst_db, crd.dst_tab)

        logger.debug(f"source table keys: {source_table_keys}.")

        logger.debug(f"target table keys: {target_table_keys}.")

        if len(source_table_keys) == 0:
            logger.error("The primary keys or unique keys not exists.")
            raise Exception()

        if set(source_table_keys) != set(target_table_keys):
            logger.error("The primary key or unique keys are not the same.")
            logger.debug(f"source table keys: {source_table_keys}.")
            logger.debug(f"target table keys: {target_table_keys}.")
            raise Exception()

        crd.table_keys = source_table_keys.copy()

        logger.debug(f"table keys: {crd.table_keys}.")

        crd.table_rows_total = max(1, mysql_query_table_rows_number(source_con, crd.src_db, crd.src_tab))
        logger.debug(f"source table rows number: {crd.table_rows_total}.")


def running_compare_1(logger: logging.Logger, crd: CompareRunningData):
    _batch_id = 1
    _process_rows = 0
    with connect(**crd.src_dsn) as source_con, connect(**crd.dst_dsn) as target_con:
        while True:
            query_statement_src, query_params_src = get_query_full_table_statement_params(crd.src_db, crd.src_tab, crd.table_keys, ["*"], crd.batch_size, crd.proc_keyval)
            query_statement_dst, query_params_dst = get_query_full_table_statement_params(crd.dst_db, crd.dst_tab, crd.table_keys, ["*"], crd.batch_size, crd.proc_keyval)

            logger.info(f"batch_id[{_batch_id}] source query statment: '{query_statement_src}', params '{query_params_src}'")
            logger.info(f"batch_id[{_batch_id}] target query statment: '{query_statement_dst}', params '{query_params_dst}'")

            source_rows = []
            target_rows = []

            _start1 = time.time()

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                source_rows = executor.submit(mysql_query, source_con, query_statement_src, query_params_src).result()
                target_rows = executor.submit(mysql_query, target_con, query_statement_dst, query_params_dst).result()

            logger.info(f"batch_id[{_batch_id}] source rows: {len(source_rows)}")
            logger.info(f"batch_id[{_batch_id}] target rows: {len(target_rows)}")

            if len(source_rows) == 0:
                break

            _process_rows += len(source_rows)

            _temp_diff_rows = find_missing_in_b(source_rows, target_rows)

            if len(_temp_diff_rows) >= 1:
                logger.info(f"batch_id[{_batch_id}] find diff rows: {len(_temp_diff_rows)}")

            crd.temp_diff_rows += _temp_diff_rows

            crd.proc_keyval = extract_keyvals(source_rows[-1], crd.table_keys)

            processed_progress = round(_process_rows / crd.table_rows_total * 100, 2)
            logger.info(f"batch_id[{_batch_id}] source rows: {len(source_rows)}, target rows: {len(target_rows)}.")
            logger.info(
                f"batch_id[{_batch_id}] processed rows number: {_process_rows}/{crd.table_rows_total}, progress: {processed_progress}%, elapsed time: {get_elapsed_time(_start1, 2)}s."
            )
            _batch_id += 1


def abc(source_con: MySQLConnection, target_con: MySQLConnection, src_db, dst_db, src_tab, dst_tab, table_keys, diff_row):
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        src_row = executor.submit(mysql_query_row, source_con, src_db, src_tab, table_keys, diff_row).result()
        dst_row = executor.submit(mysql_query_row, target_con, dst_db, dst_tab, table_keys, diff_row).result()
    source_con.close()
    target_con.close()
    return [src_row, dst_row]


def running_compare_2(logger: logging.Logger, crd: CompareRunningData):
    if len(crd.temp_diff_rows) == 0:
        return

    logger.debug(f"find diff rows: {len(crd.temp_diff_rows)}.")
    logger.debug(f"verify after sleep {crd.delay_check}s")
    time.sleep(crd.delay_check)

    src_pool = pooling.MySQLConnectionPool(pool_name="srcpool", pool_size=11, **crd.src_dsn)
    dst_pool = pooling.MySQLConnectionPool(pool_name="dstpool", pool_size=11, **crd.dst_dsn)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures: list[concurrent.futures.Future] = []

        for diff_row in crd.temp_diff_rows:
            future = executor.submit(
                abc, src_pool.get_connection(), dst_pool.get_connection(), crd.src_db, crd.dst_db, crd.src_tab, crd.dst_tab, crd.table_keys, diff_row
            )
            futures.append(future)

            if len(futures) >= 10:
                completed, not_completed = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)

                for f in completed:
                    src_row, dst_row = f.result()
                    if src_row is not None and src_row != dst_row:
                        crd.diff_rows_total += 1
                        logger.debug(f"diff src row: {src_row}")
                        logger.debug(f"diff dst row: {dst_row}")

                    futures = list(not_completed)

        for future in concurrent.futures.as_completed(futures):
            src_row, dst_row = future.result()
            if src_row is not None and src_row != dst_row:
                crd.diff_rows_total += 1
                logger.debug(f"diff src row: {src_row}")
                logger.debug(f"diff dst row: {dst_row}")
                # if crd.is_repair:
                #     mysql_repair_row(logger, target_con, crd.dst_db, crd.dst_tab, src_row)
    src_pool.close()
    dst_pool.close()


def running_compare(crd: CompareRunningData):
    logger = init_logger(crd.name)

    logger.info("running_compare")

    for _ in range(3):
        crd.error = None

        try:
            logger.info("running_compare_0")
            running_compare_0(logger, crd)
            logger.info("running_compare_0 end")

            logger.info("running_compare_1")
            running_compare_1(logger, crd)
            logger.info("running_compare_1 done")

            for diff_row in crd.temp_diff_rows:
                logger.debug(f"diff row: {diff_row}")

            # logger.info("running_compare_2")
            # running_compare_2(logger, crd)
            # logger.info("running_compare_2 done")

            break
        except Exception as e:
            crd.error = str(e)
            logger.error(crd.error)

    state = "done"
    if crd.error is not None:
        state = "error"
    elif len(crd.temp_diff_rows) >= 1:
        state = "diff"

    with open(f"{crd.name}.state", "w") as f:
        f.write(state)

    logger.info(f"table compare done, diff count: {len(crd.temp_diff_rows)}")

    return crd


def get_tables(cargs: CompareArgs) -> list[tuple[str, str, str, str]]:
    src_dsn = mysql_parse_dsn(cargs.src_dsn)

    process_tables: list[tuple[str, str, str, str]] = []

    if cargs.databases:
        for arg_db in cargs.databases:
            if ":" in arg_db:
                src_db, dst_db = arg_db.split(":")
            else:
                src_db = arg_db
                dst_db = arg_db
            for db, tab in mysql_query_tables(src_dsn, src_db):
                if f"{db}.{tab}" not in cargs.exclude_tables:
                    process_tables.append((src_db, tab, dst_db, tab))

    if cargs.tables:
        for arg_dbtab in cargs.tables:
            if ":" in arg_dbtab:
                src_dbtab, dst_dbtab = arg_dbtab.split(":")
            else:
                dst_dbtab = arg_dbtab
                src_dbtab = arg_dbtab

            src_db, src_tab = src_dbtab.split(".")
            dst_db, dst_tab = dst_dbtab.split(".")

            if f"{src_db}.{src_tab}" not in cargs.exclude_tables:
                process_tables.append((src_db, src_tab, dst_db, dst_tab))

    return list(set(process_tables))


def write_json(d, f: str):
    with open(f, "w", encoding="utf8") as f:
        json.dump(d, f)


def main():
    cargs = parse_args()
    print(cargs)

    if cargs.work_dir_clear and os.path.exists(cargs.work_dir):
        shutil.rmtree(cargs.work_dir)

    os.makedirs(cargs.work_dir, exist_ok=True)

    running_state_file = f"{cargs.work_dir}/__progress.forward.json"
    running_state = {}

    if os.path.exists(running_state_file):
        with open(running_state_file, "r", encoding="utf8") as f:
            running_state = json.load(f)

    success_count = 1

    compare_tables = get_tables(cargs)

    crds: dict[str, MysqlCompareTable] = {}
    processes_running: dict[str, multiprocessing.Process] = {}

    for src_db, src_tab, dst_db, dst_tab in compare_tables:
        compare_name = f"{cargs.work_dir}/{src_db}.{src_tab}_@_{dst_db}.{dst_tab}.forward"
        if compare_name in running_state and (running_state[compare_name] == "done" or running_state[compare_name] == "diff" or running_state[compare_name] == "error"):
            success_count += 1
            continue
        crd = MysqlCompareTable(
            compare_name,
            cargs.batch_size,
            cargs.repair,
            mysql_parse_dsn(cargs.src_dsn),
            mysql_parse_dsn(cargs.dst_dsn),
            src_db,
            src_tab,
            dst_db,
            dst_tab,
        )

        crds[compare_name] = crd
        running_state[compare_name] = "progress"

    write_json(running_state, running_state_file)

    while True:
        if len(crds) == 0 and len(processes_running) == 0:
            break

        for compare_name, proc_running in list(processes_running.items()):
            if not proc_running.is_alive():
                proc_running.join()

                if os.path.exists(f"{compare_name}.state"):
                    with open(f"{compare_name}.state", "r", encoding="utf8") as f:
                        running_state[compare_name] = f.read()

                write_json(running_state, running_state_file)
                print(f"{get_current_time()} -- {compare_name} -- complate, progress: {success_count}/{len(compare_tables)}")

                del processes_running[compare_name]
                success_count += 1
                if os.path.exists(f"{compare_name}.state"):
                    os.remove(f"{compare_name}.state")
            else:
                print(f"{get_current_time()} -- {compare_name} -- running, progress: {success_count}/{len(compare_tables)}")

        while len(crds) >= 1 and len(processes_running) < cargs.parallel:
            compare_name, crd = crds.popitem()
            print(f"{get_current_time()} -- {compare_name} -- started, progress: {success_count}/{len(compare_tables)}")
            proc = multiprocessing.Process(target=crd.start)
            processes_running[compare_name] = proc
            proc.start()

        time.sleep(10)


if __name__ == "__main__":
    main()
