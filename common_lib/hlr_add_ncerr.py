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

def add_ncerr(left, right, **kwargs):
    """
    This function adds two objects (SOM, SO or tuple[val,val_err2]) and
    returns the result of the addition in an SOM. The function does not
    handle the case of tuple/tuple.

    Parameters:
    ----------
    -> left  Object on the left of the addition sign
    -> right Object on the right of the addition sign
    -> kwargs is a list of key word arguments that the function accepts:
         axis=<y or x> This is the axis one wishes to manipulate. If no
               argument is given the default value is y
         axis_pos=<number> This is position of the axis in the axis array. If
                  no argument is given, the default value is 0

    Returns:
    -------
    <- A SOM or SO containing the results of the addition

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
    (result, res_descr) = hlr_utils.empty_result(left, right)
    (l_descr, r_descr) = hlr_utils.get_descr(left, right)

    # error check information
    if (r_descr == "SOM" and l_descr != "SOM") \
           or (r_descr == "SO" and l_descr == "number"):
        left, right = hlr_utils.swap_args(left, right)
        (l_descr, r_descr) = hlr_utils.swap_args(l_descr, r_descr)
    elif r_descr == "SOM" and l_descr == "SOM":
        hlr_utils.hlr_math_compatible(left, l_descr, right, r_descr)
    elif l_descr == "number" and r_descr == "number":
        raise RuntimeError("tuple, tuple operation is not supported!")
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

    result = hlr_utils.copy_som_attr(result, res_descr, left, l_descr,
                                     right, r_descr)

    # iterate through the values
    import array_manip
    
    for i in xrange(hlr_utils.get_length(left, right)):
        val1 = hlr_utils.get_value(left, i, l_descr, axis, axis_pos)
        err2_1 = hlr_utils.get_err2(left, i, l_descr, axis, axis_pos)

        val2 = hlr_utils.get_value(right, i, r_descr, axis, axis_pos)
        err2_2 = hlr_utils.get_err2(right, i, r_descr, axis, axis_pos)
        
        (descr_1, descr_2) = hlr_utils.get_descr(val1, val2)

        hlr_utils.hlr_math_compatible(val1, descr_1, val2, descr_2)

        value = array_manip.add_ncerr(val1, err2_1, val2, err2_2)

        map_so = hlr_utils.get_map_so(left, None, i)
        hlr_utils.result_insert(result, res_descr, value, map_so, axis,
                                axis_pos)

    return result

if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som()
    som2 = hlr_test.generate_som()

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]
    print "********** SOM2"
    print "* ", som2[0]
    print "* ", som2[1]

    print "********** add_ncerr"
    print "* so +scal:", add_ncerr(som1[0], (1, 1))
    print "* so +so  :", add_ncerr(som1[0], som1[1])
    print "* som+scal:", add_ncerr(som1, (1, 1))
    print "* som+so  :", add_ncerr(som1, som1[0])
    print "* som+som :", add_ncerr(som1, som2)
    print "* som+slist :", add_ncerr(som1, [(1, 1), (2, 1)])
