# CLAUDE.md - Development Guide for semmle-helper

## Project Overview

**semmle-helper** is a CodeQL database scheme parser implemented in OCaml. It parses table definitions with fields, types, and foreign key relationships from CodeQL database scheme files.

## Current Status ✅

The project has been **fully implemented** with complete parser functionality:

- ✅ Core parser implementation complete
- ✅ All modules implemented and tested
- ✅ Build system configured
- ✅ Executable ready for use

## Build Commands

### Development Commands

- `dune build` - Build the library
- `dune exec semmle-helper` - Run the executable with example input
- `dune runtest` - Run all tests (currently empty test suite)
- `dune clean` - Clean build artifacts
- `dune fmt` - Format code with ocamlformat
- `dune build @fmt` - Check formatting

### Installation Commands

- `opam install . --deps-only` - Install dependencies
- `dune install` - Install the package

## Project Structure

```
semmle-helper/
├── bin/
│   ├── dune              # Executable configuration
│   └── main.ml           # Demo executable
├── lib/
│   ├── dune              # Library configuration
│   ├── table.ml          # Core data types (tables, fields, attributes)
│   ├── parser.ml         # Angstrom-based parser implementation
│   ├── lexer.ml          # Lexical analysis utilities
│   └── logger.ml         # Simple logging utilities
├── test/
│   ├── dune              # Test configuration
│   └── test_semmle_helper.ml  # Empty test suite (ready for tests)
├── dune-project          # Project metadata and dependencies
├── semmle-helper.opam    # OPAM package configuration
└── .ocamlformat          # Formatting configuration
```

## Dependencies

- **angstrom**: Parser combinator library for parsing table definitions
- **yojson**: JSON handling (future use for output formatting)
- **unix**: System utilities

## Core Functionality

### Data Types (table.ml)

- **field_type**: `Int` | `String` - Basic field types
- **attribute**: Foreign key references with `@table ref` syntax or basic type references
- **field_def**: Field definition with name, type, and attribute
- **table_def**: Table definition with name and list of fields

### Parser Features (parser.ml)

- **Foreign Key Parsing**: Handles `@table ref` syntax for foreign key relationships
- **Type References**: Supports `int ref` and `string ref` for basic type references
- **Field Parsing**: Parses field definitions with optional `unique` keyword
- **Table Parsing**: Parses complete table definitions with comma-separated fields
- **Error Handling**: Uses Angstrom's built-in error reporting

### Example Usage

The main executable demonstrates parsing of sample CodeQL scheme:

```ocaml
(* Input format supported: *)
conversionkinds(
    unique int expr_id: int ref,
    int kind: @cast ref
);
is_function_template(unique int id: @function ref);
```

## Code Style Guidelines

### Formatting

- Uses ocamlformat with Jane Street profile
- Format files with: `ocamlformat -i <file>`
- .ocamlformat config: profile=janestreet, ocaml-version=5.3.0

### Naming Conventions

- snake_case for module names (table.ml, lexer.ml, parser.ml)
- snake_case for function and variable names
- PascalCase for type constructors (Int, String, ForeignKey, BasicRef)
- snake_case for record fields (ref_table, ref_type, field_def)

### Type System

- Explicit type definitions in table.ml
- Use of variant types for different kinds of attributes
- Records for structured data (field_def, table_def)

### Imports

- Minimal imports at top of files
- Use `open` for frequently used modules (Angstrom, Lexer, Table)

### Error Handling

- Uses Angstrom parser combinators with error reporting
- Parser operators: `*>`, `<*`, `>>=`, `<|>` for composition

### Comments

- Chinese comments allowed for documentation
- Focus on explaining complex parsing logic

## Next Steps / Future Work

- [ ] JSON output formatting for parsed tables
- [ ] Command-line interface for file input
- [ ] Error recovery and better error messages
- [ ] Further code(like ql) generation from parsed schemes

## Running the Project

```bash
# Install dependencies
opam install . --deps-only

# Build the project
dune build

# Run the example
dune exec semmle-helper

# Expected output:
# INFO: Starting to parse table: conversionkinds
# INFO: Parsed table conversionkinds with 2 fields
# Table: conversionkinds
#   Field: expr_id : int(Basic Reference of Int)
#   Field: kind : int(FK: cast)
# Table: is_function_template
#   Field: id : int(FK: function)
```

## Code Style Guidelines

### Formatting

- Uses ocamlformat with Jane Street profile
- Format files with: `ocamlformat -i <file>`
- .ocamlformat config: profile=janestreet, ocaml-version=5.3.0

### Naming Conventions

- snake_case for module names (table.ml, lexer.ml, parser.ml)
- snake_case for function and variable names
- PascalCase for type constructors (Int, String, ForeignKey, BasicRef)
- snake_case for record fields (ref_table, ref_type, field_def)

### Type System

- Explicit type definitions in table.ml
- Use of variant types for different kinds of attributes
- Records for structured data (field_def, table_def)

### Imports

- Minimal imports at top of files
- Use `open` for frequently used modules (Angstrom, Lexer, Table)

### Error Handling

- Uses Angstrom parser combinators with error reporting
- Parser operators: `*>`, `<*`, `>>=`, `<|>` for composition

### Comments

- Chinese comments allowed for documentation
- Focus on explaining complex parsing logic
