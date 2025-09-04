(* Type of fileds *)
type field_type =
  | Int
  | String

type attribute =
  | PrimaryKey of string
  | ForeignKey of string
  | BasicRef of field_type (* int ref 或 string ref *)

(* Field *)
type field_def =
  { name : string
  ; typ : field_type
  ; attribute : attribute
  }

(* Def of table *)
type table_def =
  { name : string
  ; fields : field_def list
  }
