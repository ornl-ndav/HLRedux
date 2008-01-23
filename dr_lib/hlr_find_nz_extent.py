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

def find_nz_extent(obj, **kwargs):
    """
    This function takes spectra and determines the extent (range) of the
    non-zero data. The lower end of the extent is determined by starting at the
    lower bound and moving up until non-zero data is encountered. Then, the
    upper end of the extent is determined by starting from the upper bound and
    moving down until non-zero data is encountered. This technique works best
    with summed spectra as individual spectrum are usually sparse. 

    @param obj: Object used for determining the non-zero data extent
    @type obj: C{SOM.SOM} or C{SOM.SO}

    @param kwargs: A list of keyword arguments that the function accepts:

    @keyword axis_pos: This is position of the x-axis in the axis array. If no
                       argument is given, the default value is I{0}.
    @type axis_pos: C{int}


    @return: Object containing the extent of the non-zero data
    @rtype: C{list} of C{tuple}s


    @raise TypeError: The incoming object is not a C{SOM} or C{SO}.
    """
    # import the helper functions
    import hlr_utils

    o_descr = hlr_utils.get_descr(obj)

    if o_descr != "SOM" and o_descr != "SO":
        raise TypeError("Incoming object must be a SOM or a SO")
    # Have a SOM or SO
    else:
        pass

    # set up for working through data
    # This time highest object in the hierarchy is NOT what we need
    result = []
    if(hlr_utils.get_length(obj) > 1):
        res_descr = "list"
    else:
        res_descr = "number"

    # Check for axis_pos keyword argument
    try:
        axis_pos = kwargs["axis_pos"]
    except KeyError:
        axis_pos = 0

    import utils

    min_ext = 0.0
    max_ext = 0.0

    # iterate through the values
    for i in xrange(hlr_utils.get_length(obj)):
        y_val = hlr_utils.get_value(obj, i, o_descr, "y")
        x_axis = hlr_utils.get_value(obj, i, o_descr, "x", axis_pos)

        for i in xrange(len(y_val)):
            if utils.compare(y_val[i], 0.0):
                min_ext = x_axis[i]
                break

        rev_list = range(len(y_val))
        rev_list.reverse()

        for j in rev_list:
            if utils.compare(y_val[j], 0.0):
                max_ext = x_axis[j+1]
                break

        hlr_utils.result_insert(result, res_descr, (min_ext, max_ext), None,
                                "all")

    import copy
    return copy.deepcopy(result)

if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som()

    # Doctor outer values to make test useful
    som1[0].y[0] = 0.0
    som1[0].var_y[0] = 0.0
    som1[0].y[-1] = 0.0
    som1[0].var_y[-1] = 0.0

    som1[1].y[0] = 0.0
    som1[1].var_y[0] = 0.0
    som1[1].y[-2] = 0.0
    som1[1].var_y[-2] = 0.0    
    som1[1].y[-1] = 0.0
    som1[1].var_y[-1] = 0.0    

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** find_nz_extent"
    print "* ", find_nz_extent(som1)
