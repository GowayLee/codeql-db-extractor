#!/usr/bin/env python3

import subprocess
import json
import sqlite3
import csv
import re
import argparse
import tempfile
import shutil
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def setup_logging():
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logging.basicConfig(level=logging.INFO, handlers=[console_handler])


def run_query(codeql_db: Path, ql_file: Path, output_bqrs: Path):
    """执行QL查询生成BQRS文件"""
    logger.info(f"Running query on database: {codeql_db}")
    logger.info(f"Using QL file: {ql_file}")

    subprocess.run(
        [
            "codeql",
            "query",
            "run",
            "-d",
            f"{codeql_db}",
            "-o",
            f"{output_bqrs}",
            "--",
            f"{ql_file}",
        ],
        check=True,
    )
    logger.info(f"BQRS file generated: {output_bqrs}")


def get_bqrs_metadata(bqrs_file: Path):
    """获取BQRS文件的元数据"""
    logger.info(f"Getting metadata from BQRS file: {bqrs_file}")

    result = subprocess.run(
        [
            "codeql",
            "bqrs",
            "info",
            "--format=json",
            f"{bqrs_file}",
        ],
        stdout=subprocess.PIPE,
        check=True,
    )

    metadata = json.loads(result.stdout)
    return metadata["result-sets"]


def decode_to_csv(bqrs_file: Path, result_set: str, output_csv: Path):
    """将单个结果集解码为CSV文件"""
    logger.info(f"Decoding result set '{result_set}' to CSV: {output_csv}")

    with open(output_csv, "w") as f:
        subprocess.run(
            [
                "codeql",
                "bqrs",
                "decode",
                "--format=csv",
                "--entities=id",
                f"--result-set={result_set}",
                f"{bqrs_file}",
            ],
            stdout=f,
            check=True,
        )


def decode_all_to_csv(bqrs_file: Path, output_dir: Path):
    """将所有结果集解码为CSV文件"""
    logger.info(f"Decoding all result sets to CSV in directory: {output_dir}")

    result_sets = get_bqrs_metadata(bqrs_file)

    output_dir.mkdir(exist_ok=True)

    for result in result_sets:
        result_set_name = result["name"]
        table_name = re.sub(r"^get_", "", result_set_name)
        output_csv = output_dir / f"{table_name}.csv"

        decode_to_csv(bqrs_file, result_set_name, output_csv)
        logger.info(f"Saved: {output_csv}")


def decode_to_sqlite(bqrs_file: Path, sqlite_db: Path):
    """将所有结果集解码到SQLite数据库"""
    logger.info(f"Decoding all result sets to SQLite database: {sqlite_db}")

    result_sets = get_bqrs_metadata(bqrs_file)

    # 删除已存在的数据库文件
    sqlite_db.unlink(missing_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # 先解码所有结果集到临时CSV文件
        tables = []
        for result in result_sets:
            result_set_name = result["name"]
            table_name = re.sub(r"^get_", "", result_set_name)
            table_columns = [c["name"] for c in result["columns"]]

            tables.append({
                "name": table_name,
                "columns": table_columns,
                "csv_file": tmpdir_path / f"{table_name}.csv"
            })

            decode_to_csv(bqrs_file, result_set_name, tables[-1]["csv_file"])

        # 导入到SQLite数据库
        with sqlite3.connect(sqlite_db) as conn:
            cur = conn.cursor()

            for table in tables:
                with open(table["csv_file"], "r") as f:
                    reader = csv.reader(f)
                    _ = next(reader)  # 跳过CSV头部

                    # 创建表
                    quoted_table_name = f'"{table["name"]}"'
                    quoted_columns = [f'"{col}"' for col in table["columns"]]
                    create_table_sql = f'''
                        CREATE TABLE {quoted_table_name} (
                            {", ".join(quoted_columns)}
                        )
                    '''
                    cur.execute(create_table_sql)

                    # 插入数据
                    placeholders = ", ".join(["?"] * len(table["columns"]))
                    insert_sql = f"INSERT INTO {quoted_table_name} VALUES ({placeholders})"
                    cur.executemany(insert_sql, reader)

                    conn.commit()
                    logger.info(f"Created table: {table['name']} with {cur.rowcount} rows")


def main():
    parser = argparse.ArgumentParser(description="Extract data from CodeQL database using BQRS files")
    parser.add_argument("--codeql-db", type=Path, required=True, help="Path to CodeQL database")
    parser.add_argument("--ql-file", type=Path, required=True, help="Path to QL query file")
    parser.add_argument("--csv", type=Path, help="Output directory for CSV files")
    parser.add_argument("--sqlite", type=Path, help="Output path for SQLite database")
    parser.add_argument("--bqrs", type=Path, help="Output path for BQRS file (optional)")

    args = parser.parse_args()
    setup_logging()

    # 检查codeql命令是否存在
    if shutil.which("codeql") is None:
        logger.error("codeql command not found in PATH")
        exit(1)

    # 生成BQRS文件
    if args.bqrs:
        bqrs_file = args.bqrs
    else:
        bqrs_file = Path(tempfile.mktemp(suffix=".bqrs"))

    run_query(args.codeql_db, args.ql_file, bqrs_file)

    # 导出数据
    if args.csv:
        decode_all_to_csv(bqrs_file, args.csv)

    if args.sqlite:
        decode_to_sqlite(bqrs_file, args.sqlite)

    # 清理临时BQRS文件
    if not args.bqrs:
        bqrs_file.unlink()

    logger.info("Extraction completed successfully")


if __name__ == "__main__":
    main()
