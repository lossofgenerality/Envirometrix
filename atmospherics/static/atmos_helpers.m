(* ::Package:: *)

BeginPackage["atmospherics`"];


(* Meta functions *)
atmosHelp::usage = "Returns documentation for all functions in atmos_helpers package";

(* Array index and coordinate functions *)
latToIndex::usage = "Given a latitude and the height of an array, returns the vertical index corresponding to the latitude. Rounds down unless otherwise specified";
lonToIndex::usage = "Given a longitude and the width of an array, returns the horizontal index corresponding to the longitude. Rounds down unless otherwise specified";
coordToIndex::usage = "Given a latitude longitude pair and the dimensions of a rectangular array, returns the indices of the cell corresponding to the coordinates";
coordValue::usage = "Given a latitude longitude pair and a rectangular array, gives the array entry value corresponding to the coordinates";
indexToLat::usage = "Given a vertical index and the height of an array, returns the latitude corresponding to the index. Gives latitude at the center of the pixel unless otherwise specified";
indexToLon::usage = "Given a horizontal index and the width of an array, returns the longitude corresponding to the index. Gives longitude at the center of the pixel unless otherwise specified";
indexToCoord::usage = "Given a set of indices and the dimensions of an array, returns the coordinates corresponding to the indices. Gives lon and lat at the center of the pixel unless otherwise specified";
arrayDim::usage = "Given a latitude and longitude range and a spatial resolution (deg per pixel), returns the dimensions of the corresponding rectangular array while accounting for rollover. 
	Note that the units of resolution mean that a higher number indicates a coarser image.";
vRes::usage = "Given a latitude range and the height, in pixels, of an array representing it, returns the vertical resolution of the array in degrees per pixel";
hRes::usage = "Given a longitude range and the width, in pixels, of an array representing it, returns the horizontal resolution of the array in degrees per pixel";
arrayRes::"Given a latitude and longitude range and the dimensions of an array representing them, returns the horizontal and vertical resolution of the array in degrees per pixel";

(* Array and coordinate region functions *)
arrayPixRegion::usage = "Given a rectangular array and ranges in the vertical and horizontal indices, returns the trimmed array while accounting for rollover";
arrayCoordRegion::usage = "Given a rectangular array and latitude and longitude ranges, returns the region of the array corresponding to the specified area while accounting for longitudinal rollover";
inGeoRange::usage = "Given a latitude and longitude range and a list of coordinates, returns whether any of the points lies in the region while accounting for longitudinal rollover";
geoFilter::usage = "Given a latitude and longitude range and a list of data points which include coordinates at the specified index, returns only the data points in the specified geographic area";

(* Datetime functions *)
parseDate::usage = "Given a datetime string such as those given in extra_args, returns the corresponding Mathematica date list";
encodeDate::usage = "Given a Mathemematica date list, returns the corresponding datetime string as accepted by the data api";
inTimeRange::usage = "Given a start date list end date list pair and a list of date lists, retutns whether any of the test dates lie in the given timeframe";
timeFilter::usage = "Given a start date list end date list pair and a list of data points which include a date list at the specified index, returns only the data points in the specified timeframe";

(* Data retrieval functions *)
getDataset::usage = "Given a filepath and the name of a dataset or set of dataset names, returns the contents of that dataset";
annotations::usage = "Given a filepath, returns the annotations, if any, associated with the file";
queryDataAPI::usage = "Given a list of key value pairs, returns the returns the links returned by the corresponding data API query. 
	The keys supported by the api are 'start', 'end', 'ids', 'tag', 'org', and 'set'.";

(* Data transformation functions *)
correlateDatasets::usage = "Given a filepath and a list of dataset names, returns a list of datapoints represented by a list of values from each dataset";
mergeData::usage = "Given a list of filepaths and a list of dataset names, returns a list of datapoints represented by a list of values from each dataset";


Begin["`Private`"];


(* Meta functions*)

