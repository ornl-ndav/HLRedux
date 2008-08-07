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

def create_axis_from_data(obj, **kwargs):
    """
    This function inspects the independent axis of the data searching for the
    minimum and maximum axis values. It also determines the bin width from
    the first bin in the axis and searches for the smallest value. From these
    values, an Axis object is created. This function assusmes that the axis is
    sorted in ascending order.

    @param obj: The object containing the data with the indpendent axis to be
    searched.
    @type obj: C{SOM.SOM} or C{SOM.SO}

    @param kwargs: A list of keyword arguments that the function accepts:

    @keyword axis_pos: This is position of the axis in the axis array. If no
                       argument is given, the default value is 0
    @type axis_pos: C{int}

    @keyword width: A override parameter for specifying the axis bin width.
    @type width: C{float}


    @return: The axis based on the found values from the data
    @rtype: L{hlr_utils.Axis}


    @raise TypeError: The incoming object is not a C{SOM} or a C{SO}
    """
    import hlr_utils

    # Check for keyword arguments
    try:
        axis_pos = kwargs["axis_pos"]
    except KeyError:
        axis_pos = 0

    try:
        axis_width = kwargs["width"]
        width_given = True
    except KeyError:
        axis_width = 999999999999999999999999999999999999.0
        width_given = False

    o_descr = hlr_utils.get_descr(obj)

    if o_descr == "number" or o_descr == "list":
        raise TypeError("Function argument must be a SOM or a SO")
    # Have a SOM or a SO, go on
    else:
        pass

    # Set extreme values for axis minimum and maximum
    axis_min = 999999999999999999999999999999999999
    axis_max = -99999999999999999999999999999999999
    
    # iterate through the values
    for i in xrange(hlr_utils.get_length(obj)):
        axis = hlr_utils.get_value(obj, i, o_descr, "x", axis_pos)

        min_index = 0
        max_index = -1

        index_ok = False
        while not index_ok:
            value = axis[min_index]
            if value == float('-inf'):
                min_index += 1
            else:
                index_ok = True
                
        axis_min = min(axis_min, axis[min_index])

        index_ok = False
        while not index_ok:
            value = axis[max_index]
            if value == float('inf'):
                max_index -= 1
            else:
                index_ok = True

        axis_max = max(axis_max, axis[max_index])

        if not width_given:
            test_width = axis[min_index+1] - axis[min_index]
            axis_width = min(axis_width, test_width)

    return hlr_utils.Axis(axis_min, axis_max, axis_width)

