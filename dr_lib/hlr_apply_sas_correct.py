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

def apply_sas_correct(obj):
    """
    This function applies the following corrections to SAS TOF data:
      - Multiply counts by pixel radius
      - Multiply counts by TOF^2 (uses bin centers)

    @param obj: The data to apply the corrections to
    @type obj: C{SOM.SOM} or C{SOM.SO}


    @return: The data after corrections have been applied
    @rtype: C{SOM.SOM} or C{SOM.SO}


    @raise TypeError: The object being rebinned is not a C{SOM} or a C{SO}    
    """
    # import the helper functions
    import hlr_utils

    # set up for working through data
    
    o_descr = hlr_utils.get_descr(obj)

    if o_descr == "number" or o_descr == "list":
        raise TypeError("Do not know how to handle given type: %s" % \
                        o_descr)
    else:
        pass

    if o_descr == "SOM":
        inst = obj.attr_list.instrument
    else:
        inst = None
    
    (result, res_descr) = hlr_utils.empty_result(obj)
    
    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)

    # iterate through the values
    import array_manip
    import utils

    import math

    len_obj = hlr_utils.get_length(obj)
    for i in xrange(len_obj):
        val = hlr_utils.get_value(obj, i, o_descr, "y")
        err2 = hlr_utils.get_err2(obj, i, o_descr, "y")
        axis = hlr_utils.get_value(obj, i, o_descr, "x", 0)
        
        #(bin_center, bin_center_err2) = utils.calc_bin_centers(axis)

        #(bin_center2, bin_center2_err2) = array_manip.mult_ncerr(\
        #    bin_center, bin_center_err2, bin_center, bin_center_err2)
        
        map_so = hlr_utils.get_map_so(obj, None, i)

        xpos = hlr_utils.get_parameter("x-offset", map_so, inst)
        ypos = hlr_utils.get_parameter("y-offset", map_so, inst)
        
        radius = math.sqrt(xpos * xpos + ypos * ypos)

        #constant = array_manip.mult_ncerr(bin_center, bin_center_err2,
        #                                  radius, 0.0)

        #constant = array_manip.mult_ncerr(bin_center2, bin_center2_err2,
        #                                  radius, 0.0)
        #constant = array_manip.mult_ncerr(radius, 0.0,
        #                                  bin_center, bin_center_err2)

        #constant = array_manip.div_ncerr(radius, 0.0,
        #                                 bin_center2, bin_center2_err2)

        #value = array_manip.mult_ncerr(val, err2, constant[0], constant[1])
        value = array_manip.mult_ncerr(val, err2, radius, 0.0)
        
        hlr_utils.result_insert(result, res_descr, value, map_so, "y")
    
    return result
