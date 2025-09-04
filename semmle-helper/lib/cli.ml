type cli_args =
  | FileInput of string * bool * string option (* filename * verbose_mode * json_output *)
  | UsageError

let read_file filename =
  try
    let channel = open_in filename in
    let content = really_input_string channel (in_channel_length channel) in
    close_in channel;
    Some content
  with
  | Sys_error msg ->
    Printf.eprintf "Error reading file: %s\n" msg;
    None
  | e ->
    Printf.eprintf "Unexpected error: %s\n" (Printexc.to_string e);
    None
;;

let parse_args () =
  let args = Array.to_list Sys.argv in
  let rec parse_flags flags json_output filename remaining =
    match remaining with
    | [] -> flags, json_output, filename
    | "-v" :: rest -> parse_flags (true :: flags) json_output filename rest
    | "--json" :: output_file :: rest ->
      parse_flags flags (Some output_file) filename rest
    | "--json" :: [] -> parse_flags flags (Some "output.json") filename []
    | flag :: rest when String.starts_with ~prefix:"-" flag ->
      parse_flags flags json_output filename rest
    | fname :: rest -> parse_flags flags json_output (Some fname) rest
  in
  let flags, json_output, filename = parse_flags [] None None args in
  let verbose_mode = List.exists (fun x -> x) flags in
  match filename with
  | Some filename ->
    (match read_file filename with
     | Some content -> FileInput (content, verbose_mode, json_output)
     | None -> UsageError)
  | None -> UsageError
;;

let print_usage () =
  Printf.eprintf "Usage: semmle-helper [OPTIONS] <input-file>\n";
  Printf.eprintf "Options:\n";
  Printf.eprintf "  -v              Verbose mode (show info messages)\n";
  Printf.eprintf "  --json [FILE]   Output JSON to FILE (default: output.json)\n"
;;
