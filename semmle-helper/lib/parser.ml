open Angstrom
open Lexer
open Table

(* 解析外键属性：@table ref *)
let foreign_key_attr =
  char '@' *> skip_many_whitespace *> identifier
  >>= fun ref_table ->
  skip_many_whitespace
  *> string "ref"
  *> skip_many_whitespace
  *> return (ForeignKey { ref_table; ref_type = ref_table })
;;

(* 解析基本类型引用属性：int ref 或 string ref *)
let basic_ref_attr =
  kw_int *> skip_many_whitespace *> string "ref" *> return (BasicRef Int)
  <|> kw_string *> skip_many_whitespace *> string "ref" *> return (BasicRef String)
;;

(* 解析属性部分 - 可以是外键属性或基本类型引用属性 *)
let attributes = foreign_key_attr <|> basic_ref_attr

(* 解析一个字段定义 *)
let field =
  Logger.info "Starting to parse field";
  option false (kw_unique *> return true)
  >>= (fun _ -> kw_int *> return Int <|> kw_string *> return String)
  >>= fun typ ->
  skip_many_whitespace *> identifier
  >>= fun name ->
  colon *> skip_many_whitespace *> attributes
  >>= fun attr ->
  Logger.info
    (Printf.sprintf
       "Parsed field: %s of type %s"
       name
       (match typ with
        | Int -> "int"
        | String -> "string"));
  return { name; typ; attributes = [ attr ] }
;;

(* 解析一张表： 表名(字段1, 字段2, ...); *)
let table =
  identifier
  >>= fun name ->
  Logger.info ("Starting to parse table: " ^ name);
  skip_many_whitespace *> lparen *> sep_by (char ',' <* skip_many_whitespace) field
  >>= fun fields ->
  Logger.info (Printf.sprintf "Parsed table %s with %d fields" name (List.length fields));
  rparen *> semicolon *> return { name; fields }
;;

(* 最终，一个文件由多张表组成，表之间由任意空白分隔 *)
let file = many (table <* skip_many_whitespace)
