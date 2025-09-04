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


def extract_table_names_from_tables(tables_data: List[Dict[str, Any]]) -> Set[str]:
    """
    Extract table names from the tables section of the JSON.

    Looks for fields with "type": "primary_key" attribute and extracts the table name.
    """
    table_names = set()

    for table in tables_data:
        for field in table.get("fields", []):
            attribute = field.get("attribute", {})
            if attribute.get("type") == "primary_key":
                table_names.add(attribute["table"])

    return table_names


def extract_table_names_from_associations(associations_data: List[Dict[str, Any]]) -> Set[str]:
    """
    Extract table names from the associations section of the JSON.

    Extracts all association names which represent table names.
    """
    return {assoc["name"] for assoc in associations_data}


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

        # Generate the query predicate
        query_name = f"get_{table_name}"
        args_str = ", ".join(args)
        params_str = ", ".join(param_names)

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

        # Extract table names from both sections
        tables = data.get("tables", [])
        associations = data.get("associations", [])

        table_names_from_tables = extract_table_names_from_tables(tables)
        table_names_from_associations = extract_table_names_from_associations(associations)

        # Combine and deduplicate table names
        all_table_names = table_names_from_tables.union(table_names_from_associations)

        if not all_table_names:
            print("No table names found in the input JSON.", file=sys.stderr)
            sys.exit(1)

        # Generate QL code
        ql_classes = generate_ql_classes(all_table_names)
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
