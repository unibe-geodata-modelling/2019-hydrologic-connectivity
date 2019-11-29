"""
_________________________________________________________________________
 
 ArcGIS script tool "HydrologicalConnectivity"

 Florian Broghammer & Julia Ryser
 18.10.2019

 Seminar geodata analysis and modelling
 Institute of Geography, Faculty of Science, University of Bern
_________________________________________________________________________

 This script tool calculates, starting with a shapefile of connected polygons
 of any shape and a DEM raster, how the outflow of a polygon is distributed
 to its neighbours. This information is stored in two xlsx-files, which are
 saved in the defined workfolder.
_________________________________________________________________________
"""

#*************************************************************************
# Imports
#*************************************************************************

from __future__ import division
import os
import arcpy
import numpy as np
import math
import pandas as pd
from openpyxl import Workbook

#*************************************************************************
# Set inputs, environment and workspace
#*************************************************************************

myworkspace = arcpy.GetParameterAsText(0)
dem_raster_unfilled = arcpy.GetParameterAsText(1)
polygon_file = arcpy.GetParameterAsText(2)

arcpy.env.workspace = myworkspace
arcpy.env.overwriteOutput = True

# Defines a reference raster for dimensions and cellsize, based on the
# DEM input raster
reference_raster = dem_raster_unfilled
arcpy.env.cellSize = reference_raster
arcpy.env.extent = reference_raster
arcpy.env.snapRaster = reference_raster
arcpy.env.Mask = reference_raster

#*************************************************************************
# This segment defines two functions which analyse how the outflow of each
# polygon is distributed to its neighbours as well as exporting the final  
# tables as easy readable xlsx-files.
#*************************************************************************

# The function 'connectivity_table' caluclates how many cells flow from 
# each polygon in the others and creates an excel-file with the results.
def connectivity_table(ID_polynom, flowdir, flowacc, export_folder):
    dim_columns = ID_polynom.shape[1] - 1  # number of columns
    dim_rows = ID_polynom.shape[0] - 1  # number of rows

    # Creates an empty list and fills it with every new value found
    # in the FID Array and sorts it, starting with the lowest value.
    ID_list = []
    a = 0
    b = 0
    for a in range(dim_rows + 1):
        for b in range(dim_columns + 1):
            if ID_polynom[a][b] not in ID_list:
                ID_list.append(ID_polynom[a][b])
    ID_list.sort()

    # Creates an array with the created list of FIDs as axes.
    dim_table = len(ID_list) + 1
    FID_table = np.zeros([dim_table, dim_table], dtype=np.int)
    FID_table[0][1:dim_table] = ID_list  # creating the x axis, entries are the found FIDs
    FID_table[1:dim_table, 0] = ID_list  # creating the y axis, entries are the found FIDs

	# Reading the flow direction file and saving the designated coordinates as new variables.
    i = 0
    j = 0
    for i in range(dim_rows + 1):
        for j in range(dim_columns + 1):
            if (flowdir[i][j] == 1) and (j < dim_columns):  # cell flows to the right
                i_temp = i
                j_temp = j + 1
            elif (flowdir[i][j] == 2) and ((j < dim_columns) and (i < dim_rows)):  # cell flows right-down
                i_temp = i + 1
                j_temp = j + 1
            elif (flowdir[i][j] == 4) and (i < dim_rows):  # cell flows down
                i_temp = i + 1
                j_temp = j
            elif (flowdir[i][j] == 8) and ((j > 0) and (i < dim_rows)):  # cell flows left-down
                i_temp = i + 1
                j_temp = j - 1
            elif (flowdir[i][j] == 16) and (j > 0):  # cell flows to the left
                i_temp = i
                j_temp = j - 1
            elif (flowdir[i][j] == 32) and ((j > 0) and (i > 0)):  # cell flows up-left
                i_temp = i - 1
                j_temp = j - 1
            elif (flowdir[i][j] == 64) and (i > 0):  # cell flows up
                i_temp = i - 1
                j_temp = j
            elif (flowdir[i][j] == 128) and ((j < dim_columns) and (i > 0)):  # cell flows up-right
                i_temp = i - 1
                j_temp = j + 1
            else:				# cell flows out of the raster. By setting the designated coordinates to 
                i_temp = i		# the current ones it is ensured that no error occures.
                j_temp = j

            # Checking if i,j is at a polygon border. If so, add the value of the flow accumulation 
			# raster of the cell at the border to the already existing value in the FID Table. 
			# The position in the table is the FID of the cell it flows out of on the y-axis and the 
			# FID of the cell it flows into on the x axis.

            if ID_polynom[i][j] != ID_polynom[i_temp][j_temp]:  # checking if the destinated cell has a different FID
                fid_outflow = ID_polynom[i][j]  				# evaluating the FID of the polygon of which the cell flows out of
                fid_inflow = ID_polynom[i_temp][j_temp]  		# evaluating the FID of the polygon the cell flows into

                for x in range(1, dim_table):
                    if FID_table[x][0] == fid_outflow:
                        break
                for y in range(1, dim_table):
                    if FID_table[0][y] == fid_inflow:
                        break

                # Adding the values from the cell under inspection onto those already noted in the table.
                FID_table[x][y] = FID_table[x][y] + (flowacc[i][j] + 1)

    # Exporting the table as an xlsx-file into the workfolder
    df = pd.DataFrame(FID_table)
    filepath = export_folder + "\\PolyToPoly_table_cells.xlsx"
    df.to_excel(filepath, index=False, header=False)

    return (FID_table)
