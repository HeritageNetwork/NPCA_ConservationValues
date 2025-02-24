# ---------------------------------------------------------------------------------------------------- #
# * NOTE: Please make a copy of this script before editing and/or running. 
# * This script calculates the total area of each species' binary habitat within a boundary.
# * The default is to loop through all MoBI species to clip the habitat.
#   This can be narrowed down to a specific list of species by changing the text file containing a list of the desired cutecodes under "Create Cutecode List" section
# * NOTE: This needs to be run twice because "picobore" and "ambycing" models don't end in "MOBI"
#   (see If/Else statement that selects species' model)
#   At some point we should fix this - potentially make copies of the final models and rename them.
# * 4 variables need to be updated by the user:
#   1) Boundary: Specified boundary to clip the rasters
#   2) tablepath: output workpace folder for tables
#   3) outTable: output dbf file
#   4) Boundary_field: field of boundary to summarize data
# * Script written by Ellie Linden with help from Tandena Wagner in the summer of 2020
# ---------------------------------------------------------------------------------------------------- #

# Import Modules
import os
import arcpy
from arcpy import env
from arcpy.sa import *
from datetime import datetime

# Set Environments
WS = r"S:\Data\NatureServe\Species_Distributions\MoBI_HabitatModels\spp_models" # Folder containing all species' folders/models
env.workspace = WS
arcpy.env.overwriteOutput = True

# Set Variables
Boundary = r"S:\Projects\NPCA\Data\Intermediate\AviKwaAmeDeepDive.gdb\PADUS_AKA_ProposedNatMon_AnalysisLayer" # UPDATE
tablepath = r"S:\Projects\NPCA\Workspace\Hannah_Hyatt\SpeciesSummaries\Int_ModelTbls_AviKwaAme_NatMon" # UPDATE
outTable = r"MoBIshms_TabAreaMerge_DEriverWatershed" # UPDATE
Boundary_field = "NPCA_Status_GAP_StudyArea" # UPDATE
print("variables and environments set")

# Create Cutecode List
cutecodelist = []
cutecode_file = open(r'S:\Projects\NPCA\Data\SpeciesLists\hypergrid_spslist\AviKwaAme_SpeciesList.txt', 'r') # UPDATE IF NEEDED
for word in cutecode_file:
    word = word.rstrip("\n") # this removes the spaces after each word
    cutecodelist.append(word)
print ("cutecode list created")

# Loop through cutecodes to get rasters and calculate area
i = 1
for i in range(len(cutecodelist)):
    try:
        cutecode = cutecodelist[i]
        srpath = WS + "\\" + cutecode + "\outputs\model_predictions\\"
        filelist = os.listdir(srpath)
        i = 1
        for i in range(len(filelist)):
            if (filelist[i].endswith(('MOBI.tif','binary.tif'))): 
                rastername = filelist[i]

        SpeciesRaster = srpath + rastername

        # Calculate area in meters squared
        area_dbf = tablepath + "\\" + cutecode + "_areatable.dbf"
        TabulateArea(Boundary, Boundary_field, SpeciesRaster, "Value", area_dbf, SpeciesRaster)

        # Add/calculate cutecode field in dbf output
        field = "cutecode"
        expression = str(cutecode)
        print(cutecode)
        arcpy.AddField_management(area_dbf, field, "TEXT")
        arcpy.CalculateField_management(area_dbf, field, '"'+expression+'"',"PYTHON")
        
    except:
        print("model doesn't overlap")

# Merge all output dbfs
env.workspace = tablepath
listTable = arcpy.ListTables()
Areas_merged = outTable
arcpy.Merge_management(listTable, Areas_merged)
print("merge complete")

# join species information
cutecode_crosswalk = r"S:\Projects\_Workspaces\Hannah_Hyatt\MoBI_Gov_Relations\SpeciesLists\CuteCodeCrosswalk.csv"
arcpy.management.JoinField(Areas_merged, "cutecode", cutecode_crosswalk, "cutecode", "Scientific_Name;Common_Name;Rounded_GRank;ESA_Status")
print("Script complete")

