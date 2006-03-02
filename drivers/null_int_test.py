#!/usr/bin/env python
###############################################################################
#
# This script is the driver for the Null Integration Test
#
# $Id$
#
###############################################################################

# Import appropriate modules here. NOTE: $PYTHONPATH must reflect where
# modules can be found.

from array_manip import sub_ncerr
import dst_base 
from so import SO
from som import SOM
from sys import argv, exit
from time import localtime, strftime, time

# Read in command line arguments for input file and output file names

try:
    filename_SOM12 = argv[1]
    filename_SOM3 = argv[2]
except IndexError:
    print "Usage:",argv[0],"<input file> <output file>"
    exit(-1)
    
# Create data source translators for reading in two NeXus files

dst1 = dst_base.getInstance("application/x-NeXus", filename_SOM12)
dst2 = dst_base.getInstance("application/x-NeXus", filename_SOM12)

# Retrieve the SOMs from the DSTs

som_id = ("/entry/data", 1)
so_axis = "time_of_flight"
starting_ids = (20, 190)
ending_ids = (30, 250)

SOM1 = dst1.getSOM(som_id, so_axis, start_id=starting_ids, end_id=ending_ids)
SOM2 = dst2.getSOM(som_id, so_axis, start_id=starting_ids, end_id=ending_ids)

if len(SOM1) != len(SOM2):
    raise IndexError, "SOM1 and SOM2 are not the same length!"

# Create SOM3

SOM3 = SOM()

# Add attibutes to SOM3

SOM3.attr_list = SOM1.attr_list
SOM3.attr_list["filename"] = filename_SOM3
SOM3.attr_list["epoch"] = time()
SOM3.attr_list["timestamp"] = strftime("%Y-%m-%d %T",
                                       localtime(SOM3.attr_list["epoch"]))
SOM3.attr_list["parents"] = {"SOM1" : SOM1.attr_list["filename"],
                             "SOM2" : SOM2.attr_list["filename"]}                    
# Loop on spectrum to do subtraction

SOM3.attr_list["operations"] = [("Step 1", "Subtraction (SOM1 - SOM2)")]

for (SO1, SO2) in map(None, SOM1, SOM2):
    SO3 = SO()
    SO3.x = SO1.x
    SO3.id = SO1.id
    SO3.y, SO3.var_y = sub_ncerr(SO1.y, SO1.var_y, SO2.y, SO2.var_y)
    SOM3.append(SO3)

# Create output file object

resource = open(filename_SOM3, "w")
    
# Create output formatting object for 3 column ASCII and pass it a file
# object

a3c = dst_base.getInstance("text/Spec", resource)

# Push SOM3 into output formatter

a3c.writeSOM(SOM3)

# Close resource by issuing release_resource call on formatter

a3c.release_resource()
