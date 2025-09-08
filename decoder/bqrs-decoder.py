#!/usr/bin/env python3

import json
import subprocess
import re
import argparse
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


def get_bqrs_metadata(bqrs_file: Path):
    """获取BQRS文件的元数据"""
    logger.info(f"Getting metadata from BQRS file: {bqrs_file}")

    import subprocess
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






def main():
    parser = argparse.ArgumentParser(description="Decode BQRS files to CSV")
    parser.add_argument("--bqrs", type=Path, required=True, help="Path to BQRS file")
    parser.add_argument("--csv", type=Path, required=True, help="Output directory for CSV files")

    args = parser.parse_args()
    setup_logging()

    # 检查BQRS文件是否存在
    if not args.bqrs.exists():
        logger.error(f"BQRS file not found: {args.bqrs}")
        exit(1)

    # 导出数据到CSV
    decode_all_to_csv(args.bqrs, args.csv)
    logger.info("BQRS to CSV decoding completed successfully")


if __name__ == "__main__":
    main()
