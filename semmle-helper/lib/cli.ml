type cli_args =
  | FileInput of string
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
  match args with
  | [ _; filename ] ->
    (* We have a filename argument *)
    (match read_file filename with
     | Some content -> FileInput content
     | None -> UsageError)
  | _ :: [] ->
    (* No filename provided *)
    UsageError
  | _ ->
    (* Too many arguments *)
    UsageError
;;

let print_usage () = Printf.eprintf "Usage: semmle-helper <input-file>\n"
