#!/usr/bin/env python3
"""
QL Code Generator for CodeQL Database Schema

This script reads a JSON file containing database schema information and generates
QL class definitions for extracting database information.
"""

import json
import argparse
import sys
from typing import List, Set, Dict, Any

# CodeQL reserved words that need special handling
CODEQL_RESERVED_WORDS = {
    "true", "false", "from", "super", "result", "import", "module", "class",
    "predicate", "query", "extends", "where", "select", "order", "by", "asc",
    "desc", "and", "or", "not", "exists", "forall", "if", "then", "else",
    "in", "instanceof", "this", "none"
}


def sanitize_identifier(name: str) -> str:
    """
    Sanitize an identifier by applying transformation rules:
    1. Convert to lowercase if it contains capital characters
    2. Add underscore prefix if it's a CodeQL reserved word
    """
    # Rule 1: Convert to lowercase if it contains capital characters
    if any(c.isupper() for c in name):
        name = name.lower()

    # Rule 3: Add underscore if it's a reserved word
    if name.lower() in CODEQL_RESERVED_WORDS:
        name = f"{name}_"

    return name


def extract_table_names_from_tables(tables_data: List[Dict[str, Any]]) -> Set[str]:
    """
    Extract table names from the tables section of the JSON.

    Looks for fields with "type": "primary_key" or "foreign_key" attribute and extracts the table name.
    """
    table_names = set()

    for table in tables_data:
        for field in table.get("fields", []):
            attribute = field.get("attribute", {})
            if attribute.get("type") == "primary_key" or attribute.get("type") == "foreign_key":
                table_names.add(attribute["table"])

    return table_names


def extract_table_names_from_unions(unions_data: List[Dict[str, Any]]) -> Set[str]:
    """
    Extract table names from the unions section of the JSON.

    Extracts union names and all options which represent table names.
    """
    table_names = set()

    for union in unions_data:
        table_names.add(union["name"])
        # Add all options from the union
        for option in union.get("options", []):
            table_names.add(option)

    return table_names

def extract_table_names_from_enums(enums_data: List[Dict[str, Any]]) -> Set[str]:
    """
    Extract table names from the enums section of the JSON.

    Extracts table names from enum definitions and their items.
    """
    table_names = set()

    for enum in enums_data:
        # Add the main table name from the enum
        table_names.add(enum["table"])

        # Add all table names from the items list
        for item in enum.get("items", []):
            table_names.add(item["table"])

    return table_names

def prune_tables(all_table_names: Set[str], ref_table_names: Set[str]) -> Set[str]:
    """
    Prune table names by applying filtering rules and display statistics.

    Rules:
    1. Only keep tables that exist in ref_table_names
    2. Remove duplicate tables (already handled by set operations)

    Returns the pruned set of table names.
    """
    # Display initial statistics
    print(f"Initial table count: {len(all_table_names)}", file=sys.stderr)
    print(f"Reference table count: {len(ref_table_names)}", file=sys.stderr)

    # Calculate missing tables in all_table_names with respect to ref_table_names
    missing_in_all = ref_table_names - all_table_names
    print(f"Missing tables in all_table_names: {len(missing_in_all)}", file=sys.stderr)
    if missing_in_all:
        print(f"Missing tables: {sorted(missing_in_all)}", file=sys.stderr)

    pruned_tables = all_table_names.intersection(ref_table_names)

    # Display pruning statistics
    removed_count = len(all_table_names) - len(pruned_tables)
    print(f"Tables removed: {removed_count}", file=sys.stderr)
    print(f"Final table count: {len(pruned_tables)}", file=sys.stderr)

    return pruned_tables



def generate_ql_classes(table_names: Set[str]) -> str:
    """
    Generate QL class definitions for each table name.

    Format: class DB_<table_name> extends @<table_name> { string toString() { result = "DB_<table_name>" } }
    """
    ql_code = []

    for table_name in sorted(table_names):
        class_name = f"DB_{table_name}"
        ql_class = f"class {class_name} extends @{table_name} {{\n  string toString() {{ result = \"{class_name}\" }}\n}}"
        ql_code.append(ql_class)

    return "\n\n".join(ql_code)


