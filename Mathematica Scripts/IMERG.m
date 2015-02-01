(* ::Package:: *)

(*Array index and coordinate functions*)coordToIndex[{lat_,lon_},{h_,w_},latstart_:-90,latend_:90,lonstart_:-180,lonend_:180,roundDown_:True]:=If[roundDown,Floor,Ceiling]@{Clip[(h Abs[(lat-latstart)/(latend-latstart)]),{1,h}],Clip[(w Abs[(lon-lonstart)/(lonend-lonstart)]),{1,w}]}

(*Array and coordinate region functions*)

arrayPixRegion[array_,{vmin_,vmax_},{hmin_,hmax_}]:=Block[{vregion},vregion=If[vmin<vmax,array[[-vmax;;-vmin]],Join[array[[-vmax;;]],array[[;;-vmin]]]];
If[hmin<hmax,vregion[[;;,hmin;;hmax]],Join[vregion[[;;,hmin;;]],vregion[[;;, ;;hmax]],2]]]

arrayCoordRegion[array_,{latmin_,latmax_},{lonmin_,lonmax_}]:=Block[{vmin,vmax,hmin,hmax},{vmin,hmin}=coordToIndex[{latmin,lonmin},Dimensions[array][[;;2]]];
{vmax,hmax}=coordToIndex[{latmax,lonmax},Dimensions[array][[;;2]]];
arrayPixRegion[array,{vmin,vmax},{hmin,hmax}]]

geoFilter[{latmin_,latmax_},{lonmin_,lonmax_},datapoints_,latindex_,lonindex_]:=Select[datapoints,And[latmin<=Extract[#,latindex]<=latmax,If[lonmin<lonmax,lonmin<=Extract[#,lonindex]<=lonmax,Or[Extract[#,lonindex]<=lonmin,lonmax<=Extract[#,lonindex]]]]&]

(*Datetime functions*)

parseDate[dateString_]:=DateList[{StringInsert[dateString,"/",{5,7,9,11,13}],{"Year","Month","Day","Hour24","Minute","Second"}}]

(*Data retrieval functions*)

getDataset[filepath_,dataset_]:=Import[filepath,{"Datasets",dataset}]

(*Data transformation functions*)

correlateDatasets[filepath_,datasets_]:=Block[{array,depth},array=Map[getDataset[filepath,#]&,datasets];
depth=ArrayDepth[array];
Transpose[array,Prepend[Range[depth][[;;-2]],depth]]]

{extra_args}
files = {data};

files = Sort[files];
{latrange, lonrange} = 
  ToExpression[{{latStart, latEnd}, {lonStart, lonEnd}}];
datasets = StringSplit[datasets, ","];
dataset = datasets[[1]];

images = Map[
	Image[arrayCoordRegion[Transpose[getDataset[#, dataset]], latrange, lonrange],
	ImageSize -> Large
]&, files];

man = Manipulate[
	Column[{
		images[[file]],
		"File name: " <> FileNameSplit[files[[file]]][[-1]],
		"Latitude range: " <> latStart <> " to " <> latEnd, 
		"Longitude range: " <> lonStart <> " to " <> lonEnd,
		"Start: " <> DateString[parseDate[startDateTime]],
		"End: " <> DateString[parseDate[endDateTime]],
		"Dataset: " <> dataset,
		"Data streams: " <> streams
	}, Alignment -> Center],
{file, 1, Length[files], 1}, SaveDefinitions->True];

UsingFrontEnd@Export["images.cdf", DocumentNotebook[{man}]];
