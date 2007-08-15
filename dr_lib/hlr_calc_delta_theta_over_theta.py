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

def calc_delta_theta_over_theta(som, dataset_type="data"):
    """
    This function takes a C{SOM} that contains reflectometer slit and angle
    information and calculates the parameter delta theta / theta. The function
    will also store the calculated prameter as well as other slit and angle
    information into the C{SOM}s attribute list. The function will not return
    the C{SOM} as the core data values were not changed.

    @param som: The object that contains the slit and angle information
    @type som: C{SOM.SOM}

    @param dataset_type: The practical name of the dataset being processed.
                         The default value is I{data}.
    @type dataset_type: C{string}


    @raise TypeError: Anything other than a C{SOM} is given
    """
    import hlr_utils
    
    o_descr = hlr_utils.get_descr(som)

    if o_descr != "SOM":
        raise TypeError("Function argument must be a SOM")
    # Have a SOM, go on
    else:
        pass
    
    import math

    # Get slit information
    slit1_top = hlr_utils.get_special("Slit1_top", None)
    slit1_bot = hlr_utils.get_special("Slit1_bottom", None)
    slit1_dist = hlr_utils.get_special("Slit1_distance", None)
    
    slit2_top = hlr_utils.get_special("Slit2_top", None)
    slit2_bot = hlr_utils.get_special("Slit2_bottom", None)    
    slit2_dist = hlr_utils.get_special("Slit2_distance", None)

    # Calculate intermediate slit parameters
    slit1_size = math.fabs(slit1_top - slit1_bot)
    slit2_size = math.fabs(slit2_top - slit2_bot)
    slit12_distance = math.fabs(slit1_dist - slit2_dist)

    # Calculate delta theta
    dtheta = math.max(slit1_size, slit2_size) / slit12_distance


    # Add parameters to attribute list
    som.attr_list[dataset_type+"-slit1_size"] = slit1_size
    som.attr_list[dataset_type+"-slit2_size"] = slit2_size
    som.attr_list[dataset_type+"-slit12_distance"] = slit12_distance
    som.attr_list[dataset_type+"-dtheta"] = dtheta
