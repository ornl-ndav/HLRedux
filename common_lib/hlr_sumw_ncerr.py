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

def sumw_ncerr(obj1, obj2, **kwargs):
    """
    This function sums by weighting errors of two objects (SOM or SO) and
    returns the result of that action in an SOM. The function does not
    handle the cases of SOM+tuple, SO+tuple or tuple+tuple.

    Parameters:
    ----------
    -> obj1  First object in the weighted sum
    -> obj2  Second object in the the weighted sum
    -> kwargs is a list of key word arguments that the function accepts:
         axis=<y or x> This is the axis one wishes to manipulate. If no
               argument is given the default value is y
         axis_pos=<number> This is position of the axis in the axis array. If
                  no argument is given, the default value is 0

    Returns:
    -------
    <- A SOM or SO containing the results of the weighted sum

    Exceptions:
    ----------
    <- TypeError is raised if the tuple/tuple case is presented to the function
    <- IndexError is raised if the two SOMs do not contain the same number
       of spectra
    <- RunTimeError is raised if the x-axis units of the SOMs do not match
    <- RunTimeError is raised if the y-axis units of the SOMs do not match
    <- RunTimeError is raised if the x-axes of the two SOs are not equal
    """
    
    # import the helper functions
    import hlr_utils

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj1, obj2)
    (o1_descr, o2_descr) = hlr_utils.get_descr(obj1, obj2)

    # error check information
    if o1_descr == "number" or o2_descr == "number":
        raise RuntimeError("Operations with tuples are not supported!")
    elif o2_descr == "SOM" and o1_descr == "SO":
        (obj1, obj2) = hlr_utils.swap_args(obj1, obj2)
        (o1_descr, o2_descr) = hlr_utils.swap_args(o1_descr, o2_descr)
    elif o2_descr == "SOM" and o1_descr == "SOM":
        hlr_utils.hlr_math_compatible(obj1, o1_descr, obj2, o2_descr)
    else:
        pass

    # Check for axis keyword argument
    try:
        axis = kwargs["axis"]
    except KeyError:
        axis = "y"
        
    # Check for axis_pos keyword argument
    try:
        axis_pos = kwargs["axis_pos"]
    except KeyError:
        axis_pos = 0

    result = hlr_utils.copy_som_attr(result, res_descr, obj1, o1_descr,
                                     obj2, o2_descr)
    
    # iterate through the values
    import array_manip
    
    for i in range(hlr_utils.get_length(obj1, obj2)):
        val1 = hlr_utils.get_value(obj1, i, o1_descr, axis, axis_pos)
        err2_1 = hlr_utils.get_err2(obj1, i, o1_descr, axis, axis_pos)

        val2 = hlr_utils.get_value(obj2, i, o2_descr, axis, axis_pos)
        err2_2 = hlr_utils.get_err2(obj2, i, o2_descr, axis, axis_pos)
        
        (descr_1, descr_2) = hlr_utils.get_descr(val1, val2)

        hlr_utils.hlr_math_compatible(val1, descr_1, val2, descr_2)

        value = array_manip.sumw_ncerr(val1, err2_1, val2, err2_2)
        
        map_so = hlr_utils.get_map_so(obj1, None, i)
        hlr_utils.result_insert(result, res_descr, value, map_so, axis,
                                axis_pos)

    return result


if __name__=="__main__":
    import hlr_test

    som1 = hlr_test.generate_som()
    som2 = hlr_test.generate_som()

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]
    print "********** SOM2"
    print "* ", som2[0]
    print "* ", som2[1]

    print "********** sumw_ncerr"
    print "* som+som :", sumw_ncerr(som1, som2)
    print "* som+so  :", sumw_ncerr(som1, som2[0])
    print "* so +so  :", sumw_ncerr(som1[0], som2[1])






