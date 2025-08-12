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


def hash_dict(d):
    # return frozenset(d.items())
    return frozenset((k, frozenset(v) if isinstance(v, set) else v) for k, v in d.items())


def find_missing_in_b(a, b):
    b_hashes = {hash_dict(d) for d in b}

    missing_in_b = [d for d in a if hash_dict(d) not in b_hashes]

    return missing_in_b
