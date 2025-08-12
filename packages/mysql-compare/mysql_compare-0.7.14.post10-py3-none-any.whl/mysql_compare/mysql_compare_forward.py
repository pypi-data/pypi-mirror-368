import argparse
import concurrent.futures
import datetime
import json
import logging
import os
import shutil
import time

from mysql.connector import MySQLConnection, connect


def init_logger(name: str | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    handler = logging.FileHandler(f"{name}.log")
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


def hash_dict(d):
    # return frozenset(d.items())
    return frozenset((k, frozenset(v) if isinstance(v, set) else v) for k, v in d.items())


def find_missing_in_b(a, b):
    b_hashes = {hash_dict(d) for d in b}

    missing_in_b = [d for d in a if hash_dict(d) not in b_hashes]

    return missing_in_b


def query_tables(dsn: dict, db: str):
    with connect(**dsn) as con:
        cur = con.cursor()
        cur.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema = %s ORDER BY 1, 2", (db,))
        for db, tab in cur.fetchall():
            yield db, tab


def get_current_datetime():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def parse_dsn(dsn: str) -> dict:
    _userpass, _hostport = dsn.split("@")
    _user, _pass = _userpass.split(":")
    _host, _port = _hostport.split(":")
    return {"host": _host, "port": _port, "user": _user, "password": _pass, "time_zone": "+00:00"}


def get_table_rows_by_keys(con: MySQLConnection, database: str, table: str, table_keys, diff_rows: list[dict]) -> list[dict]:
    cols = [key[0] for key in table_keys]
    placeholders = ", ".join(["%s"] * len(cols))

    in_clause = ", ".join([f"({placeholders})" for _ in diff_rows])

    params = [val for row in diff_rows for val in (row[col] for col in cols)]

    formatted_cols = [f"`{c}`" for c in cols]
    _stmt = f"SELECT * FROM {database}.{table} WHERE ({', '.join(formatted_cols)}) IN ({in_clause}) ORDER BY {', '.join(formatted_cols)}"

    with con.cursor(dictionary=True, buffered=True) as cur:
        cur.execute(_stmt, tuple(params))
        return cur.fetchall()


def get_table_rows_number(con: MySQLConnection, database: str, table: str) -> int:
    with con.cursor() as cur:
        cur.execute("SELECT table_rows FROM information_schema.tables WHERE table_schema = %s AND table_name = %s", (database, table))
        (rows,) = cur.fetchone()
        return rows


def get_table_structure(con: MySQLConnection, database: str, table: str) -> list[tuple[str, str]]:
    with con.cursor() as cur:
        cur.execute(
            "SELECT column_name, CAST(data_type as char(255)) FROM information_schema.columns WHERE table_schema = %s AND table_name = %s ORDER BY ordinal_position",
            (database, table),
        )
        return cur.fetchall()


def get_table_keys(con: MySQLConnection, database: str, table: str):
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

    return pkeys, ukeys


def get_elapsed_time(st: float, ndigits=None) -> int | float:
    return round(time.time() - st, ndigits)


def extract_keyvals(row: dict, keys: list[tuple[str, str]]):
    _keys = [item[0] for item in keys]
    new_dict = {}
    for key in row:
        if key in _keys:
            new_dict[key] = row[key]

    return new_dict


def query_rows(con: MySQLConnection, query_statement: str, query_params) -> list[dict]:
    with con.cursor(dictionary=True, buffered=True) as cur:
        cur.execute(query_statement, tuple(query_params))
        return cur.fetchall()


def repair_row(logger: logging.Logger, con: MySQLConnection, database: str, table: str, row: dict):
    columns = ", ".join([f"`{col}`" for col in row.keys()])
    values_placeholder = ", ".join(["%s"] * len(row))
    values = tuple(row.values())
    sql = f"REPLACE INTO `{database}`.`{table}` ({columns}) VALUES ({values_placeholder});"
    logger.info(f"repair sql: {sql}, values: {values}")
    with con.cursor() as cur:
        cur.execute(sql, values)
        affected_rows = cur.rowcount
        logger.info(f"row repair rows: {affected_rows}")
    con.commit()


def get_row_by_key(con: MySQLConnection, database, table, table_keys, diff_row) -> list[dict]:
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
        row = cur.fetchone()
        if row is None:
            return []
        return [row]


def get_query_full_table_statement_params(
    database: str,
    table: str,
    table_keys,
    limit_size: int,
    ckpt_row: dict = None,
):
    _keyval = ckpt_row
    # select * from where 1 = 1 and ((a > xxx) or (a = xxx and b > yyy) or (a = xxx and b = yyy and c > zzz)) order by a,b,c limit checksize
    _key_colns = ", ".join([f"`{col[0]}`" for col in table_keys])

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
    where_clause = "WHERE " + "(" + ") or (".join(where_conditions) + ")"

    statement_with_condition = f"SELECT * FROM `{database}`.`{table}` {where_clause} ORDER BY {_key_colns} LIMIT {limit_size}"
    statement_without_condition = f"SELECT * FROM `{database}`.`{table}` ORDER BY {_key_colns} LIMIT {limit_size}"

    _params: list = []
    if _keyval:
        for end_idx in range(len(table_keys)):
            for i, (column_name, _) in enumerate(table_keys[: end_idx + 1]):
                _params.append(_keyval[column_name])

    statement = statement_with_condition if _params else statement_without_condition

    return statement, _params


class MysqlTableCompareForward:
    def __init__(
        self,
        compare_name: str,
        src_dsn: dict,
        dst_dsn: dict,
        src_database: str,
        src_table: str,
        dst_database: str,
        dst_table: str,
        limit_size: int = 2000,
        repair: bool = False,
        arg_delay_check: int = 0,
    ) -> None:
        self.compare_name = compare_name

        self.source_dsn = src_dsn
        self.target_dsn = dst_dsn

        self.limit_size = limit_size

        self.src_db = src_database
        self.src_tab = src_table
        self.dst_db = dst_database
        self.dst_tab = dst_table

        self.table_keys = []
        self.source_table_ukeys = []

        self.is_repair = repair
        self.delay_check_wait = arg_delay_check

        self.processed_rows_number = 0
        self.different_rows_number = 0

    def run(self):
        self.logger = init_logger(self.compare_name)

        with connect(**self.source_dsn) as source_con, connect(**self.target_dsn) as target_con:
            source_table_struct: list[tuple[str, str]] = get_table_structure(source_con, self.src_db, self.src_tab)
            target_table_struct: list[tuple[str, str]] = get_table_structure(target_con, self.dst_db, self.dst_tab)

            self.logger.debug(f"source table structure: { source_table_struct}.")
            self.logger.debug(f"target table structure: { target_table_struct}.")

            if len(source_table_struct) == 0:
                self.logger.error("source table not exists.")
                raise Exception()

            if set(source_table_struct) != set(target_table_struct):
                self.logger.error("source and target table structure diff.")
                raise Exception()

            source_table_pkeys, source_table_ukeys = get_table_keys(source_con, self.src_db, self.src_tab)
            target_table_pkeys, target_table_ukeys = get_table_keys(target_con, self.dst_db, self.dst_tab)

            self.logger.debug(f"source table pkeys: {source_table_pkeys}.")
            self.logger.debug(f"source table ukeys: {source_table_ukeys}.")

            self.logger.debug(f"target table pkeys: {target_table_pkeys}.")
            self.logger.debug(f"target table ukeys: {target_table_ukeys}.")

            source_table_keys = source_table_ukeys if len(source_table_pkeys) == 0 else source_table_pkeys
            target_table_keys = target_table_ukeys if len(target_table_pkeys) == 0 else target_table_pkeys

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

            self.source_table_rows_number = max(1, get_table_rows_number(source_con, self.src_db, self.src_tab))
            self.logger.debug(f"source table rows number: {self.source_table_rows_number}.")

        _keyval = None
        batch_id = 1

        with connect(**self.source_dsn) as source_con, connect(**self.target_dsn) as target_con:
            while True:
                self.logger.debug(f"batch_id[{batch_id}] start compare keys: {_keyval}")

                query_statement_src, query_params_src = get_query_full_table_statement_params(self.src_db, self.src_tab, self.table_keys, self.limit_size, _keyval)
                query_statement_dst, query_params_dst = get_query_full_table_statement_params(self.dst_db, self.dst_tab, self.table_keys, self.limit_size, _keyval)

                self.logger.debug(f"batch_id[{batch_id}] source query statment: '{query_statement_src}', params '{query_params_src}'")
                self.logger.debug(f"batch_id[{batch_id}] target query statment: '{query_statement_dst}', params '{query_params_dst}'")

                source_rows = []
                target_rows = []
                diff_rows = []

                _start1 = time.time()
                _sleep_time = 0

                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    future_source = executor.submit(query_rows, source_con, query_statement_src, query_params_src)
                    future_target = executor.submit(query_rows, target_con, query_statement_dst, query_params_dst)

                    source_rows = future_source.result()
                    target_rows = future_target.result()

                if len(source_rows) == 0:
                    break

                self.processed_rows_number += len(source_rows)
                diff_rows = find_missing_in_b(source_rows, target_rows)

                if len(diff_rows) >= 1:
                    self.logger.debug(f"find diff rows: {len(diff_rows)}.")
                    self.logger.debug(f"verify after sleep {self.delay_check_wait}s")
                    time.sleep(self.delay_check_wait)
                    _sleep_time = self.delay_check_wait

                for diff_row in diff_rows:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                        future_source_twice = executor.submit(get_row_by_key, source_con, self.src_db, self.src_tab, self.table_keys, diff_row)
                        future_target_twice = executor.submit(get_row_by_key, target_con, self.dst_db, self.dst_tab, self.table_keys, diff_row)

                    new_row_src = future_source_twice.result()
                    new_row_dst = future_target_twice.result()

                    diff_rows_twice = find_missing_in_b(new_row_src, new_row_dst)
                    if len(diff_rows_twice) == 1:
                        self.logger.debug(f"batch_id[{batch_id}] diff row source: {new_row_src}")
                        self.logger.debug(f"batch_id[{batch_id}] diff row target: {new_row_dst}")
                        self.different_rows_number += 1
                        if self.is_repair:
                            repair_row(self.logger, target_con, self.dst_db, self.dst_tab, diff_rows_twice[0])

                _keyval = extract_keyvals(source_rows[-1], self.table_keys)

                processed_progress = round(self.processed_rows_number / self.source_table_rows_number * 100, 2)
                self.logger.debug(f"batch_id[{batch_id}] source rows: {len(source_rows)}, target rows: {len(target_rows)}.")
                self.logger.debug(
                    f"batch_id[{batch_id}] processed rows number: {self.processed_rows_number}/{self.source_table_rows_number}, progress: {processed_progress}%, elapsed time: {get_elapsed_time(_start1, 2) - _sleep_time}s."
                )
                batch_id += 1

        self.logger.debug(f"compare completed, processed rows: {self.processed_rows_number}, different: {self.different_rows_number}.")

        return self.different_rows_number


def parse_args(external_args=None):
    parser = argparse.ArgumentParser(description="Parse databases and tables")

    parser.add_argument("--src-dsn", type=str, required=True, help="List of tables")
    parser.add_argument("--dst-dsn", type=str, required=True, help="List of tables")

    parser.add_argument("--databases", nargs="+", default=[], help="List of databases")
    parser.add_argument("--tables", nargs="+", default=[], help="List of tables")
    parser.add_argument("--exclude-tables", default=[], nargs="+", help="List of tables")

    parser.add_argument("--batch-size", type=int, default=1000, help="List of tables")

    parser.add_argument("--parallel", type=int, default=1, help="Repair the tables")

    parser.add_argument("--repair", action="store_true", default=False, help="Repair the tables")
    parser.add_argument("--delay-check", type=int, default=0, help="Repair the tables")

    parser.add_argument("--work-dir", type=str, default=datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S"), help="Repair the tables")
    parser.add_argument("--work-dir-clear", action="store_true", help="Repair the tables")

    args = parser.parse_args(external_args)
    print(f"args: {args}")
    return args


def run(args=None):
    args = parse_args(args)

    arg_src_dsn: str = args.src_dsn
    arg_dst_dsn: str = args.dst_dsn
    arg_databases: list[str] = args.databases
    arg_tables: list[str] = args.tables
    arg_exclude_tables: list[str] = args.exclude_tables
    arg_parallel: int = args.parallel
    arg_repair: bool = args.repair
    arg_delay_check: int = args.delay_check

    arg_batch_size: int = args.batch_size
    arg_work_dir: int = args.work_dir
    arg_work_dir_clear: int = args.work_dir_clear

    src_dsn = parse_dsn(arg_src_dsn)
    dst_dsn = parse_dsn(arg_dst_dsn)

    process_tables: list[tuple[str, str, str, str]] = []

    if arg_databases:
        for arg_db in arg_databases:
            if ":" in arg_db:
                src_db, dst_db = arg_db.split(":")
            else:
                src_db = arg_db
                dst_db = arg_db
            for db, tab in query_tables(src_dsn, src_db):
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

    future_to_task = {}
    compare_success = 0

    if arg_work_dir_clear and os.path.exists(arg_work_dir):
        shutil.rmtree(arg_work_dir)

    os.makedirs(arg_work_dir, exist_ok=True)

    diff_summary = {}
    progress_sumary = {}

    with concurrent.futures.ProcessPoolExecutor(max_workers=arg_parallel) as executor:
        for src_db, src_tab, dst_db, dst_tab in process_tables:
            compare_name = f"{arg_work_dir}/{src_db}.{src_tab}@{dst_db}.{dst_tab}.forward"
            progress_sumary[compare_name] = "progress"

            if os.path.exists(f"{compare_name}.log.done"):
                compare_success += 1
                progress_sumary[compare_name] = "done"
                continue

            if os.path.exists(f"{compare_name}.err.log.done"):
                os.remove(f"{compare_name}.err.log.done")

            mtc = MysqlTableCompareForward(compare_name, src_dsn, dst_dsn, src_db, src_tab, dst_db, dst_tab, arg_batch_size, arg_repair, arg_delay_check)
            future_to_task[executor.submit(mtc.run)] = f"{compare_name}"

        with open(f"{arg_work_dir}/progress.json", "w", encoding="utf8") as f:
            json.dump(progress_sumary, f)

        for future in concurrent.futures.as_completed(future_to_task):
            compare_name: str = future_to_task[future]
            compare_success += 1
            try:
                diff_cnt = future.result()
                if diff_cnt >= 1:
                    compare_dbtab = compare_name.split("/")[1].split("@")[0]
                    diff_summary[compare_dbtab] = diff_cnt
                if os.path.exists(f"{compare_name}.log"):
                    os.rename(f"{compare_name}.log", f"{compare_name}.log.done")

                progress_sumary[compare_name] = "done"
                with open(f"{arg_work_dir}/progress.json", "w", encoding="utf8") as f:
                    json.dump(progress_sumary, f)
            except Exception as e:
                with open(f"{compare_name}.log", "a+") as f:
                    f.write(str(e))
                # print(f"{get_current_datetime()} {compare_name} generated an exception: {e}")
                if os.path.exists(f"{compare_name}.log"):
                    os.rename(f"{compare_name}.log", f"{compare_name}.err.log.done")

                progress_sumary[compare_name] = "error"
                with open(f"{arg_work_dir}/progress.json", "w", encoding="utf8") as f:
                    json.dump(progress_sumary, f)
            finally:
                print(f"{get_current_datetime()} compare complate: '{compare_name}' progress: {compare_success}/{len(process_tables)}")

    with open(f"{arg_work_dir}/summary.json", "w", encoding="utf8") as f:
        json.dump(diff_summary, f)

    with open(f"{arg_work_dir}/progress.json", "w", encoding="utf8") as f:
        json.dump(progress_sumary, f)
    # source_dsn = {"host": "192.168.161.93", "port": 33026, "user": "root", "password": "root_password", "time_zone": "+00:00"}
    # target_dsn = {"host": "192.168.161.93", "port": 33027, "user": "root", "password": "root_password", "time_zone": "+00:00"}
    # MysqlTableCompare(source_dsn, target_dsn, "test1", "tab", "test1", "tab", 50000, True).run()


# python3.12 mysql_compare.py --src-dsn root:root_password@192.168.161.93:33026 --dst-dsn root:root_password@192.168.161.93:33026 --parallel 10 --tables test1.tab


# python3.12 mysql_compare.py --src-dsn ghost:54448hotINBOX@10.50.10.83:3310 --dst-dsn ghost:54448hotINBOX@10.50.10.83:3317 --parallel 20 --compare-batch 50000 --databases merchant_center_vela_v1 --exclude-tables merchant_center_vela_v1.amazon_product_info merchant_center_vela_v1.attributes_extends_to_group merchant_center_vela_v1.attributes_values_groups merchant_center_vela_v1.attributes_values_to_group merchant_center_vela_v1.auto_naming_test merchant_center_vela_v1.bi_17tk_deliver_interval merchant_center_vela_v1.bi_coupon_exclusion_products merchant_center_vela_v1.bi_discount_product merchant_center_vela_v1.bi_sku_purchase_price merchant_center_vela_v1.categories_to_templates merchant_center_vela_v1.location_to_phonenumber_regex merchant_center_vela_v1.logistics_attributes_rules merchant_center_vela_v1.log_mc_categories_autoprice merchant_center_vela_v1.log_mc_categories_autoprice_gmrate_interval merchant_center_vela_v1.log_mc_categories_price_stops merchant_center_vela_v1.log_modify_price_approve_info merchant_center_vela_v1.log_operate merchant_center_vela_v1.mc_access_log merchant_center_vela_v1.mc_actions merchant_center_vela_v1.mc_admins_configuration merchant_center_vela_v1.mc_admins_groups merchant_center_vela_v1.mc_admins_groups_to_actions merchant_center_vela_v1.mc_admins_menu_panel_view merchant_center_vela_v1.mc_admins_to_categories merchant_center_vela_v1.mc_admins_to_groups merchant_center_vela_v1.mc_ad_content_his merchant_center_vela_v1.mc_ad_date_title merchant_center_vela_v1.mc_ad_documents_del merchant_center_vela_v1.mc_ad_documents_desc_del merchant_center_vela_v1.mc_ad_font_style merchant_center_vela_v1.mc_ad_order_to_categories_del merchant_center_vela_v1.mc_ad_show_type merchant_center_vela_v1.mc_ad_templates_del merchant_center_vela_v1.mc_ad_templates_to_documents_del merchant_center_vela_v1.mc_ad_templates_to_documents_style_del merchant_center_vela_v1.mc_ad_unit_to_categories_del merchant_center_vela_v1.mc_apply_detail merchant_center_vela_v1.mc_apply_info merchant_center_vela_v1.mc_attributes_click_rate merchant_center_vela_v1.mc_attributes_cms_lexicon merchant_center_vela_v1.mc_attributes_values_to_attributes_20210807_backup merchant_center_vela_v1.mc_attributes_values_to_attributes_20210807_del merchant_center_vela_v1.mc_attributes_values_to_attributes_20210807_dump_d merchant_center_vela_v1.mc_attr_merge_record merchant_center_vela_v1.mc_banner_auto merchant_center_vela_v1.mc_banner_auto_content merchant_center_vela_v1.mc_banner_auto_content_desc merchant_center_vela_v1.mc_banner_copies_format merchant_center_vela_v1.mc_banner_template merchant_center_vela_v1.mc_categories_attributes_gather merchant_center_vela_v1.mc_categories_autoprice_gmrate_interval merchant_center_vela_v1.mc_categories_auto_price_log merchant_center_vela_v1.mc_categories_bi_report_config merchant_center_vela_v1.mc_categories_express_rates merchant_center_vela_v1.mc_categories_fs_bg_color merchant_center_vela_v1.mc_categories_lexicon merchant_center_vela_v1.mc_categories_operation_log merchant_center_vela_v1.mc_categories_price_policy merchant_center_vela_v1.mc_categories_price_rate_log merchant_center_vela_v1.mc_categories_price_stops merchant_center_vela_v1.mc_categories_procurement_price merchant_center_vela_v1.mc_categories_products_num merchant_center_vela_v1.mc_categories_sales_sum_ninety_days merchant_center_vela_v1.mc_categories_to_basecategories_extends merchant_center_vela_v1.mc_categories_translate merchant_center_vela_v1.mc_category_nav_group_old merchant_center_vela_v1.mc_clearance_product merchant_center_vela_v1.mc_combination_products_history merchant_center_vela_v1.mc_country_order_num merchant_center_vela_v1.mc_coupons_bak merchant_center_vela_v1.mc_coupon_activity merchant_center_vela_v1.mc_coupon_activty_restrict merchant_center_vela_v1.mc_coupon_apply_department merchant_center_vela_v1.mc_coupon_config merchant_center_vela_v1.mc_coupon_config_type merchant_center_vela_v1.mc_coupon_form merchant_center_vela_v1.mc_coupon_form_to_coupon merchant_center_vela_v1.mc_coupon_restrict_bak merchant_center_vela_v1.mc_coupon_value_type merchant_center_vela_v1.mc_craw_products_tag merchant_center_vela_v1.mc_ctr_avg merchant_center_vela_v1.mc_ctr_avg_history merchant_center_vela_v1.mc_ctr_daily merchant_center_vela_v1.mc_currencies_his merchant_center_vela_v1.mc_dailydeals_products_gather merchant_center_vela_v1.mc_delivery_form merchant_center_vela_v1.mc_delivery_form_to_delivery merchant_center_vela_v1.mc_dfp_items_desc_extend merchant_center_vela_v1.mc_dfp_items_desc_extend_language merchant_center_vela_v1.mc_dfp_items_desc_extend_language_img merchant_center_vela_v1.mc_discount merchant_center_vela_v1.mc_discount_desc merchant_center_vela_v1.mc_discount_rule_auto_log merchant_center_vela_v1.mc_discount_rule_his merchant_center_vela_v1.mc_discount_rule_log merchant_center_vela_v1.mc_discount_rule_products merchant_center_vela_v1.mc_discount_rule_products2_his merchant_center_vela_v1.mc_discount_rule_to_supplier merchant_center_vela_v1.mc_discount_type_third_party merchant_center_vela_v1.mc_duplicate_products merchant_center_vela_v1.mc_duplicate_products_new merchant_center_vela_v1.mc_email_ad merchant_center_vela_v1.mc_email_ad_desc merchant_center_vela_v1.mc_feature_history merchant_center_vela_v1.mc_flash_sale_deal merchant_center_vela_v1.mc_flash_sale_deal_product merchant_center_vela_v1.mc_form_to_apply_info merchant_center_vela_v1.mc_king_kong_area_operation_log merchant_center_vela_v1.mc_logs merchant_center_vela_v1.mc_logs_content_history merchant_center_vela_v1.mc_menu_panel merchant_center_vela_v1.mc_menu_panel_to_actions merchant_center_vela_v1.mc_modify_price_projects merchant_center_vela_v1.mc_npu_ct_site merchant_center_vela_v1.mc_ns_merge_record merchant_center_vela_v1.mc_ns_price merchant_center_vela_v1.mc_price_expression merchant_center_vela_v1.mc_price_lock merchant_center_vela_v1.mc_price_lock_products merchant_center_vela_v1.mc_products_alias merchant_center_vela_v1.mc_products_alias_channel merchant_center_vela_v1.mc_products_autoprice_log merchant_center_vela_v1.mc_products_average_sale_price merchant_center_vela_v1.mc_products_bi_report merchant_center_vela_v1.mc_products_description merchant_center_vela_v1.mc_products_desc_images_bak merchant_center_vela_v1.mc_products_flashsale_time merchant_center_vela_v1.mc_products_gross_margin_rate merchant_center_vela_v1.mc_products_gross_margin_rate_his merchant_center_vela_v1.mc_products_images_import_log merchant_center_vela_v1.mc_products_label_bak merchant_center_vela_v1.mc_products_price_follow merchant_center_vela_v1.mc_products_price_history merchant_center_vela_v1.mc_products_price_hold merchant_center_vela_v1.mc_products_priority_catchtop merchant_center_vela_v1.mc_products_procurement_price merchant_center_vela_v1.mc_products_procurement_price_his merchant_center_vela_v1.mc_products_scheduled_status merchant_center_vela_v1.mc_products_snapshot merchant_center_vela_v1.mc_products_static_data merchant_center_vela_v1.mc_products_static_shippingprice merchant_center_vela_v1.mc_products_stats_auto_sort_continent merchant_center_vela_v1.mc_products_stats_growthrate merchant_center_vela_v1.mc_products_stat_day merchant_center_vela_v1.mc_products_third_party_shippingprice merchant_center_vela_v1.mc_products_to_discount merchant_center_vela_v1.mc_product_import_price_log merchant_center_vela_v1.mc_promotion_category_discount_mapping merchant_center_vela_v1.mc_promotion_category_products merchant_center_vela_v1.mc_promotion_floor_desc_draft merchant_center_vela_v1.mc_promotion_floor_draft merchant_center_vela_v1.mc_promotion_floor_products_draft merchant_center_vela_v1.mc_promotion_floor_to_category_draft merchant_center_vela_v1.mc_promotion_floor_to_category_product_draft merchant_center_vela_v1.mc_promotion_floor_to_tab_page_draft merchant_center_vela_v1.mc_promotion_tab_page_desc_draft merchant_center_vela_v1.mc_rd_ga_fix_rate_1 merchant_center_vela_v1.mc_rd_ga_fix_rate_2 merchant_center_vela_v1.mc_rd_ga_fix_rate_3 merchant_center_vela_v1.mc_rd_ga_fix_rate_4 merchant_center_vela_v1.mc_recommend_product_view_bak20150417 merchant_center_vela_v1.mc_recommend_product_view_temp merchant_center_vela_v1.mc_rewards_type merchant_center_vela_v1.mc_reward_type merchant_center_vela_v1.mc_sku_price_hold merchant_center_vela_v1.mc_slimbanner_template merchant_center_vela_v1.mc_slimbanner_template_desc merchant_center_vela_v1.mc_store_template merchant_center_vela_v1.mc_task merchant_center_vela_v1.mc_task_products merchant_center_vela_v1.mc_temporary_products_info merchant_center_vela_v1.mc_top_menu merchant_center_vela_v1.mc_tung_diff_test merchant_center_vela_v1.mc_update_delivery_day_20200817 merchant_center_vela_v1.mc_update_delivery_day_20200831 merchant_center_vela_v1.mc_wizard_note merchant_center_vela_v1.multilingual_text merchant_center_vela_v1.name_rules merchant_center_vela_v1.name_rule_constant merchant_center_vela_v1.name_rule_constant_text merchant_center_vela_v1.name_rule_item_info merchant_center_vela_v1.name_rule_template merchant_center_vela_v1.name_rule_to merchant_center_vela_v1.pa_to_coordinate merchant_center_vela_v1.pa_to_custom_images merchant_center_vela_v1.phonenumber_regex merchant_center_vela_v1.postcode_regex merchant_center_vela_v1.products_copy_log merchant_center_vela_v1.products_extend_attributes merchant_center_vela_v1.products_measure_data merchant_center_vela_v1.products_to_attributes_extends_to_attributes merchant_center_vela_v1.sku_measure_data merchant_center_vela_v1.sku_weight merchant_center_vela_v1.tbl_2013q3_res_pid merchant_center_vela_v1.tbl_2013q3_res_sku merchant_center_vela_v1.tbl_2013q4_res_pid merchant_center_vela_v1.tbl_2013q4_res_sku merchant_center_vela_v1.test merchant_center_vela_v1.test_activity_icon_20210708 merchant_center_vela_v1.test_orders_products_free_duty merchant_center_vela_v1.test_pre_orders_products_free_duty merchant_center_vela_v1.tmp_18_highlights merchant_center_vela_v1.tmp_1_highlights merchant_center_vela_v1.tmp_2013_sell merchant_center_vela_v1.tmp_2013_sell_1 merchant_center_vela_v1.tmp_2013_sell_2 merchant_center_vela_v1.tmp_2013_sell_3 merchant_center_vela_v1.tmp_ad_content merchant_center_vela_v1.tmp_atav merchant_center_vela_v1.tmp_attr_to_tpl merchant_center_vela_v1.tmp_block_en merchant_center_vela_v1.tmp_categories_synonym merchant_center_vela_v1.tmp_cate_img merchant_center_vela_v1.tmp_coupon_id merchant_center_vela_v1.tmp_duplicate_products_id merchant_center_vela_v1.tmp_e merchant_center_vela_v1.tmp_epl_content merchant_center_vela_v1.tmp_epl_val merchant_center_vela_v1.tmp_hisprice merchant_center_vela_v1.tmp_hisprice_2cate merchant_center_vela_v1.tmp_hx merchant_center_vela_v1.tmp_mc_product_stock merchant_center_vela_v1.tmp_offstock_litb merchant_center_vela_v1.tmp_offstock_litb_add27 merchant_center_vela_v1.tmp_offstock_mini merchant_center_vela_v1.tmp_offstock_mini_add27 merchant_center_vela_v1.tmp_offstock_mini_add28 merchant_center_vela_v1.tmp_offstock_pid_add25 merchant_center_vela_v1.tmp_offstock_pid_add26 merchant_center_vela_v1.tmp_offstock_pid_add28 merchant_center_vela_v1.tmp_offstock_sku merchant_center_vela_v1.tmp_offstock_sku1 merchant_center_vela_v1.tmp_offstock_sku_add26 merchant_center_vela_v1.tmp_offstock_sku_add27 merchant_center_vela_v1.tmp_offstock_sku_add28 merchant_center_vela_v1.tmp_offstock_sku_final merchant_center_vela_v1.tmp_offstock_xh27 merchant_center_vela_v1.tmp_onstock_all29_litb merchant_center_vela_v1.tmp_onstock_litb_106 merchant_center_vela_v1.tmp_onstock_luoshuang merchant_center_vela_v1.tmp_onstock_mini_106 merchant_center_vela_v1.tmp_onstock_wuxi29_mini merchant_center_vela_v1.tmp_p merchant_center_vela_v1.tmp_p2c merchant_center_vela_v1.tmp_pid merchant_center_vela_v1.tmp_products_name merchant_center_vela_v1.tmp_products_sku_custom merchant_center_vela_v1.tmp_products_stats_auto_sort merchant_center_vela_v1.tmp_products_stats_auto_sort_continent merchant_center_vela_v1.tmp_sell merchant_center_vela_v1.tmp_tariff_payout_rules_vat_guoting merchant_center_vela_v1.tung_same_test merchant_center_vela_v1.v3_bi_cp_products merchant_center_vela_v1.v3_shared_inventory_rule_20220322 merchant_center_vela_v1.v3_shared_inventory_rule_country_20220322 merchant_center_vela_v1.v3_shared_inventory_rule_sku_20220322 merchant_center_vela_v1.v3_test merchant_center_vela_v1.v3_tungsten_test merchant_center_vela_v1.mc_magnification_price_history merchant_center_vela_v1.mc_magnification_discount_price_history
#
# docker rm -f tmp1
# docker run -d --name tmp2 -v /opt/mysql-compare:/opt --network host -w /opt python:3 sleep inf
# docker exec -it tmp1 pip install mysql-connector-python==9.0.0
