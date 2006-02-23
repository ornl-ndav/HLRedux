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

# Create data source translators for reading in two NeXus files



# Push attributes into SOM1 and SOM2



# Push spectrum into SOM1 and SOM2


if len(SOM1) != len(SOM2):
    raise IndexError, "SOM1 and SOM2 are not the same length!"

# Create SOM3

SOM3 = SOM(len(SOM1))

# Loop on spectrum to do subtraction

for counter in range(len(SOM1)):
    SOM3[counter].x = SOM3[counter].x
    SOM3[counter].y,
    SOM3[counter].y_var = sub_ncerr(SOM1[counter].y, SOM1[counter].y_var,
                                    SOM2[counter].y, SOM2[counter].y_var)
    
# Create output formatting object



# Push attibute object into formatter



# Push SOM3 into into formatter



