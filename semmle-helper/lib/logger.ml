let quiet_mode = ref false

let set_quiet quiet = quiet_mode := quiet

let log message = if not !quiet_mode then Printf.printf "%s\n" message
let debug message = log ("DEBUG: " ^ message)
let info message = log ("INFO: " ^ message)
let warning message = log ("WARNING: " ^ message)
let error message = log ("ERROR: " ^ message)
