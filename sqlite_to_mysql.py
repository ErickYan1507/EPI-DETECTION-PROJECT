"""
sqlite_to_mysql.py

Simple migration tool to copy all tables/rows from a local SQLite DB into a MySQL database.

Usage:
  python sqlite_to_mysql.py --sqlite database/epi_detection.db --create-schema

It reads MySQL connection info from environment variables (recommended):
  MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

If `--create-schema` is passed and `sql/01_create_database.sql` exists it will execute it before importing.
"""
import os
import argparse
import sqlite3
import pymysql
from pathlib import Path
from dotenv import load_dotenv


def load_env(env_path=None):
    if env_path and Path(env_path).exists():
        load_dotenv(env_path)
    else:
        # try project .env if present
        load_dotenv()


def create_mysql_db_if_missing(conn, db_name):
    with conn.cursor() as cur:
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    conn.commit()


def execute_schema(conn, schema_file):
    with open(schema_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    # Heuristic fixes for MariaDB (XAMPP): replace 'NULLABLE' with 'NULL'
    sql = sql.replace(' NULLABLE', ' NULL')
    sql = sql.replace('\r\n', '\n')
    with conn.cursor() as cur:
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        for i, stmt in enumerate(statements, 1):
            try:
                cur.execute(stmt)
            except Exception as e:
                print(f"Schema execution error on statement {i}: {e}")
                print("--- Statement start ---")
                print(stmt[:1000])
                print("--- Statement end ---")
                # continue to attempt remaining statements
        conn.commit()


def copy_table(sqlite_conn, mysql_conn, table_name, chunk=500):
    if table_name == 'sqlite_sequence':
        return 0
    s_cur = sqlite_conn.cursor()
    s_cur.execute(f'SELECT * FROM "{table_name}"')
    rows = s_cur.fetchall()
    if not rows:
        return 0
    cols = [d[0] for d in s_cur.description]
    placeholders = ','.join(['%s'] * len(cols))
    col_list = ','.join([f'`{c}`' for c in cols])
    insert_sql = f'INSERT INTO `{table_name}` ({col_list}) VALUES ({placeholders})'
    m_cur = mysql_conn.cursor()
    count = 0
    for i in range(0, len(rows), chunk):
        batch = rows[i:i+chunk]
        # convert sqlite types to Python types acceptable by PyMySQL (mostly passthrough)
        m_cur.executemany(insert_sql, batch)
        mysql_conn.commit()
        count += len(batch)
    return count


def main():
    parser = argparse.ArgumentParser(description='Copy SQLite DB into MySQL')
    parser.add_argument('--sqlite', default=os.getenv('SQLITE_PATH', 'database/epi_detection.db'))
    parser.add_argument('--create-schema', action='store_true')
    parser.add_argument('--env', help='Path to .env file to load')
    args = parser.parse_args()

    load_env(args.env)

    mysql_host = os.getenv('MYSQL_HOST', os.getenv('DB_HOST', 'localhost'))
    mysql_port = int(os.getenv('MYSQL_PORT', os.getenv('DB_PORT', 3306)))
    mysql_user = os.getenv('MYSQL_USER', os.getenv('DB_USER', 'epi_user'))
    mysql_pass = os.getenv('MYSQL_PASSWORD', os.getenv('DB_PASSWORD', ''))
    mysql_db = os.getenv('MYSQL_DB', os.getenv('DB_NAME', 'epi_detection_db'))

    sqlite_path = Path(args.sqlite)
    if not sqlite_path.exists():
        print(f"SQLite DB not found: {sqlite_path}")
        return

    print(f"Connecting to MySQL {mysql_user}@{mysql_host}:{mysql_port}/{mysql_db}")
    # connect to mysql server (no DB) to ensure DB exists
    conn0 = pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_pass, charset='utf8mb4', autocommit=False)
    try:
        create_mysql_db_if_missing(conn0, mysql_db)
    finally:
        conn0.close()

    # connect to target DB
    mysql_conn = pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_pass, db=mysql_db, charset='utf8mb4', autocommit=False)

    if args.create_schema:
        schema_file = Path('sql/01_create_database.sql')
        if schema_file.exists():
            print("Executing schema file to create tables...")
            execute_schema(mysql_conn, schema_file)
        else:
            print("Schema file sql/01_create_database.sql not found; skipping schema creation")

    sqlite_conn = sqlite3.connect(str(sqlite_path))
    s_cur = sqlite_conn.cursor()
    s_cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in s_cur.fetchall()]

    total = 0
    for t in tables:
        print(f"Copying table: {t}")
        try:
            copied = copy_table(sqlite_conn, mysql_conn, t)
            print(f"  - rows copied: {copied}")
            total += copied
        except Exception as e:
            print(f"  ! Error copying table {t}: {e}")

    sqlite_conn.close()
    mysql_conn.close()
    print(f"Done. Total rows copied: {total}")


if __name__ == '__main__':
    main()
