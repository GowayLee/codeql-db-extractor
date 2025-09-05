(* Type of fileds *)
type field_type =
  | Int
  | String
  | Float
  | Boolean

type table_name = string
type field_name = string

type attribute =
  | PrimaryKey of table_name
  | ForeignKey of table_name
  | BasicRef of field_type (* int ref 或 string ref *)

(* Field *)
type field_def =
  { name : field_name
  ; typ : field_type
  ; attribute : attribute
  }

(* Def of table *)
type table_def =
  { name : table_name
  ; fields : field_def list
  }

(* Def of union *)
type union_def =
  { name : table_name
  ; options : table_name list
  }

type enum_item =
  { id : string
  ; table : table_name
  }

type enum_def =
  { table : table_name
  ; field : field_name
  ; items : enum_item list
  }

type scheme_element =
  | Table of table_def
  | Union of union_def
  | Enum of enum_def

type scheme =
  { tables : table_def list
  ; unions : union_def list
  ; enums : enum_def list
  }
