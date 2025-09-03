open Semmle_helper.Table
open Semmle_helper.Parser
open Angstrom

let parse_input input =
  match parse_string ~consume:All file input with
  | Ok tables -> tables
  | Error err -> failwith ("Parse error: " ^ err)
;;

let () =
  let example_input =
    "conversionkinds(\n\
    \    unique int expr_id: int ref,\n\
    \    int kind: @cast ref\n\
     );\n\
     is_function_template(unique int id: @function ref);"
  in
  let result = parse_input example_input in
  (* 打印结果 *)
  List.iter
    (fun tbl ->
       Printf.printf "Table: %s\n" tbl.name;
       List.iter
         (fun fld ->
            let attr_info =
              match fld.attributes with
              | [ ForeignKey { ref_table; _ } ] -> Printf.sprintf " (FK: %s)" ref_table
              | [ BasicRef _ ] -> " (Basic Reference)"
              | _ -> " (Unknown attribute)"
            in
            Printf.printf
              "  Field: %s : %s%s\n"
              fld.name
              (match fld.typ with
               | Int -> "int"
               | String -> "string")
              attr_info)
         tbl.fields)
    result
;;
