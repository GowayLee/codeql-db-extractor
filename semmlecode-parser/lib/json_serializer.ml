open Yojson.Safe
open Table

(* JSON serialization functions *)
let field_type_to_json = function
  | Int -> `String "int"
  | String -> `String "string"
  | Float -> `String "float"
  | Boolean -> `String "boolean"
;;

let attribute_to_json = function
  | PrimaryKey table_name ->
    `Assoc [ "type", `String "primary_key"; "table", `String table_name ]
  | ForeignKey table_name ->
    `Assoc [ "type", `String "foreign_key"; "table", `String table_name ]
  | BasicRef field_type ->
    `Assoc [ "type", `String "basic_ref"; "field_type", field_type_to_json field_type ]
;;

let field_def_to_json (field : field_def) =
  `Assoc
    [ "name", `String field.name
    ; "type", field_type_to_json field.typ
    ; "attribute", attribute_to_json field.attribute
    ]
;;

let table_def_to_json (table : table_def) =
  `Assoc
    [ "name", `String table.name
    ; "fields", `List (List.map field_def_to_json table.fields)
    ]
;;

let assoc_def_to_json assoc =
  `Assoc
    [ "name", `String assoc.name
    ; "options", `List (List.map (fun opt -> `String opt) assoc.options)
    ]
;;

let scheme_to_json scheme =
  `Assoc
    [ "tables", `List (List.map table_def_to_json scheme.tables)
    ; "associations", `List (List.map assoc_def_to_json scheme.assocs)
    ]
;;

let write_scheme_to_file scheme filename =
  let json = scheme_to_json scheme in
  let channel = open_out filename in
  to_channel channel json;
  close_out channel
;;
