open Semmle_helper.Table
open Semmle_helper.Parser
open Semmle_helper.Cli
open Angstrom

let parse_input input =
  match parse_string ~consume:All scheme_parser input with
  | Ok tables -> tables
  | Error err -> failwith ("Parse error" ^ err)
;;

let print_scheme = function
  | { tables; assocs } ->
    List.iter
      (fun (table : table_def) ->
         Printf.printf "Table: %s\n" table.name;
         List.iter
           (fun field ->
              let attr_str =
                match field.attribute with
                | PrimaryKey tbl -> Printf.sprintf "PK: %s" tbl
                | ForeignKey tbl -> Printf.sprintf "FK: %s" tbl
                | BasicRef Int -> "Basic Reference of Int"
                | BasicRef String -> "Basic Reference of String"
              in
              Printf.printf
                "  Field: %s : %s(%s)\n"
                field.name
                (match field.typ with
                 | Int -> "int"
                 | String -> "string")
                attr_str)
           table.fields;
         print_newline ())
      tables;
    List.iter
      (fun assoc ->
         Printf.printf
           "Association: %s -> [%s]\n"
           assoc.name
           (String.concat "; " assoc.options))
      assocs
;;

let () =
  let input_source = parse_args () in
  match input_source with
  | FileInput content ->
    let scheme = parse_input content in
    print_scheme scheme
  | UsageError ->
    print_usage ();
    exit 1
;;
