#!/usr/bin/env python3

import sqlite3
import csv
import re
import argparse
from pathlib import Path
import logging

# SQLite reserved keywords that need to be filtered
SQLITE_KEYWORDS = {
    'ABORT', 'ACTION', 'ADD', 'AFTER', 'ALL', 'ALTER', 'ANALYZE', 'AND', 'AS', 'ASC',
    'ATTACH', 'AUTOINCREMENT', 'BEFORE', 'BEGIN', 'BETWEEN', 'BY', 'CASCADE', 'CASE',
    'CAST', 'CHECK', 'COLLATE', 'COLUMN', 'COMMIT', 'CONFLICT', 'CONSTRAINT', 'CREATE',
    'CROSS', 'CURRENT_DATE', 'CURRENT_TIME', 'CURRENT_TIMESTAMP', 'DATABASE', 'DEFAULT',
    'DEFERRABLE', 'DEFERRED', 'DELETE', 'DESC', 'DETACH', 'DISTINCT', 'DROP', 'EACH',
    'ELSE', 'END', 'ESCAPE', 'EXCEPT', 'EXCLUSIVE', 'EXISTS', 'EXPLAIN', 'FAIL', 'FOR',
    'FOREIGN', 'FROM', 'FULL', 'GLOB', 'GROUP', 'HAVING', 'IF', 'IGNORE', 'IMMEDIATE',
    'IN', 'INDEX', 'INDEXED', 'INITIALLY', 'INNER', 'INSERT', 'INSTEAD', 'INTERSECT',
    'INTO', 'IS', 'ISNULL', 'JOIN', 'KEY', 'LEFT', 'LIKE', 'LIMIT', 'MATCH', 'NATURAL',
    'NO', 'NOT', 'NOTNULL', 'NULL', 'OF', 'OFFSET', 'ON', 'OR', 'ORDER', 'OUTER',
    'PLAN', 'PRAGMA', 'PRIMARY', 'QUERY', 'RAISE', 'RECURSIVE', 'REFERENCES', 'REGEXP',
    'REINDEX', 'RELEASE', 'RENAME', 'REPLACE', 'RESTRICT', 'RIGHT', 'ROLLBACK', 'ROW',
    'SAVEPOINT', 'SELECT', 'SET', 'TABLE', 'TEMP', 'TEMPORARY', 'THEN', 'TO', 'TRANSACTION',
    'TRIGGER', 'UNION', 'UNIQUE', 'UPDATE', 'USING', 'VACUUM', 'VALUES', 'VIEW', 'VIRTUAL',
    'WHEN', 'WHERE', 'WITH', 'WITHOUT'
}

logger = logging.getLogger(__name__)


def filter_sqlite_keyword(column_name: str) -> str:
    """Filter SQLite reserved keywords by appending '_' suffix"""
    if column_name.upper() in SQLITE_KEYWORDS:
        return f"{column_name}_"
    return column_name


def setup_logging():
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logging.basicConfig(level=logging.INFO, handlers=[console_handler])


def csv_to_sqlite(csv_dir: Path, sqlite_db: Path):
    """将CSV目录中的所有CSV文件导入到SQLite数据库"""
    logger.info(f"Converting CSV files from {csv_dir} to SQLite database: {sqlite_db}")

    # 删除已存在的数据库文件
    sqlite_db.unlink(missing_ok=True)

    with sqlite3.connect(sqlite_db) as conn:
        cur = conn.cursor()

        # 获取所有CSV文件
        csv_files = list(csv_dir.glob("*.csv"))

        if not csv_files:
            logger.warning(f"No CSV files found in directory: {csv_dir}")
            return

        for csv_file in csv_files:
            table_name = filter_sqlite_keyword(csv_file.stem)

            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.reader(f)

                # 读取CSV头部获取列名
                try:
                    columns = next(reader)
                except StopIteration:
                    logger.warning(f"Empty CSV file: {csv_file}")
                    continue

                # 转换列名：移除"ID of "前缀和尾部下划线
                transformed_columns = [
                    re.sub(r"^ID of ", "", col)  # Remove "ID of " prefix
                    .rstrip("_")  # Remove trailing underscores
                    for col in columns
                ]

                # 创建表
                quoted_table_name = f'"{table_name}"'
                quoted_columns = [f'"{col}"' for col in transformed_columns]
                create_table_sql = f'''
                    CREATE TABLE {quoted_table_name} (
                        {", ".join(quoted_columns)}
                    )
                '''
                cur.execute(create_table_sql)

                # 插入数据
                placeholders = ", ".join(["?"] * len(transformed_columns))
                insert_sql = f"INSERT INTO {quoted_table_name} VALUES ({placeholders})"

                row_count = 0
                for row in reader:
                    if len(row) == len(columns):  # 确保行数据与列数匹配
                        cur.execute(insert_sql, row)
                        row_count += 1

                conn.commit()
                logger.info(f"Created table: {table_name} with {row_count} rows")


def main():
    parser = argparse.ArgumentParser(description="Convert CSV files to SQLite database")
    parser.add_argument("--csv", type=Path, required=True, help="Input directory containing CSV files")
    parser.add_argument("--sqlite", type=Path, required=True, help="Output path for SQLite database")

    args = parser.parse_args()
    setup_logging()

    # 检查CSV目录是否存在
    if not args.csv.exists() or not args.csv.is_dir():
        logger.error(f"CSV directory not found: {args.csv}")
        exit(1)

    csv_to_sqlite(args.csv, args.sqlite)
    logger.info("CSV to SQLite conversion completed successfully")


if __name__ == "__main__":
    main()
