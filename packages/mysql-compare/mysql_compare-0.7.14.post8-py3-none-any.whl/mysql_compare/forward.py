import argparse
import datetime
import json
import multiprocessing
import os
import shutil
import time
from dataclasses import dataclass
from urllib.parse import parse_qs

from mysql.connector import connect

from mysql_compare._mysql_compare_table import MysqlCompareTable


def get_current_time():
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


def mysql_query_tables(dsn: dict, db: str):
    with connect(**dsn) as con:
        cur = con.cursor()
        cur.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema = %s ORDER BY 1, 2", (db,))
        for db, tab in cur.fetchall():
            yield db, tab


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
    work_dir: str
    work_dir_clear: bool
    repair: int
    display_diff: bool
    batch_timeout: int
    exact: bool


def parse_args() -> CompareArgs:
    parser = argparse.ArgumentParser(description="Parse databases and tables")

    parser.add_argument("--src-dsn", type=str, required=True, help="List of tables")
    parser.add_argument("--dst-dsn", type=str, required=True, help="List of tables")

    parser.add_argument("--databases", nargs="+", default=[], help="List of databases")
    parser.add_argument("--tables", nargs="+", default=[], help="List of tables")
    parser.add_argument("--exclude-tables", nargs="+", default=[], help="List of tables")

    parser.add_argument("--batch-size", type=int, default=1000, help="List of tables")
    parser.add_argument("--batch-timeout", type=int, default=120, help="List of tables")

    parser.add_argument("--parallel", type=int, default=1, help="Repair the tables")

    parser.add_argument("--repair", type=int, default=0, help="Execute the forward script")
    parser.add_argument("--display-diff", action="store_true", help="Execute the forward script")
    parser.add_argument("--exact", action="store_true", help="Execute the forward script")

    parser.add_argument("--work-dir", type=str, default=datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"), help="Repair the tables")
    parser.add_argument("--work-dir-clear", action="store_true", help="Repair the tables")

    args = parser.parse_args()
    return CompareArgs(**vars(args))


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
    if cargs.repair >= 1:
        cargs.exact = True

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
            cargs.batch_timeout,
            cargs.repair,
            cargs.display_diff,
            cargs.exact,
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
