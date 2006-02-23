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
from dst_base import DST_BASE
from so import SO
from som import SOM

filename_SOM3 = "stuff1.dat"

# Create data source translators for reading in two NeXus files



# Push attributes into SOM1 and SOM2



# Push spectrum into SOM1 and SOM2


if len(SOM1) != len(SOM2):
    raise IndexError, "SOM1 and SOM2 are not the same length!"

# Create SOM3

SOM3 = SOM()
SOM3.attr_list = SOM1.attr_list
SOM3.attr_list["filename"] = filename_SOM3
SOM3.attr_list["parents"] = {"SOM1" : SOM1.attr_list["filename"],
                             "SOM2" : SOM2.attr_list["filename"]}                    
# Loop on spectrum to do subtraction

SOM3.attr_list["operations"] = {"Step 1" : "Subtraction (SOM1 - SOM2)"}

for (SO1, SO2) in map(None, SOM1, SOM2):
    SO3 = so.SO()
    SO3.x = SO1.x
    SO3.y, SO3.y_var = sub_ncerr(SO1.y, SO1.y_var, SO2.y, SO2.y_var)
    SOM3.append(SO3)
    
# Create output formatting object for 3 column ASCII

a3c = DST_BASE.getInstance("text/Spec", resource)

# Push SOM3 into output formatter

a3c.write(SOM3,args)

