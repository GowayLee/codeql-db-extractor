open Angstrom

(* comment *)
let block_comment = string "/*" *> many_till any_char (string "*/")
let line_comment = string "//" *> take_while (fun c -> c <> '\n' && c <> '\r')

(* identifier *)
let is_identifier_char c =
  match c with
  | 'a' .. 'z' | 'A' .. 'Z' | '0' .. '9' | '_' -> true
  | _ -> false
;;

let identifier =
  take_while1 is_identifier_char
  >>= fun first_char -> take_while is_identifier_char >>| fun rest -> first_char ^ rest
;;

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

(* keyset *)
let keyset = string "#keyset[" *> many_till any_char (char ']')

(* skip *)
let skip_ws =
  skip_many
    (choice
       [ map line_comment ~f:(fun _ -> ())
       ; map block_comment ~f:(fun _ -> ())
       ; map whitespace ~f:(fun _ -> ())
       ; map keyset ~f:(fun _ -> ())
       ])
;;

let skip_spaces_only =
  skip_many
    (choice
       [ map line_comment ~f:(fun _ -> ())
       ; map block_comment ~f:(fun _ -> ())
       ; map space ~f:(fun _ -> ())
       ; map keyset ~f:(fun _ -> ())
       ])
;;

let kw_unique = string "unique" <* skip_ws
let kw_int = string "int" <* skip_ws
let kw_string = string "string" <* skip_ws
let kw_float = string "float" <* skip_ws
let kw_boolean = string "boolean" <* skip_ws
let lparen = char '(' <* skip_ws
let rparen = char ')' <* skip_ws
let colon = skip_ws *> char ':' <* skip_ws
let semicolon = char ';' <* skip_ws
let at = char '@'
let dot = char '.'

(* union related lex *)
let equal = char '=' <* skip_spaces_only
let pipe = char '|' <* skip_spaces_only
let at_identifier = at *> identifier <* skip_spaces_only

let line_union_terminator =
  char ';' *> skip_ws *> return ()
  <|> end_of_line *> skip_ws *> return ()
  <|> end_of_input *> return ()
;;

let block_union_terminator =
  char ';' *> skip_ws *> return ()
  <|> skip_ws *> char ';' *> skip_ws *> return ()
  <|> end_of_input *> return ()
;;

(* enum related lex *)
let kw_case = string "case" <* skip_ws
let kw_of = string "of" <* skip_ws

let number =
  take_while1 (function
    | '0' .. '9' -> true
    | _ -> false)
;;
