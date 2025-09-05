open Angstrom
open Lexer
open Table

(* foreign key：@table ref *)
let foreign_key_attr =
  at_identifier
  >>= fun ref_table -> skip_ws *> string "ref" *> skip_ws *> return (ForeignKey ref_table)
;;

(* primary key：@table *)
let primary_key_attr =
  at_identifier >>= fun cur_table -> skip_ws *> return (PrimaryKey cur_table)
;;

(* basic ref：int ref / string ref *)
let basic_ref_attr =
  kw_int *> string "ref" *> skip_ws *> return (BasicRef Int)
  <|> kw_string *> string "ref" *> skip_ws *> return (BasicRef String)
  <|> kw_float *> string "ref" *> skip_ws *> return (BasicRef Float)
  <|> kw_boolean *> string "ref" *> skip_ws *> return (BasicRef Boolean)
;;

let attribute =
  choice
    ~failure_msg:"Ilegal field attr"
    [ foreign_key_attr; primary_key_attr; basic_ref_attr ]
;;

(* field_def *)
let field =
  Logger.info "Starting to parse field";
  option false (kw_unique *> return true)
  >>= (fun _ ->
  kw_int *> return Int
  <|> kw_string *> return String
  <|> kw_float *> return Float
  <|> kw_boolean *> return Boolean)
  >>= fun typ ->
  skip_ws *> identifier
  >>= fun name ->
  colon *> attribute
  >>= fun attr ->
  Logger.info
    (Printf.sprintf
       "Parsed field: %s of type %s"
       name
       (match typ with
        | Int -> "int"
        | String -> "string"
        | Float -> "float"
        | Boolean -> "boolean"));
  return { name; typ; attribute = attr }
;;

(* union_def *)
let union =
  at_identifier
  >>= fun name ->
  Logger.info ("Starting to parse union: " ^ name);
  skip_spaces_only *> equal
  >>= fun _ ->
  sep_by1 (skip_ws *> pipe) at_identifier
  >>= (fun options -> block_union_terminator *> return { name; options })
  <|> (sep_by1 (skip_spaces_only *> pipe) at_identifier
       >>= fun options -> line_union_terminator *> return { name; options })
;;

(* enum *)
let enum_item =
  number
  >>= fun id ->
  skip_spaces_only *> equal *> at_identifier >>= fun table -> return { id; table }
;;

let enum =
  kw_case *> at_identifier
  >>= fun table ->
  dot *> identifier
  >>= fun field ->
  skip_spaces_only *> kw_of *> sep_by1 (skip_ws *> pipe) enum_item
  >>= fun items -> block_union_terminator *> return { table; field; items }
;;

(* 表 *)
let table =
  identifier
  >>= fun name ->
  Logger.info ("Starting to parse table: " ^ name);
  skip_ws *> lparen *> sep_by (char ',' <* skip_ws) field
  >>= fun fields ->
  Logger.info (Printf.sprintf "Parsed table %s with %d fields" name (List.length fields));
  rparen *> option false (semicolon *> return true) *> return { name; fields }
;;

let table_element = table >>| fun t -> Table t
let union_element = union >>| fun a -> Union a
let enum_element = enum >>| fun e -> Enum e

let scheme_element =
  skip_ws *> (table_element <|> union_element <|> enum_element) <* skip_ws
;;

let all_elements = many scheme_element

let scheme_parser =
  all_elements
  >>= fun elements ->
  let tables = ref [] in
  let unions = ref [] in
  let enums = ref [] in
  List.iter
    (function
      | Table t -> tables := t :: !tables
      | Union a -> unions := a :: !unions
      | Enum e -> enums := e :: !enums)
    elements;
  return { tables = List.rev !tables; unions = List.rev !unions; enums = List.rev !enums }
;;
