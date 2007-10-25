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

def lin_interpolate_spectra(obj, lint_range):
    """
    This function takes spectra and linearly interpolates the spectra between
    the provided range. Values outside the range are left unchanged.
    
    @param obj: The object containing the spectra to be linearly interpolated
    @type obj: C{SOM.SOM}

    @param lint_range: Range pairs where the spectra will be linearly
                       interpolated
    @type lint_range: C{list} of C{tuple}s


    @return: Object containing the linearly interpolated spectra
    @rtype: C{SOM.SOM}


    @raise RuntimeError: If I{obj} and I{lint_range} do not have the same
                         length
    """
    # import the helper functions
    import hlr_utils

    # Kickout if incoming object is NoneType
    if obj is None:
        return obj

    # Length cross-check
    if len(obj) != len(lint_range):
        raise RuntimeError("The SOM and the range pair list must be the same "\
                           +"length")

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj)
    o_descr = hlr_utils.get_descr(obj)

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)

    # iterate through the values
    import bisect

    import nessi_list
    import copy
    for i in xrange(hlr_utils.get_length(obj)):
        map_so = hlr_utils.get_map_so(obj, None, i)

        # Get information from SOM
        y_val = hlr_utils.get_value(obj, i, o_descr, "y")
        y_err2 = hlr_utils.get_err2(obj, i, o_descr, "y")
        x_axis = hlr_utils.get_value(obj, i, o_descr, "x", 0)
        
        y_new = copy.deepcopy(y_val)
        var_y_new = copy.deepcopy(y_err2)

        # Find the bins for the range to linearly interpolate
        i_start = bisect.bisect(x_axis, lint_range[i][0]) - 1
        i_end = bisect.bisect(x_axis, lint_range[i][1]) - 1

        # Calculate slope and offset for line based on range end points
        slope = (y_val[i_end] - y_val[i_start]) / \
                (x_axis[i_end] - x_axis[i_start])
        
        offset = y_val[i_start] - slope * x_axis[i_start]

        for j in xrange(i_start, i_end+1):
            y_new[j] = (slope * x_axis[j]) + offset
            var_y_new[j] = y_err2[i_start]

        hlr_utils.result_insert(result, res_descr, (y_new, var_y_new),
                                map_so, "y")

    return result
