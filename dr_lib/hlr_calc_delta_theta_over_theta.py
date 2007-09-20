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
    import SOM
    
    o_descr = hlr_utils.get_descr(som)

    if o_descr != "SOM":
        raise TypeError("Function argument must be a SOM")
    # Have a SOM, go on
    else:
        pass
    
    import math

    # Create a dummy SO
    so = SOM.SO()

    # Create a dummy information tuple
    no_info = (None, None, None)

    # Get slit information
    try:
        slit1_top = hlr_utils.get_special(som.attr_list["Slit1_top"], so)
    except KeyError:
        slit1_top = no_info

    try:
        slit1_bot = hlr_utils.get_special(som.attr_list["Slit1_bottom"], so)
    except KeyError:
        slit1_bot = no_info

    try:
        slit1_dist = hlr_utils.get_special(som.attr_list["Slit1_distance"], so)
    except KeyError:
        slit1_dist = no_info

    if slit1_top[0] is None or slit1_bot[0] is None:
        slit1_size_ok = False
    else:
        slit1_size_ok = True

    try:
        slit2_top = hlr_utils.get_special(som.attr_list["Slit2_top"], so)
    except KeyError:
        slit2_top = no_info

    try:
        slit2_bot = hlr_utils.get_special(som.attr_list["Slit2_bottom"], so)
    except KeyError:
        slit2_bot = no_info

    try:
        slit2_dist = hlr_utils.get_special(som.attr_list["Slit2_distance"], so)
    except KeyError:
        slit2_dist = no_info

    if slit2_top[0] is None or slit2_bot[0] is None:
        slit2_size_ok = False
    else:
        slit2_size_ok = True

    if slit1_dist[0] is None or slit2_dist[0] is None:
        slit12_dist_ok = False
    else:
        slit12_dist_ok = True

    # Unit checks
    if slit1_size_ok and slit2_size_ok:
        if slit1_top[2] != slit2_top[2]:
            raise ValueError("Slit top opening distances are not in the same "\
                             +"units. slit1 (%s), slit2 (%s)" % (slit1_top[2],
                                                                 slit2_top[2]))

        if slit1_bot[2] != slit2_bot[2]:
            raise ValueError("Slit bottom opening distances are not in the "\
                             +"same units. slit1 (%s), slit2 (%s)" \
                             % (slit1_bot[2],
                                slit2_bot[2]))    
            
    if slit1_dist[2] != slit2_dist[2] and slit12_dist_ok:
        raise ValueError("Slit distances are not in the same units. "\
                         +"slit1 (%s), slit2 (%s)" % (slit1_dist[2],
                                                      slit2_dist[2]))

    # Calculate intermediate slit parameters
    if slit1_size_ok:
        slit1_size = math.fabs(slit1_top[0] - slit1_bot[0])
        if slit1_top[2] == "millimetre":
            slit1_size /= 1000.0
            slit1_size_units = "metre"
        else:
            slit1_size_units = slit1_top[2]
    else:
        slit1_size = float('nan')
        slit1_size_units = None

    if slit2_size_ok:
        slit2_size = math.fabs(slit2_top[0] - slit2_bot[0])
        if slit2_top[2] == "millimetre":
            slit2_size /= 1000.0
            slit2_size_units = "metre"
        else:
            slit2_size_units = slit2_top[2]
    else:
        slit2_size = float('nan')
        slit2_size_units = None

    if slit12_dist_ok:
        slit12_distance = math.fabs(slit1_dist[0] - slit2_dist[0])
    else:
        slit12_distance = float('nan')

    # Calculate delta theta
    if slit1_size_ok and not slit2_size_ok:
        dtheta = slit1_size / slit12_distance
    elif slit2_size_ok and not slit1_size_ok:
        dtheta = slit2_size / slit12_distance
    else:
        dtheta = max(slit1_size, slit2_size) / slit12_distance

    # Calculate delta theta over theta
    try:
        theta = hlr_utils.get_special(som.attr_list["Theta"], so)
    except KeyError:
        theta = no_info

    if theta[0] is not None:
        if theta[2] == "degrees" or theta[2] == "degree":
            theta_rads = theta[0] * (math.pi / 180.0)
        else:
            theta_rads = theta[0]
    else:
        theta_rads = float('nan')
    
    dtheta_over_theta = dtheta / theta_rads

    # Add parameters to attribute list
    som.attr_list[dataset_type+"-slit1_size"] = (slit1_size, slit1_size_units)
    som.attr_list[dataset_type+"-slit2_size"] = (slit2_size, slit2_size_units)
    som.attr_list[dataset_type+"-slit12_distance"] = (slit12_distance,
                                                      slit1_dist[2])
    som.attr_list[dataset_type+"-delta_theta"] = (dtheta, "radians")
    som.attr_list[dataset_type+"-theta"] = (theta_rads, "radians")
    som.attr_list[dataset_type+"-dtheta_over_theta"] = dtheta_over_theta
    
