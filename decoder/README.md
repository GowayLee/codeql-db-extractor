# Decoder Directory

This directory contains tools for decoding and converting BQRS files to various formats including CSV, SQLite, and Soufflé Datalog.

## Scripts

### 1. bqrs-decoder.py

**Purpose**: Decodes BQRS files to CSV format.

**Usage**:

```bash
python3 bqrs-decoder.py --bqrs <input_bqrs_file> --csv <output_csv_directory>
```

**Options**:

- `--bqrs`: Path to the input BQRS file
- `--csv`: Output directory for CSV files

**Example**:

```bash
python3 bqrs-decoder.py --bqrs results.bqrs --csv ./csv_output
```

**Output**: Creates individual CSV files for each result set in the BQRS file.

### 2. csv-to-sqlite.py

**Purpose**: Converts CSV files to SQLite database.

**Usage**:

```bash
python3 csv-to-sqlite.py --csv <input_csv_directory> --sqlite <output_sqlite_file>
```

**Options**:

- `--csv`: Input directory containing CSV files
- `--sqlite`: Output path for SQLite database file

**Example**:

```bash
python3 csv-to-sqlite.py --csv ./csv_output --sqlite database.db
```

**Features**:

- Handles SQLite reserved keywords by appending underscores
- Removes "ID of " prefixes from column names
- Creates proper SQLite tables with appropriate data types

### 3. sqlite-to-csv.py

**Purpose**: Converts SQLite database back to CSV files with Soufflé-compatible formatting.

**Usage**:

```bash
python3 sqlite-to-csv.py --sqlite <input_sqlite_file> --output <output_csv_directory>
```

**Options**:

- `--sqlite`: Input SQLite database file
- `--output`: Output directory for CSV files

**Example**:

```bash
python3 sqlite-to-csv.py --sqlite database.db --output ./souffle_csv
```

**Features**:

- Transforms column names to be Soufflé-compatible
- Avoids Soufflé keyword conflicts
- Ensures proper CSV formatting

### 4. csv-to-souffle.py

**Purpose**: Converts CSV files to Soufflé Datalog (.dl) format.

**Usage**:

```bash
python3 csv-to-souffle.py --csv <input_csv_directory> --output <output_dl_file> [--prefix <relation_prefix>]
```

**Options**:

- `--csv`: Input directory containing CSV files
- `--output`: Output .dl file path
- `--prefix`: Optional prefix for all relation names

**Example**:

```bash
python3 csv-to-souffle.py --csv ./csv_output --output program.dl --prefix myapp
```

**Features**:

- Infers column types (symbol, number, float)
- Transforms column names to Soufflé-compatible format
- Handles special character escaping
- Generates both relation declarations and fact data

## Workflow

1. **BQRS to CSV**: Use `bqrs-decoder.py` to convert BQRS files to CSV
2. **CSV to SQLite**: Use `csv-to-sqlite.py` for database storage and querying
3. **SQLite to CSV**: Use `sqlite-to-csv.py` for Soufflé-compatible CSV output
4. **CSV to Soufflé**: Use `csv-to-souffle.py` for Datalog program generation

## Dependencies

- Python 3.x
- CodeQL CLI (for BQRS decoding)
- SQLite3 (included with Python)
- Required Python modules: `sqlite3`, `csv`, `re`, `argparse`, `pathlib`, `logging`

## Data Flow

```
BQRS File → CSV Files → SQLite Database → Soufflé CSV → Soufflé Datalog
          (bqrs-decoder) (csv-to-sqlite) (sqlite-to-csv) (csv-to-souffle)
```

Each script can be used independently or as part of the complete pipeline.

