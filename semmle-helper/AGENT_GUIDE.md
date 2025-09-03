# CRUSH.md - Development Guide for semmle-helper

## Build Commands

- `dune build` - Build the library
- `dune exec semmle_helper` - Run the executable
- `dune runtest` - Run all tests
- `dune clean` - Clean build artifacts

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