# end of the connectivity table function

# The function 'connectivity_table_percent' creates and exports a similar
# table like the function 'connectivity_table' but calculates precent values
# instead of absolute cell numbers. 
def connectivity_table_percent(FID_table, export_folder2):
    dim_table = len(FID_table[0])
    FID_percent = np.empty([dim_table, dim_table], dtype=float)
    FID_percent[0][1:dim_table] = FID_table[0][1: ]  # creating the x axis, entries are the found FIDs
    FID_percent[1:dim_table, 0] = FID_table[0][1: ]  # creating the y axis, entries are the found FIDs

    i = 1
    j = 1
    for i in range(1, dim_table):
        sumRow = FID_table[i][1:(dim_table)].sum()
        for j in range(1, dim_table):
            FID_percent[i][j] = round(FID_table[i][j] / sumRow, 4)
    FID_percent[0][0] = 0

    # Exporting the table with the percent values as an xlsx-file into the workfolder
    df2 = pd.DataFrame(FID_percent)
    filepath2 = export_folder2 + "\\PolyToPoly_table_percent.xlsx"
    df2.to_excel(filepath2, index=False, header=False)

    return FID_percent
# end of the connectivity table percent function

#*************************************************************************
# ArcGIS Comands
#*************************************************************************

print("Starting with raster calculation.")

# Fill DEM
arcpy.gp.Fill_sa(dem_raster_unfilled, (os.path.join(myworkspace, "dem_raster.tif")), "")
dem_raster = os.path.join(myworkspace, "dem_raster.tif")

# Flow direction
arcpy.gp.FlowDirection_sa(dem_raster, (os.path.join(myworkspace, "flowdir.tif")), "NORMAL", "", "D8")
flowdirection = os.path.join(myworkspace, "flowdir.tif")

# Flow accumulation
arcpy.gp.FlowAccumulation_sa(flowdirection, (os.path.join(myworkspace, "flowacc.tif")), "", "INTEGER")
flowaccumulation = os.path.join(myworkspace, "flowacc.tif")

# Feature to rasters
arcpy.FeatureToRaster_conversion(in_features=polygon_file, field="FID", 
out_raster=(os.path.join(myworkspace, "poly_raster.tif")))

polygon_raster = (os.path.join(myworkspace, "poly_raster.tif"))

# Raster to array
dir_arr = arcpy.RasterToNumPyArray(flowdirection)

accu_arr = arcpy.RasterToNumPyArray(flowaccumulation)

poly_arr = arcpy.RasterToNumPyArray(polygon_raster)

#*************************************************************************
# Applying custom functions
#*************************************************************************

print("Starting with custom functions.")

Polytable = connectivity_table(poly_arr,dir_arr,accu_arr,myworkspace)
Percenttable = connectivity_table_percent(Polytable,myworkspace)

#*************************************************************************
print("Script compiled without error.")