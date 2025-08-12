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

from . import mysql_compare

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

if __name__ == "__main__":
    mysql_compare.run()
