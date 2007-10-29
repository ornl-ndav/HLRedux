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

def bisect_helper(axis, low_val, high_val):
    """
    This function checks the value against the axis to find the proper bin
    index for the given value in the axis.

    @param axis: The array of values to search
    @type axis: C{nessi_list.NessiList}

    @param low_val: The lower value to search for in axis
    @type low_val: C{float}

    @param high_val: The lower value to search for in axis
    @type high_val: C{float}    


    @return: The index pair in the axis corresponding to the values
    @rtype: C{tuple} of two C{int}s


    @raise TypeError: The axis given is not a C{NessiList}
    """

    try:
        axis.__type__
    except AttributeError:
        raise TypeError("Rebinning axis must be a NessiList!")

    lo_val = float(low_val)
    hi_val = float(high_val)

    # Requested range is off low end of axis
    if lo_val < axis[0] and hi_val < axis[0]:
        return (-1, -1)

    # Requested range is off high end of axis
    if lo_val > axis[-1] and hi_val > axis[-1]:
        return (-1, -1)    

    import bisect

    index_lo_r = bisect.bisect(axis, lo_val)
    index_lo_l = bisect.bisect_left(axis, lo_val)

    index_hi_r = bisect.bisect(axis, hi_val)
    index_hi_l = bisect.bisect_left(axis, hi_val)

    # This quantity is actually the length of the associated value array
    len_axis = len(axis) - 1

    index_l = __fix_index(max(index_lo_r, index_lo_l)-1, len_axis)
    index_r = __fix_index(min(index_hi_r, index_hi_l)-1, len_axis)
                  
    return (index_l, index_r)

def __fix_index(index, end_index):
    """
    This function corrects a given index so that it remains on the correct
    bounds for a histogram value array which is one longer than the
    corresponding axis.

    @param index: The index to possible correct
    @type index: C{int}

    @param end_index: The last index in the value axis
    @type end_index: C{int}


    @return: The corrected index
    @rtype: C{int}
    """
    
    if index == -1:
        return 0
    elif index == end_index:
        return index - 1
    else:
        return index
