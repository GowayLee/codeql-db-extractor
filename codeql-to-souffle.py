#!/usr/bin/env python3
"""
CodeQL to Soufflé Datalog Pipeline

This script provides a unified interface for converting CodeQL databases or SQLite databases
to Soufflé Datalog format. It manages intermediate files and cleanup automatically.
"""

import argparse
import logging
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)


def setup_logging():
    """Set up logging configuration"""
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logging.basicConfig(level=logging.INFO, handlers=[console_handler])


def check_codeql_available():
    """Check if CodeQL CLI is available in PATH"""
    if shutil.which("codeql") is None:
        logger.error("CodeQL CLI not found in PATH. Please install CodeQL and ensure it's in your PATH.")
        return False
    return True


def run_command(cmd: list, description: str) -> bool:
    """Run a command and handle errors"""
    logger.info(f"{description}: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        return False
    except FileNotFoundError as e:
        logger.error(f"Command not found: {e}")
        return False


def codeql_to_bqrs(codeql_db: Path, language: str, output_bqrs: Path) -> bool:
    """Convert CodeQL database to BQRS file using appropriate QL extractor"""
    # Determine the correct QL file based on language
    ql_extractor_dir = Path(__file__).parent / "extractor"

    if language == "cpp":
        ql_file = ql_extractor_dir / "cpp-ql-extractor" / "extractor.ql"
    elif language == "java":
        ql_file = ql_extractor_dir / "java-ql-extractor" / "extractor.ql"
    else:
        logger.error(f"Unsupported language: {language}. Supported languages: cpp, java")
        return False

    if not ql_file.exists():
        logger.error(f"QL extractor file not found: {ql_file}")
        return False

    # Run the QL query to generate BQRS
    cmd = [
        "codeql", "query", "run",
        "-d", str(codeql_db),
        "-o", str(output_bqrs),
        "--", str(ql_file)
    ]

    return run_command(cmd, "Running CodeQL query")


def bqrs_to_csv(bqrs_file: Path, output_csv_dir: Path) -> bool:
    """Convert BQRS file to CSV files using bqrs-decoder.py"""
    decoder_script = Path(__file__).parent / "decoder" / "bqrs-decoder.py"

    if not decoder_script.exists():
        logger.error(f"BQRS decoder script not found: {decoder_script}")
        return False

    cmd = [
        "python3", str(decoder_script),
        "--bqrs", str(bqrs_file),
        "--csv", str(output_csv_dir)
    ]

    return run_command(cmd, "Converting BQRS to CSV")


def csv_to_sqlite(csv_dir: Path, output_sqlite: Path) -> bool:
    """Convert CSV files to SQLite database"""
    converter_script = Path(__file__).parent / "decoder" / "csv-to-sqlite.py"

    if not converter_script.exists():
        logger.error(f"CSV to SQLite script not found: {converter_script}")
        return False

    cmd = [
        "python3", str(converter_script),
        "--csv", str(csv_dir),
        "--sqlite", str(output_sqlite)
    ]

    return run_command(cmd, "Converting CSV to SQLite")


def sqlite_to_csv(sqlite_db: Path, output_csv_dir: Path) -> bool:
    """Convert SQLite database to CSV files"""
    converter_script = Path(__file__).parent / "decoder" / "sqlite-to-csv.py"

    if not converter_script.exists():
        logger.error(f"SQLite to CSV script not found: {converter_script}")
        return False

    cmd = [
        "python3", str(converter_script),
        "--sqlite", str(sqlite_db),
        "--output", str(output_csv_dir)
    ]

    return run_command(cmd, "Converting SQLite to CSV")


def csv_to_souffle(csv_dir: Path, output_dl: Path, prefix: Optional[str] = None) -> bool:
    """Convert CSV files to Soufflé Datalog format"""
    converter_script = Path(__file__).parent / "decoder" / "csv-to-souffle.py"

    if not converter_script.exists():
        logger.error(f"CSV to Soufflé script not found: {converter_script}")
        return False

    cmd = [
        "python3", str(converter_script),
        "--csv", str(csv_dir),
        "--output", str(output_dl)
    ]

    if prefix:
        cmd.extend(["--prefix", prefix])

    return run_command(cmd, "Converting CSV to Soufflé Datalog")


def codeql_to_souffle_workflow(
    codeql_db: Path,
    language: str,
    output_dl: Path,
    prefix: Optional[str] = None,
    keep_intermediate: bool = False
) -> bool:
    """Complete workflow: CodeQL database → BQRS → CSV → Soufflé Datalog"""
    logger.info(f"Starting CodeQL to Soufflé workflow for {language} database")

    with tempfile.TemporaryDirectory(prefix="codeql_to_souffle_") as temp_dir:
        temp_path = Path(temp_dir)

        # Step 1: CodeQL → BQRS
        bqrs_file = temp_path / "output.bqrs"
        if not codeql_to_bqrs(codeql_db, language, bqrs_file):
            return False

        # Step 2: BQRS → CSV
        csv_dir = temp_path / "csv_output"
        csv_dir.mkdir()
        if not bqrs_to_csv(bqrs_file, csv_dir):
            return False

        # Step 3: CSV → Soufflé Datalog
        if not csv_to_souffle(csv_dir, output_dl, prefix):
            return False

        # Optional: Keep intermediate files
        if keep_intermediate:
            intermediate_dir = output_dl.parent / "intermediate"
            intermediate_dir.mkdir(exist_ok=True)

            # Copy BQRS file
            shutil.copy2(bqrs_file, intermediate_dir / "output.bqrs")

            # Copy CSV files
            csv_backup = intermediate_dir / "csv_output"
            if csv_backup.exists():
                shutil.rmtree(csv_backup)
            shutil.copytree(csv_dir, csv_backup)

            logger.info(f"Intermediate files saved to: {intermediate_dir}")

        logger.info(f"Soufflé Datalog file generated: {output_dl}")
        return True


def sqlite_to_souffle_workflow(
    sqlite_db: Path,
    output_dl: Path,
    prefix: Optional[str] = None,
    keep_intermediate: bool = False
) -> bool:
    """Workflow: SQLite database → CSV → Soufflé Datalog"""
    logger.info("Starting SQLite to Soufflé workflow")

    with tempfile.TemporaryDirectory(prefix="sqlite_to_souffle_") as temp_dir:
        temp_path = Path(temp_dir)

        # Step 1: SQLite → CSV
        csv_dir = temp_path / "csv_output"
        csv_dir.mkdir()
        if not sqlite_to_csv(sqlite_db, csv_dir):
            return False

        # Step 2: CSV → Soufflé Datalog
        if not csv_to_souffle(csv_dir, output_dl, prefix):
            return False

        # Optional: Keep intermediate files
        if keep_intermediate:
            intermediate_dir = output_dl.parent / "intermediate"
            intermediate_dir.mkdir(exist_ok=True)

            # Copy CSV files
            csv_backup = intermediate_dir / "csv_output"
            if csv_backup.exists():
                shutil.rmtree(csv_backup)
            shutil.copytree(csv_dir, csv_backup)

            logger.info(f"Intermediate CSV files saved to: {intermediate_dir}")

        logger.info(f"Soufflé Datalog file generated: {output_dl}")
        return True


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Convert CodeQL databases or SQLite databases to Soufflé Datalog format"
    )

    # Input source selection
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--codeql-db", type=Path, help="Path to CodeQL database")
    input_group.add_argument("--sqlite-db", type=Path, help="Path to SQLite database")

    # Language selection (for CodeQL only)
    parser.add_argument("--language", choices=["cpp", "java"],
                       help="Programming language (required for CodeQL databases)")

    # Output options
    parser.add_argument("--output", "-o", type=Path, required=True,
                       help="Output Soufflé .dl file path")
    parser.add_argument("--prefix", type=str,
                       help="Prefix for all relation names in Soufflé output")

    # Additional options
    parser.add_argument("--keep-intermediate", action="store_true",
                       help="Keep intermediate files (BQRS, CSV) for debugging")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")

    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    setup_logging()

    # Validate inputs
    if args.codeql_db:
        if not args.language:
            logger.error("Language must be specified for CodeQL databases (--language cpp|java)")
            sys.exit(1)

        if not args.codeql_db.exists():
            logger.error(f"CodeQL database not found: {args.codeql_db}")
            sys.exit(1)

        if not check_codeql_available():
            sys.exit(1)

        # Run CodeQL workflow
        success = codeql_to_souffle_workflow(
            args.codeql_db, args.language, args.output,
            args.prefix, args.keep_intermediate
        )

    else:  # SQLite database
        if not args.sqlite_db.exists():
            logger.error(f"SQLite database not found: {args.sqlite_db}")
            sys.exit(1)

        # Run SQLite workflow
        success = sqlite_to_souffle_workflow(
            args.sqlite_db, args.output, args.prefix, args.keep_intermediate
        )

    if not success:
        logger.error("Workflow failed")
        sys.exit(1)

    logger.info("Workflow completed successfully")


if __name__ == "__main__":
    main()
