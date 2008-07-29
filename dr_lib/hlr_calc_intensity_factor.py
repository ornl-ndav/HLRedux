#                  High-Level Reduction Functions
#           A part of the SNS Analysis Software Suite.
#
#                  Spallation Neutron Source
#          Oak Ridge National Laboratory, Oak Ridge TN.
#
#
#                             NOTICE
#
# For this software and its associated documentation, permission is granted
# to reproduce, prepare derivative works, and distribute copies to the public
# for any purpose and without fee.
#
# This material was prepared as an account of work sponsored by an agency of
# the United States Government.  Neither the United States Government nor the
# United States Department of Energy, nor any of their employees, makes any
# warranty, express or implied, or assumes any legal liability or
# responsibility for the accuracy, completeness, or usefulness of any
# information, apparatus, product, or process disclosed, or represents that
# its use would not infringe privately owned rights.
#

# $Id$

def calc_intensity_factor(obj):
    """
    This function calculates an intensity factor for each pixel. This is
    accomplished by summing all the data in the incoming object and then
    dividing that into the sum of each pixel individually. Each individual
    factor is also multiplied by the total number of pixels present.

    @param obj: Object containing spectra that will have the intensity factor
                calculated from them.
    @type obj: C{SOM.SOM} or C{SOM.SO}

    
    @return: Object containing the intensity factor
    @rtype: C{SOM.SOM} or C{SOM.SO}
    """
    # import the helper functions
    import hlr_utils

    return obj
