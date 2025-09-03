(* Type of fileds *)
type field_type =
  | Int
  | String

type attribute =
  | ForeignKey of
      { ref_table : string
      ; ref_type : string
      }
    (* @table ref *)
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