def generate_query_predicates(tables_data: List[Dict[str, Any]]) -> str:
    """
    Generate query predicates for each table.

    Format: query predicate get_<table_name>(<arg_types> <arg_names>) { <table_name>(<arg_names>) }
    """
    query_code = []

    for table in tables_data:
        table_name = table["name"]
        fields = table.get("fields", [])

        args = []
        param_names = []

        for field in fields:
            field_name = field["name"]
            attribute = field.get("attribute", {})
            attr_type = attribute.get("type")

            if attr_type in ["foreign_key", "primary_key"]:
                # Use DB_<table> for foreign/primary keys
                arg_type = f"DB_{attribute['table']}"
            elif attr_type == "basic_ref":
                # Use the field_type for basic_ref
                arg_type = attribute["field_type"]
            else:
                # Fallback to field type if attribute type is unknown
                arg_type = field["type"]

            args.append(f"{arg_type} {field_name}")
            param_names.append(field_name)

        # Apply transformation rules
        # Rule 1: Lowercase predicate name if it contains capital characters
        query_name = f"get_{sanitize_identifier(table_name)}"

        # Rule 2: Lowercase arg_names if they contain capital characters
        # Rule 3: Handle reserved words in arg_names
        sanitized_args = []
        sanitized_param_names = []

        for arg in args:
            # Split arg into type and name
            if " " in arg:
                arg_type, arg_name = arg.split(" ", 1)
                sanitized_name = sanitize_identifier(arg_name)
                sanitized_args.append(f"{arg_type} {sanitized_name}")
                sanitized_param_names.append(sanitized_name)
            else:
                # Handle case where arg doesn't have a space (shouldn't happen)
                sanitized_args.append(arg)
                sanitized_param_names.append(arg)

        args_str = ", ".join(sanitized_args)
        params_str = ", ".join(sanitized_param_names)

        query_predicate = f"query predicate {query_name}({args_str}) {{\n  {table_name}({params_str})\n}}"
        query_code.append(query_predicate)

    return "\n\n".join(query_code)


def main():
    """Main function to orchestrate the QL code generation process."""
    parser = argparse.ArgumentParser(description="Generate QL code from database schema JSON")
    parser.add_argument("input_file", help="Input JSON file containing schema information")
    parser.add_argument("-o", "--output", help="Output QL file (default: stdout)")

    args = parser.parse_args()

    try:
        # Read and parse JSON file
        with open(args.input_file, 'r') as f:
            data = json.load(f)

        # Extract table names from all sections
        tables = data.get("tables", [])
        unions = data.get("unions", [])
        enums = data.get("enums", [])

        table_names_from_tables = extract_table_names_from_tables(tables)
        table_names_from_unions = extract_table_names_from_unions(unions)
        table_names_from_enums = extract_table_names_from_enums(enums)

        # Combine and deduplicate table names
        all_table_names = table_names_from_tables.union(table_names_from_unions).union(table_names_from_enums)

        if not all_table_names:
            print("No table names found in the input JSON.", file=sys.stderr)
            sys.exit(1)

        pruned_tables = prune_tables(all_table_names, table_names_from_tables)

        # Generate QL code
        ql_classes = generate_ql_classes(pruned_tables)
        query_predicates = generate_query_predicates(tables)

        # Combine both outputs
        full_output = ql_classes + "\n\n" + query_predicates

        # Write output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(full_output)
            print(f"QL code generated successfully: {args.output}")
        else:
            print(full_output)

    except FileNotFoundError:
        print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in '{args.input_file}': {e}", file=sys.stderr)
        sys.exit(1)
    except KeyError as e:
        print(f"Error: Missing required field in JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
