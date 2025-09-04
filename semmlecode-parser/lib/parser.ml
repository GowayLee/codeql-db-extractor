open Angstrom
open Lexer
open Table

(* 关联表 *)
let association = char '@' *> identifier *> many_till any_char (char ';')

(* 外键属性：@table ref *)
let foreign_key_attr =
  char '@' *> identifier
  >>= fun ref_table -> skip_ws *> string "ref" *> skip_ws *> return (ForeignKey ref_table)
;;

(* 主键属性：@table *)
let primary_key_attr =
  char '@' *> identifier >>= fun cur_table -> skip_ws *> return (PrimaryKey cur_table)
;;

(* 基本类型引用属性：int ref 或 string ref *)
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

(* 字段定义 *)
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

(* 关联 *)
let assoc_option = char '@' *> identifier <* skip_spaces_only

let assoc =
  char '@' *> identifier
  >>= fun name ->
  Logger.info ("Starting to parse association: " ^ name);
  skip_spaces_only *> equal
  >>= fun _ ->
  sep_by1 (skip_ws *> pipe) assoc_option
  >>= (fun options -> block_assoc_terminator *> return { name; options })
  <|> (sep_by1 (skip_spaces_only *> pipe) assoc_option
       >>= fun options -> line_assoc_terminator *> return { name; options })
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
let assoc_element = assoc >>| fun a -> Assoc a
let scheme_element = skip_ws *> (table_element <|> assoc_element) <* skip_ws
let all_elements = many scheme_element

let scheme_parser =
  all_elements
  >>= fun elements ->
  let tables = ref [] in
  let assocs = ref [] in
  List.iter
    (function
      | Table t -> tables := t :: !tables
      | Assoc a -> assocs := a :: !assocs)
    elements;
  return { tables = List.rev !tables; assocs = List.rev !assocs }
;;
