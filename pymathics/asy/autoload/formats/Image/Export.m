(* Image Exporter *)

Begin["System`Convert`Image`"]

ImportExport`RegisterExport[
    "PNG",
	System`Convert`Image`ExportToPNG,
        FunctionChannels -> {"FileNames"},
	Options -> {},
	BinaryFormat -> True
];

ImportExport`RegisterExport[
    "JPEG",
	System`Convert`Image`ExportToJPG,
        FunctionChannels -> {"FileNames"},
	Options -> {},
	BinaryFormat -> True
];


End[]