atmosHelp[]:= ?atmospherics`*


(* Array index and coordinate functions *)

latToIndex[lat_, h_, latstart_:-90, latend_:90, roundDown_:True]:=Clip[If[roundDown,Floor,Ceiling]@(h Abs[(lat-latstart)/(latend-latstart)]), {1, h}]

lonToIndex[lon_, w_, lonstart_:-180, lonend_:180, roundDown_:True]:=Clip[If[roundDown,Floor,Ceiling]@(w Abs[(lon-lonstart)/(lonend-lonstart)]), {1, w}]

coordToIndex[{lat_, lon_}, {h_,w_}, latstart_:-90, latend_:90, lonstart_:-180, lonend_:180, roundDown_:True]:=If[roundDown,Floor,Ceiling]@{Clip[(h Abs[(lat-latstart)/(latend-latstart)]), {1, h}], Clip[(w Abs[(lon-lonstart)/(lonend-lonstart)]), {1, w}]}

coordValue[{lat_, lon_}, latstart_:-90, latend_:90, lonstart_:-180, lonend_:180, array_]:=Extract[array, coordToIndex[ {lat, lon, latstart, latend, lonstart, lonend}, Dimensions[array][[;;2]] ] ]

indexToLat[index_, h_, horiz_:"center", latstart_:-90, latend_:90]:= Which[
	horiz=="center", (180*(index-.5)/h)-90, 
	horiz=="top", (180*index/h)-90,
	horiz=="bottom", (180*(index-1)/h)-90
]

indexToLon[index_, v_, vert_:"center", lonstart_:-180, lonend_:180]:= Which[
	vert=="center", (360*(index-.5)/v)-180, 
	vert=="left", (360*index/v)-180,
	vert=="right", (360*(index-1)/v)-180
]

indexToCoord[{vindex_, hindex_}, {h_, w_}, horiz_:"center", vert_:"center", latstart_:-90, latend_:90, lonstart_:-180, lonend_:180]:= {indexToLat[vindex, h, horiz], indexToLon[hindex, w, vert]}

arrayDim[{latmin_, latmax_}, {lonmin_, lonmax_}, {hres_, vres_}]:= Block[{height, width},
	height = Ceiling[If[latmin<latmax, (latmax-latmin)/vres, (180-latmax+latmin)/vres]];
	width = Ceiling[If[lonmin<lonmax, (lonmax-lonmin)/vres, (360-lonmax+lonmin)/vres]];
	{height, width}
]

vRes[{latmin_, latmax_}, height_]:= If[latmin<latmax, (latmax - latmin)/height, (180-latmax+latmin)/height]

hRes[{lonmin_, lonmax_}, width_]:= If[lonmin<lonmax, (lonmax - lonmin)/width, (360-lonmax+lonmin)/width]

arrayRes[latrange_, lonrange_, {ArrayHeight_, ArrayWidth_}]:= {vRes[latrange, ArrayHeight], vRes[lonrange, ArrayWidth]}


(* Array and coordinate region functions *)

arrayPixRegion[array_, {vmin_, vmax_}, {hmin_, hmax_}]:= Block[{vregion},
	vregion=If[vmin < vmax, array[[-vmax;;-vmin]], Join[array[[-vmax;;]], array[[;;-vmin]]]];
	If[hmin < hmax, vregion[[;;, hmin;;hmax]], Join[vregion[[;;, hmin;;]],vregion[[;;, ;;hmax]], 2]]
]

arrayCoordRegion[array_, {latmin_, latmax_}, {lonmin_, lonmax_}]:= Block[{vmin, vmax, hmin, hmax},
	{vmin, hmin} = coordToIndex[{latmin, lonmin}, Dimensions[array][[;;2]] ];
	{vmax, hmax} = coordToIndex[{latmax, lonmax}, Dimensions[array][[;;2]] ];
	arrayPixRegion[array, {vmin, vmax}, {hmin, hmax}]
]

inGeoRange[{latmin_, latmax_}, {lonmin_, lonmax_}, coords_]:= Block[{datlatmin, datlatmax, datlonmin, datlonmax},
	{datlatmin, datlatmax} = {Min[coords[[;;, 1]]], Max[coords[[;;, 1]]]};
	{datlonmin, datlonmax} = {Min[coords[[;;, 2]]], Max[coords[[;;, 2]]]};
	And[ (* Data covers both lat and lon of AOI *)
		Or[ (* Data covers lat of AOI *)
			latmin <= datlatmin <= latmax, (* Data intersects North portion of AOI *)
			latmin <= datlatmax <= latmax, (* Data intersects South portion of AOI *)
			datlatmin <= latmin && datlatmax >= latmax (* Data covers all lats of AOI *)
		],
		Or[ (* Data covers lon of AOI *)
			If[ lonmin <= lonmax, 
				Or[ (* If there is no lon rollover *)
					lonmin <= datlonmin <= lonmax, (* Data intersects East portion of AOI *)
					lonmin <= datlonmax <= lonmax, (* Data intersects West portion of AOI *)
					datlonmin <= lonmin && datlonmax >= lonmax (* Data covers all lons of AOI *)
				],
				Or[ (* If there is lon rollover *)
					datlonmin >= lonmin, (* Data lies entirely in East portion of AOI *)
					datlonmax <= lonmax, (* Data lies entirely in West portion of AOI *)
					datlonmin <= lonmax, (* Data intersects West portion of AOI *)
					datlonmax >= lonmin  (* Data intersects East portion of AOI *)
				]
			]
		]
	]
]

geoFilter[{latmin_, latmax_}, {lonmin_, lonmax_}, datapoints_, latindex_, lonindex_]:= 
	Select[datapoints, inGeoRange[{latmin, latmax}, {lonmin, lonmax} ,{{Extract[#, latindex], Extract[#, lonindex]}}]&]


(* Datetime functions *)

parseDate[dateString_]:= DateList[{StringInsert[dateString,"/", {5,7,9,11,13}], {"Year", "Month", "Day", "Hour24", "Minute", "Second"}}]

encodeDate[dateList_]:= DateString[dateList, {"Year", "Month", "Day", "Hour24", "Minute", "Second"}]

inTimeRange[{dateStart_, dateEnd_}, dates_]:= Or @@((DateDifference[dateStart, #]>=0 && DateDifference[#, dateEnd]>=0) &/@ dates)

timeFilter[{dateStart_, dateEnd_}, datapoints_, index_]:= Select[datapoints, inTimeRange[{dateStart, dateEnd}, {Extract[#, index]}]&]


(* Data retrieval functions *)

getDataset[filepath_, dataset_]:= Import[filepath, {"Datasets", dataset}]

annotations[filepath_]:= Import[filepath, "Annotations"]

queryDataAPI[opts_]:= Import["http://atmospherics.lossofgenerality.com/data/api/?"<>StringJoin[#[[1]]<>"="<>#[[2]]<>"&" &/@ opts], {"HTML", "Hyperlinks"}]


(* Data transformation functions *)

correlateDatasets[filepath_, datasets_]:= Block[{array, depth},
	array = getDataset[filepath, #] &/@ datasets;
	depth = ArrayDepth[array];
	Transpose[array, Prepend[Range[depth][[;;-2]], depth]]
]

mergeData[filepaths_, datasets_]:=Join @@ (correlateDatasets[#, datasets]&/@filepaths)


End[];
EndPackage[];



(*Copyright 2014-present lossofgenerality.com*)