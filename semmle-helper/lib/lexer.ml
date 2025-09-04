open Angstrom

(* 注释 *)
let block_comment = string "/*" *> many_till any_char (string "*/")
let line_comment = string "//" *> take_while (fun c -> c <> '\n' && c <> '\r')

let whitespace =
  take_while1 (function
    | ' ' | '\t' | '\n' | '\r' -> true
    | _ -> false)
;;

let space =
  take_while1 (function
    | ' ' | '\t' -> true
    | _ -> false)
;;

let skip_ws =
  skip_many
    (choice
       [ map line_comment ~f:(fun _ -> ())
       ; map block_comment ~f:(fun _ -> ())
       ; map whitespace ~f:(fun _ -> ())
       ])
;;

let skip_spaces_only =
  skip_many
    (choice
       [ map line_comment ~f:(fun _ -> ())
       ; map block_comment ~f:(fun _ -> ())
       ; map space ~f:(fun _ -> ())
       ])
;;

let is_identifier_char c =
  match c with
  | 'a' .. 'z' | 'A' .. 'Z' | '0' .. '9' | '_' -> true
  | _ -> false
;;

let identifier =
  take_while1 is_identifier_char
  >>= fun first_char -> take_while is_identifier_char >>| fun rest -> first_char ^ rest
;;

let kw_unique = string "unique" <* skip_ws
let kw_int = string "int" <* skip_ws
let kw_string = string "string" <* skip_ws
let lparen = char '(' <* skip_ws
let rparen = char ')' <* skip_ws
let colon = skip_ws *> char ':' <* skip_ws
let semicolon = char ';' <* skip_ws

(* assoc rerelated lex *)
let equal = char '=' <* skip_spaces_only
let pipe = char '|' <* skip_spaces_only

let line_assoc_terminator =
  char ';' *> skip_ws *> return ()
  <|> end_of_line *> skip_ws *> return ()
  <|> end_of_input *> return ()
;;

let block_assoc_terminator =
  char ';' *> skip_ws *> return ()
  <|> skip_ws *> char ';' *> skip_ws *> return ()
  <|> end_of_input *> return ()
;;
