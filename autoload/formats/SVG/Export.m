(* Text Exporter *)

Begin["System`Convert`TextDump`"]


ImportExport`RegisterExport[
    "SVG",
	System`Convert`TextDump`ExportToSVG,
	FunctionChannels -> {"FileNames"},
	Options -> {"ByteOrderMark"},
	DefaultElement -> "Plaintext",
	BinaryFormat -> False
]


End[]
