"""
sqlite_to_mysql_safe.py

Safer migration tool that handles schema mismatches between SQLite and MySQL.
It only copies columns that exist in both databases.

Usage:
  python sqlite_to_mysql_safe.py --sqlite database/epi_detection.db --skip-schema

It reads MySQL connection info from environment variables:
  MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
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
        load_dotenv()


def get_sqlite_columns(sqlite_conn, table_name):
    """Get list of columns in SQLite table"""
    cursor = sqlite_conn.cursor()
    cursor.execute(f'PRAGMA table_info("{table_name}")')
    return {row[1] for row in cursor.fetchall()}  # row[1] is column name


def get_mysql_columns(mysql_conn, table_name):
    """Get list of columns in MySQL table"""
    try:
        with mysql_conn.cursor() as cur:
            cur.execute(
                f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                f"WHERE TABLE_NAME = %s AND TABLE_SCHEMA = DATABASE()",
                (table_name,)
            )
            return {row[0] for row in cur.fetchall()}
    except Exception as e:
        print(f"Error getting MySQL columns for {table_name}: {e}")
        return set()


def copy_table(sqlite_conn, mysql_conn, table_name, chunk=500):
    """Copy table from SQLite to MySQL, handling column mismatches"""
    if table_name == 'sqlite_sequence':
        return 0
    
    sqlite_cols = get_sqlite_columns(sqlite_conn, table_name)
    mysql_cols = get_mysql_columns(mysql_conn, table_name)
    
    if not mysql_cols:
        print(f"  - Table {table_name} not found in MySQL (skipping)")
        return 0
    
    # Find common columns
    common_cols = sorted(sqlite_cols & mysql_cols)
    
    if not common_cols:
        print(f"  - No common columns found (SQLite: {sqlite_cols}, MySQL: {mysql_cols})")
        return 0
    
    # Read from SQLite with column reordering
    s_cursor = sqlite_conn.cursor()
    all_cols_sql = ','.join([f'"{c}"' for c in sorted(sqlite_cols)])
    s_cursor.execute(f'SELECT {all_cols_sql} FROM "{table_name}"')
    rows = s_cursor.fetchall()
    
    if not rows:
        return 0
    
    # Map column names to indices in the SELECT
    sqlite_col_list = sorted(sqlite_cols)
    col_idx_map = {col: idx for idx, col in enumerate(sqlite_col_list)}
    
    # Extract only common columns
    filtered_rows = []
    for row in rows:
        filtered_row = tuple(row[col_idx_map[col]] for col in common_cols)
        filtered_rows.append(filtered_row)
    
    # Build INSERT statement
    col_list = ','.join([f'`{c}`' for c in common_cols])
    placeholders = ','.join(['%s'] * len(common_cols))
    insert_sql = f'INSERT INTO `{table_name}` ({col_list}) VALUES ({placeholders})'
    
    # Copy in batches
    m_cursor = mysql_conn.cursor()
    count = 0
    for i in range(0, len(filtered_rows), chunk):
        batch = filtered_rows[i:i+chunk]
        try:
            m_cursor.executemany(insert_sql, batch)
            mysql_conn.commit()
            count += len(batch)
        except Exception as e:
            print(f"    - Batch error: {e}")
            mysql_conn.rollback()
    
    return count


def main():
    parser = argparse.ArgumentParser(
        description='Safely copy SQLite DB into MySQL (handles schema mismatches)'
    )
    parser.add_argument('--sqlite', default=os.getenv('SQLITE_PATH', 'database/epi_detection.db'))
    parser.add_argument('--skip-schema', action='store_true', help='Skip schema creation')
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
    
    # Connect to MySQL
    try:
        mysql_conn = pymysql.connect(
            host=mysql_host,
            port=mysql_port,
            user=mysql_user,
            password=mysql_pass,
            database=mysql_db,
            charset='utf8mb4',
            autocommit=False
        )
    except Exception as e:
        print(f"Failed to connect to MySQL: {e}")
        return

    # Connect to SQLite
    sqlite_conn = sqlite3.connect(str(sqlite_path))
    
    # Get list of tables
    s_cur = sqlite_conn.cursor()
    s_cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in s_cur.fetchall()]

    print(f"Found {len(tables)} tables in SQLite")
    print()

    total = 0
    errors = 0
    for t in tables:
        try:
            copied = copy_table(sqlite_conn, mysql_conn, t)
            print(f"  ✓ {t}: {copied} rows")
            total += copied
        except Exception as e:
            print(f"  ✗ {t}: {e}")
            errors += 1

    sqlite_conn.close()
    mysql_conn.close()
    
    print()
    print(f"Migration complete!")
    print(f"  Total rows copied: {total}")
    print(f"  Tables with errors: {errors}")


if __name__ == '__main__':
    main()
