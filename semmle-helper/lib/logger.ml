let log message = Printf.printf "%s\n" message
let debug message = log ("DEBUG: " ^ message)
let info message = log ("INFO: " ^ message)
let warning message = log ("WARNING: " ^ message)
let error message = log ("ERROR: " ^ message)

