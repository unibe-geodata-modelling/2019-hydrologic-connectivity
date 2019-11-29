# HYDROLOGICAL CONNECTIVITY, 2019

## Summary
We created a toolbox “hydrological connectivity” which includes one script tool. This script tool needs to be saved in the same folder as the toolbox (ESRI, 2016a). The script was written and tested for the version ArcMap 10.6. 

When the script tool is started, the user needs to set a workspace folder, a digital elevation model (DEM) raster and a polygon shape file as input. The input DEM raster will be used as a reference raster. All new calculated raster will have the same extend and cell size.

Starting with connected polygons of any shape, the code calculates how the outflow of a polygon is distributed to his neighbors. It firstly processes the flow direction and flow accumulation. Based on these, two connectivity tables are then calculated. One table summarizes in percent and the other in total cell values, how much water flows from one polygon to the others. These tables are exported in two xls-files. The tables are to read in the way, that the number in the cell is the amount of water which flows from the polygon with the FID in the first column into the polygon with the FID in the first row.

The toolbox can for example be used to calculate the hydrological connectivity between hydrologic response units (HRUs).

## Conditions and restrictions 
By every new run, the old output is overwritten, if this is not desired, ‘overwriteOutput’ should be set to FALSE.

The boarders of the polygon raster are set to the extent of the DEM. This means, if the polygon shape file has a bigger extend, it is cropped. If it’s smaller or irregular shaped, the out-side is treated as one polygon. To shorten the calculation time, it makes sense to use a DEM snipped which isn’t much bigger than the polygon shapefile. 

Cells, which flow out of the raster, are ignored. This means, that there’s only limited information about the polygons at the edge of the raster available.

The polygons and the DEM need to be in the same projection. This is a potential error source, which wasn’t further examined. 

When polygons are not properly connected, the room in between is either seen as a polygon on its own, or if it’s connected to the outside, calculated as the outside polygon. 

## Further explainations
In the document Hydrological_Connectivity_Documentation.pdf you find further information about the code structure and explanations how the code works, as well as an documentation of the development process.

