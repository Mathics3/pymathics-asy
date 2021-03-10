(* Image Exporter *)

Begin["System`Convert`Image`"]
Print["register exporters"]
ImportExport`RegisterExport[
    "PNG",
	System`Convert`Image`ExportToPNG,
        FunctionChannels -> {"FileNames"},
	Options -> {"ImageSize"},
	BinaryFormat -> True
];

ImportExport`RegisterExport[
    "JPEG",
	System`Convert`Image`ExportToJPG,
        FunctionChannels -> {"FileNames"},
    Options -> {"ImageSize"},
	BinaryFormat -> True
];


End[]
