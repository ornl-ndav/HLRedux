###############################################################################
#
# This script is the driver for the Null Integration Test
#
# $Id$
#
###############################################################################

# Import appropriate modules here. NOTE: $PYTHONPATH must reflect where
# modules can be found. Also, no pollution of namespace will be allowed.

import array_manip
import som

# Create data source translators for reading in two NeXus files



# Push attributes into SOM1 and SOM2



# Push spectrum into SOM1 and SOM2


if len(SOM1) != len(SOM2):
    raise IndexError, "SOM1 and SOM2 are not the same length!"

# Create SOM3

SOM3 = som.SOM()

# Loop on spectrum to do subtraction

for (SO1, SO2) in map(None, SOM1, SOM2):
    SO3 = so.SO()
    SO3.x = SO1.x
    SO3.y, SO3.y_var = sub_ncerr(SO1.y, SO1.y_var, SO2.y, SO2.y_var)
    SOM3.append(SO3)
    
# Create output formatting object



# Push attibute object into formatter



# Push SOM3 into into formatter



