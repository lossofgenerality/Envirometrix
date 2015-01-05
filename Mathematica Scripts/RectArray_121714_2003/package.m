(*Array index and coordinate functions*)

coordToIndex[{lat_,lon_},{h_,w_},latstart_:-90,latend_:90,lonstart_:-180,lonend_:180,roundDown_:True]:=If[roundDown,Floor,Ceiling]@{Clip[(h Abs[(lat-latstart)/(latend-latstart)]),{1,h}],Clip[(w Abs[(lon-lonstart)/(lonend-lonstart)]),{1,w}]}

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


lonend="41.562500"; totalsize="1000"; latstart="33.912643"; latend="60.648253"; lonstart="-14.617188"; startDateTime="20141118120000"; endDateTime="20141119120000"; datasets="/S1/surfacePrecipitation";streams="GPROF-GMI";
files=Import["http://atmospherics.lossofgenerality.com/data/api/?ids=4&start=20141118120000&end=20141119120000", {"HTML", "Hyperlinks"}];

logstream=OpenWrite[FileNameJoin[{DirectoryName[$InputFileName],"log.txt"}]];
AppendTo[$Output,logstream];
AppendTo[$Echo,logstream];
AppendTo[$Urgent,logstream];
AppendTo[$Messages,logstream];

files=Sort[files];
{latrange,lonrange}=ToExpression[{{latstart,latend},{lonstart,lonend}}];
width=Ceiling[ToExpression[totalsize]];
height=Ceiling[Abs[Differences[latrange][[1]]*ToExpression[totalsize]/Differences[lonrange][[1]]]];
dims={height,width};
datasets=StringSplit[datasets,","];
datasets={"/S1/Latitude","/S1/Longitude",datasets[[1]]};
datetimesets={"/S1/ScanTime/Year","/S1/ScanTime/Month","/S1/ScanTime/DayOfMonth","/S1/ScanTime/Hour","/S1/ScanTime/Minute","/S1/ScanTime/Second"};

LaunchKernels[];
SetSharedVariable[buffer];
buffer=ConstantArray[N[-9999],Join[dims,{9}]];

update[points_]:=Module[{index,buffer2},buffer2=ConstantArray[0,Join[dims,{9}]];
(index=coordToIndex[#[[;;2]],dims,latrange[[1]],latrange[[2]],lonrange[[1]],lonrange[[2]]];
If[DateDifference[Extract[buffer2,index][[-6;;]],#[[-6;;]]]>0,buffer2[[index[[1]],index[[2]]]]=#;];)&/@points;
buffer2]

update2[newbuffer_]:=Module[{temp},temp=Transpose[{buffer,newbuffer},{3,1,2}];
buffer=Map[SortBy[#,(#[[-6;;]])&][[-1]]&,temp,{2}];]

runs=Flatten[ParallelMap[(data=correlateDatasets[#,datasets];
timedata=correlateDatasets[#,datetimesets];
timedata=ConstantArray[#,Dimensions[data][[2]]]&/@timedata;data=Flatten[Transpose[{data,timedata},{3,1,2}],1];
data=Flatten[data,{{1},{2,3}}];
data=DeleteCases[data,x_/;x[[3]]==N[-9999]];
data=geoFilter[latrange,lonrange,data,1,2];
If[Length[data]>0,runlength=Ceiling[Length[data]/$KernelCount];
Partition[data,runlength,runlength,{1,1},{}]])&,files],1];

runs2=DeleteCases[runs,Null];

(*Export["/tmp/tmp.aNBWM3G91s/"<>"1.txt", "Data broken into runs: "<>ToString[Dimensions[runs2]]];*)

runbuffers=ParallelMap[update,runs2];

(*Export["/tmp/tmp.aNBWM3G91s/"<>"2.txt", "Runs compiled into buffers: "<>ToString[Dimensions[runbuffers]]];*)

(*ParallelMap[update2, runbuffers];*)

Clear[bufferlock];
ParallelMap[CriticalSection[{bufferlock}, update2[#]] &, runbuffers];

(*Export["/tmp/tmp.aNBWM3G91s/"<>"3.txt", "run buffers combined "<>ToString[Dimensions[buffer]]];*)

map=(0.5*ImageData[Import["http://naturalearth.springercarto.com/ne3_data/8192/masks/water_8k.png"]]+ImageData[Import["http://naturalearth.springercarto.com/ne3_data/8192/masks/boundaries_8k.png"]]);
submap=Image[arrayCoordRegion[map,latrange,lonrange],ImageSize->Reverse[dims]];

dataArray = Reverse[buffer[[;;,;;,3]]];


overlay=ReliefImage[GaussianFilter[dataArray, 5],ColorFunction->"ThermometerColors",ImageSize->ImageDimensions[submap]];
alpha=Image[Clip[GaussianFilter[dataArray, 5],{0,1}],ImageSize->ImageDimensions[submap]];
mapoverlay=ImageCompose[submap,ImageResize[SetAlphaChannel[overlay,alpha],ImageDimensions[submap]]];

Export["/tmp/tmp.aNBWM3G91s/"<>"mapoverlay.jpg", Column[{Image[mapoverlay,ImageSize->Reverse[dims]],"Latitude range: "<>latstart<>" to "<>latend,"Longitude range: "<>lonstart<>" to "<>lonend,"Start: "<>DateString[parseDate[startDateTime]],"End: "<>DateString[parseDate[endDateTime]],"Dataset: "<>datasets[[3]],"Data streams: "<>streams},Alignment->{Center,Center,Left}]];

Export["/tmp/tmp.aNBWM3G91s/"<>"image.jpg", Column[{ArrayPlot[GaussianFilter[dataArray, 5],ImageSize->Reverse[dims]],"Latitude range: "<>latstart<>" to "<>latend,"Longitude range: "<>lonstart<>" to "<>lonend,"Start: "<>DateString[parseDate[startDateTime]],"End: "<>DateString[parseDate[endDateTime]],"Dataset: "<>datasets[[3]],"Data streams: "<>streams},Alignment->{Center,Center,Left}]];

Export["/tmp/tmp.aNBWM3G91s/"<>"data.h5", Transpose[buffer,{2,3,1}],{"Datasets",Join[datasets,datetimesets]}];

Close[logstream];

(*License: http://www.gnu.org/licenses/old-licenses/gpl-2.0.html*)