open Semmle_helper.Table
open Semmle_helper.Parser
open Semmle_helper.Cli
open Angstrom

let parse_input input =
  match parse_string ~consume:All file input with
  | Ok tables -> tables
  | Error err -> failwith ("Parse error" ^ err)
;;

let print_tables tables =
  List.iter
    (fun tbl ->
       Printf.printf "Table: %s\n" tbl.name;
       List.iter
         (fun fld ->
            let attr_info =
              match fld.attribute with
              | PrimaryKey cur_table -> Printf.sprintf " (PK: %s)" cur_table
              | ForeignKey ref_table -> Printf.sprintf " (FK: %s)" ref_table
              | BasicRef typ ->
                (match typ with
                 | Int -> "(Basic Reference of Int)"
                 | String -> "(Basic Reference of String)")
            in
            Printf.printf
              "  Field: %s : %s%s\n"
              fld.name
              (match fld.typ with
               | Int -> "int"
               | String -> "string")
              attr_info)
         tbl.fields)
    tables
;;

let () =
  let input_source = parse_args () in
  match input_source with
  | FileInput content ->
    let tables = parse_input content in
    print_tables tables
  | UsageError ->
    print_usage ();
    exit 1
;;

