#!/usr/bin/env python3

import sqlite3
import csv
import re
import argparse
from pathlib import Path
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


def setup_logging():
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logging.basicConfig(level=logging.INFO, handlers=[console_handler])


def is_souffle_keyword(column_name: str) -> bool:
    """检查列名是否为Soufflé关键字"""
    souffle_keywords = {
        # 逻辑运算符
        "true", "false", "not", "and", "or",
        # 控制流
        "if", "then", "else", "endif",
        # 类型关键字
        "number", "symbol", "float",
        # 声明关键字
        "decl", "input", "output", "functor", "choice-domain",
        # 其他保留字
        "rule", "fact", "query", "plan", "pragma"
    }
    return column_name.lower() in souffle_keywords


def transform_column_name(col: str) -> str:
    """转换列名为Soufflé兼容的格式，避免关键字冲突"""
    # 移除"ID of "前缀
    col = re.sub(r"^ID of ", "", col)
    # 将空格和特殊字符转换为下划线
    col = re.sub(r"[^a-zA-Z0-9_]", "_", col)
    # 确保以字母开头
    if col and not col[0].isalpha():
        col = "col_" + col
    
    # 转换为小写
    col = col.lower()
    
    # 如果是Soufflé关键字，添加前缀避免冲突
    if is_souffle_keyword(col):
        col = "col_" + col
    
    return col


def get_table_names(conn: sqlite3.Connection) -> List[str]:
    """获取数据库中所有表名"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
    """)
    return [row[0] for row in cursor.fetchall()]


def get_table_columns(conn: sqlite3.Connection, table_name: str) -> List[str]:
    """获取表的列名"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]


def export_table_to_csv(conn: sqlite3.Connection, table_name: str, output_dir: Path):
    """将单个表导出为CSV文件"""
    # 获取原始列名
    original_columns = get_table_columns(conn, table_name)
    
    # 转换列名为Soufflé兼容格式
    transformed_columns = [transform_column_name(col) for col in original_columns]
    
    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # CSV文件路径
    csv_file = output_dir / f"{table_name}.csv"
    
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        
        # 写入转换后的列名
        writer.writerow(transformed_columns)
        
        # 写入数据
        row_count = 0
        for row in cursor.fetchall():
            writer.writerow(row)
            row_count += 1
    
    logger.info(f"Exported table {table_name} with {row_count} rows to {csv_file}")
    return row_count


def sqlite_to_csv(sqlite_db: Path, output_dir: Path):
    """将SQLite数据库中的所有表转换为CSV文件"""
    logger.info(f"Converting SQLite database {sqlite_db} to CSV files in {output_dir}")
    
    if not sqlite_db.exists():
        logger.error(f"SQLite database not found: {sqlite_db}")
        exit(1)
    
    with sqlite3.connect(sqlite_db) as conn:
        table_names = get_table_names(conn)
        
        if not table_names:
            logger.warning(f"No tables found in database: {sqlite_db}")
            return
        
        total_tables = 0
        total_rows = 0
        
        for table_name in table_names:
            try:
                row_count = export_table_to_csv(conn, table_name, output_dir)
                total_tables += 1
                total_rows += row_count
            except Exception as e:
                logger.error(f"Failed to export table {table_name}: {e}")
        
        logger.info(f"Exported {total_tables} tables with {total_rows} total rows")


def main():
    parser = argparse.ArgumentParser(description="Convert SQLite database to CSV files")
    parser.add_argument("--sqlite", type=Path, required=True, help="Input SQLite database file")
    parser.add_argument("--output", type=Path, required=True, help="Output directory for CSV files")
    
    args = parser.parse_args()
    setup_logging()
    
    sqlite_to_csv(args.sqlite, args.output)
    logger.info("SQLite to CSV conversion completed successfully")


if __name__ == "__main__":
    main()