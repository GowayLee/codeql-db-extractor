open Angstrom

let ws = function
  | ' ' | '\t' | '\n' | '\r' -> true
  | _ -> false
;;

let whitespace = take_while1 ws
let skip_many_whitespace = skip_while ws

let is_identifier_char c =
  match c with
  | 'a' .. 'z' | 'A' .. 'Z' | '0' .. '9' | '_' -> true
  | _ -> false
;;

let identifier =
  take_while1 is_identifier_char
  >>= fun first_char -> take_while is_identifier_char >>| fun rest -> first_char ^ rest
;;

let kw_unique = string "unique" <* skip_many_whitespace
let kw_int = string "int" <* skip_many_whitespace
let kw_string = string "string" <* skip_many_whitespace
let lparen = char '(' <* skip_many_whitespace
let rparen = char ')' <* skip_many_whitespace
let colon = char ':' <* skip_many_whitespace
let semicolon = char ';' <* skip_many_whitespace
