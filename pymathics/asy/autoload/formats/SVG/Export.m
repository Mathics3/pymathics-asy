(* Text Exporter *)

Begin["System`Convert`TextDump`"]


ImportExport`RegisterExport[
    "SVG",
	System`Convert`TextDump`ExportToSVG,
	FunctionChannels -> {"FileNames"},
        Options -> {System`ByteOrderMark,System`ImageSize},
	DefaultElement -> "Plaintext",
	BinaryFormat -> False
]


End[]
