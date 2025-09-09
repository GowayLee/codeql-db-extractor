# Extractor Directory

This directory contains tools for extracting data from CodeQL databases and generating QL queries.

## Scripts

### 1. db-extractor.py

**Purpose**: Executes QL queries on CodeQL databases to generate BQRS files.

**Usage**:

```bash
python3 db-extractor.py --codeql-db <path_to_codeql_db> --ql-file <path_to_ql_file> [--bqrs <output_bqrs_file>] [--metadata]
```

**Options**:

- `--codeql-db`: Path to the CodeQL database
- `--ql-file`: Path to the QL query file
- `--bqrs`: Output path for the BQRS file (optional, creates temporary file if not specified)
- `--metadata`: Print BQRS metadata information

**Example**:

```bash
python3 db-extractor.py --codeql-db /path/to/database --ql-file query.ql --bqrs output.bqrs --metadata
```

### 2. ql-generator.py

**Purpose**: Generates QL class definitions and query predicates from database schema JSON files.

**Usage**:

```bash
python3 ql-generator.py <input_json_file> [-o <output_ql_file>]
```

**Options**:

- `input_json_file`: Input JSON file containing database schema information
- `-o, --output`: Output QL file path (optional, defaults to stdout)

**Example**:

```bash
python3 ql-generator.py schema.json -o generated_queries.ql
```

## Subdirectories

### cpp-ql-extractor/

Contains QL code specific to C++ code analysis:

- `extractor.ql`: Main QL extractor for C++
- `qlpack.yml`: CodeQL pack configuration
- `codeql-pack.lock.yml`: Lock file for dependencies

### java-ql-extractor/

Contains QL code specific to Java code analysis:

- `extractor.ql`: Main QL extractor for Java
- `qlpack.yml`: CodeQL pack configuration
- `codeql-pack.lock.yml`: Lock file for dependencies

## Dependencies

- Python 3.x
- CodeQL CLI must be installed and available in PATH
- Required Python modules: `subprocess`, `json`, `argparse`, `tempfile`, `shutil`, `pathlib`, `logging`

## Workflow

1. Use `ql-generator.py` to generate QL queries from schema JSON
2. Use `db-extractor.py` to execute queries against CodeQL databases
3. Generated BQRS files can be processed by decoder scripts

