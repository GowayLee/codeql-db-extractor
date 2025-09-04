(* Type of fileds *)
type field_type =
  | Int
  | String
  | Float
  | Boolean

type table_name = string

type attribute =
  | PrimaryKey of table_name
  | ForeignKey of table_name
  | BasicRef of field_type (* int ref 或 string ref *)

(* Field *)
type field_def =
  { name : string
  ; typ : field_type
  ; attribute : attribute
  }

(* Def of table *)
type table_def =
  { name : table_name
  ; fields : field_def list
  }

type assoc_def =
  { name : table_name
  ; options : table_name list
  }

type scheme_element =
  | Table of table_def
  | Assoc of assoc_def

type scheme =
  { tables : table_def list
  ; assocs : assoc_def list
  }
