#!/usr/bin/env python3

import subprocess
import json
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


def main():
    parser = argparse.ArgumentParser(description="Generate BQRS files from CodeQL database using QL queries")
    parser.add_argument("--codeql-db", type=Path, required=True, help="Path to CodeQL database")
    parser.add_argument("--ql-file", type=Path, required=True, help="Path to QL query file")
    parser.add_argument("--bqrs", type=Path, help="Output path for BQRS file")
    parser.add_argument("--metadata", action="store_true", help="Print BQRS metadata")

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
        bqrs_file = Path(tempfile.mkstemp(suffix=".bqrs")[1])

    run_query(args.codeql_db, args.ql_file, bqrs_file)

    # 输出元数据
    if args.metadata:
        result_sets = get_bqrs_metadata(bqrs_file)
        print(json.dumps(result_sets, indent=2))

    # 清理临时BQRS文件
    if not args.bqrs:
        bqrs_file.unlink()

    logger.info("BQRS extraction completed successfully")


if __name__ == "__main__":
    main()
