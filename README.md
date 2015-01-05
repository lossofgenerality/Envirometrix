Envirometrix
============

This project provides a framework for collecting atmospheric data from various sources via FTP and analysing them using prebuilt Mathematica scripts on an remote server through a web interface. It utilizes the Django web framework and consists of two main Django apps for data handling and analysis.


The RectArray script compiles the selected data from orbit data into a rectangular array which can be analysed more easily. It also produces a visualization of the data both with and without a background map for geographic context. Below is an example of the output with reference map.

![example image](https://github.com/lossofgenerality/Envirometrix/blob/master/Mathematica%20Scripts/RectArray_121714_2003/mapoverlay.jpg)

The web interface allows access to a constantly updated base of atmospherics data gathered from specified FTP servers. The system supports the use of HDF5 files containing multiple datasets which may be selected from within the interface. In the example below, the data streams listed are from NASA/JAXA.

![interface screencap 1](https://github.com/lossofgenerality/Envirometrix/blob/master/Mathematica%20Scripts/Interface%20Screencaps/mathgui_1.jpg)

Parameters available from the interface can be determined to correspond with variables in each underlying Mathematica script. This includes support for interactively selecting geographic regions through a Google Maps interface.

![interface screencap 2](https://github.com/lossofgenerality/Envirometrix/blob/master/Mathematica%20Scripts/Interface%20Screencaps/mathgui_2.jpg)

Script output is also accessed through an interface

![output screencap](https://github.com/lossofgenerality/Envirometrix/blob/master/Mathematica%20Scripts/Interface%20Screencaps/output_1.jpg)


License:

Copyright 2014-present lossofgenerality.com
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
