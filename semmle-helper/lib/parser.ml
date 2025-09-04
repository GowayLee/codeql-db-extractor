open Angstrom
open Lexer
open Table

(* 注释 *)
let block_comment = string "/*" *> many_till any_char (string "*/")
let line_comment = string "//" *> take_while (fun c -> c <> '\n' && c <> '\r')

(* 主键信息 *)
let keyset = string "#keyset[" *> many_till any_char (char ']')

(* 关联表 *)
let association = char '@' *> identifier *> many_till any_char (char ';')

(* 字段枚举值 *)
let case =
  string "case @" *> identifier *> char '.' *> identifier *> many_till any_char (char ';')
;;

let extended_ws =
  choice
    [ map line_comment ~f:(fun _ -> ())
    ; map block_comment ~f:(fun _ -> ())
    ; map whitespace ~f:(fun _ -> ())
    ]
;;

let ignoreable_element =
  choice
    [ map keyset ~f:(fun _ -> ())
    ; map association ~f:(fun _ -> ())
    ; map case ~f:(fun _ -> ())
    ; map line_comment ~f:(fun _ -> ())
    ; map block_comment ~f:(fun _ -> ())
    ; map whitespace ~f:(fun _ -> ())
    ]
;;

let skip_extended_ws = skip_many extended_ws

(* let skip_ignorable = skip_many ignoreable_element *)
let kw_unique = string "unique" <* skip_extended_ws
let kw_int = string "int" <* skip_extended_ws
let kw_string = string "string" <* skip_extended_ws
let lparen = char '(' <* skip_extended_ws
let rparen = char ')' <* skip_extended_ws
let colon = char ':' <* skip_extended_ws
let semicolon = char ';' <* skip_extended_ws

(* 外键属性：@table ref *)
let foreign_key_attr =
  char '@' *> identifier
  >>= fun ref_table ->
  skip_extended_ws *> string "ref" *> skip_extended_ws *> return (ForeignKey ref_table)
;;

(* 主键属性：@table *)
let primary_key_attr =
  char '@' *> identifier
  >>= fun cur_table -> skip_extended_ws *> return (PrimaryKey cur_table)
;;

(* 基本类型引用属性：int ref 或 string ref *)
let basic_ref_attr =
  kw_int *> skip_extended_ws *> string "ref" *> skip_extended_ws *> return (BasicRef Int)
  <|> kw_string
      *> skip_extended_ws
      *> string "ref"
      *> skip_extended_ws
      *> return (BasicRef String)
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
  >>= (fun _ -> kw_int *> return Int <|> kw_string *> return String)
  >>= fun typ ->
  skip_extended_ws *> identifier
  >>= fun name ->
  colon *> skip_extended_ws *> attribute
  >>= fun attr ->
  Logger.info
    (Printf.sprintf
       "Parsed field: %s of type %s"
       name
       (match typ with
        | Int -> "int"
        | String -> "string"));
  return { name; typ; attribute = attr }
;;

(* 表： 表名(字段1, 字段2, ...); *)
let table =
  identifier
  >>= fun name ->
  Logger.info ("Starting to parse table: " ^ name);
  skip_extended_ws *> lparen *> sep_by (char ',' <* skip_extended_ws) field
  >>= fun fields ->
  Logger.info (Printf.sprintf "Parsed table %s with %d fields" name (List.length fields));
  rparen *> semicolon *> return { name; fields }
;;

(* 最终，一个文件由多张表组成，表之间由任意空白分隔 *)
let file = skip_extended_ws *> sep_by skip_extended_ws table <* skip_extended_ws
