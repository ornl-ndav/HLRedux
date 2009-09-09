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

def mult_ncerr(left, right, **kwargs):
    """
    This function multiplies two objects (C{SOM}, C{SO} or
    C{tuple(val,val_err2)}) and returns the result of the multiplication in a
    C{SOM} or C{SO}. The function does not handle the case of
    C{tuple}*C{tuple}.

    @param left: Object on the left of the multiplication sign
    @type left: C{SOM.SOM}, C{SOM.SO}

    @param right: Object on the right of the multiplication sign
    @type right: C{SOM.SOM}, C{SOM.SO} or C{tuple}
    
    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword axis: This is the axis one wishes to manipulate. If no argument
                   is given the default value is y
    @type axis: C{string}=<y or x>
    
    @keyword axis_pos: This is position of the axis in the axis array. If no
                       argument is given, the default value is 0
    @type axis_pos: C{int}

    @keyword length_one_som: This is a flag that lets the function know it is
                             dealing with a length 1 C{SOM} so that attributes
                             may be passed along. The length 1 C{SOM} will be
                             turned into a C{SO}. The default value is False.
    @type length_one_som: C{boolean}
    
    @keyword length_one_som_pos: This is the argument position of the length 1
                                 C{SOM} since division order is not
                                 commutative. The default value is 2.
    @type length_one_som_pos: C{int}=<1 or 2> 


    @return: Object containing the results of the multiplication
    @rtype: C{SOM.SOM} or C{SOM.SO} 


    @raise TypeError: The C{tuple}*C{tuple} case is presented to the function
    
    @raise IndexError: The two C{SOM}s do not contain the same number of
                       spectra
    @raise RunTimeError: The x-axis units of the C{SOM}s do not match
    
    @raise RunTimeError: The y-axis units of the C{SOM}s do not match
    
    @raise RunTimeError: The x-axes of the two C{SO}s are not equal
    """
    
    # import the helper functions
    import hlr_utils

    # Check to see if we are working with a length 1 SOM
    try:
        length_one_som = kwargs["length_one_som"]
    except KeyError:
        length_one_som = False

    try:
        length_one_som_pos = kwargs["length_one_som_pos"]
        if length_one_som_pos != 1 or length_one_som_pos != 2:
            raise RuntimeError("length_one_som_pos must be either 1 or 2 and "\
                               +"%d" % length_one_som_pos)
    except KeyError:
        length_one_som_pos = 2

    if length_one_som:
        if length_one_som_pos == 1:
            som_copy = left
            left = left[0]
        else:
            som_copy = right
            right = right[0]
    else:
        # Not working with a length 1 SOM, do nothing
        pass

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(left, right)
    (l_descr, r_descr) = hlr_utils.get_descr(left, right)

    # error check information
    if (r_descr == "SOM" and l_descr != "SOM") \
           or (r_descr == "SO" and l_descr == "number"):
        (left, right) = hlr_utils.swap_args(left, right)
        (l_descr, r_descr) = hlr_utils.swap_args(l_descr, r_descr)
    elif r_descr == "SOM" and l_descr == "SOM":
        hlr_utils.math_compatible(left, l_descr, right, r_descr)
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

    if length_one_som:
        if length_one_som_pos == 1:
            result = hlr_utils.copy_som_attr(result, res_descr,
                                             som_copy, "SOM",
                                             right, r_descr)
        else:
            result = hlr_utils.copy_som_attr(result, res_descr, left, l_descr,
                                             som_copy, "SOM")            
    else:
        result = hlr_utils.copy_som_attr(result, res_descr, left, l_descr,
                                         right, r_descr)

    # iterate through the values
    import array_manip
    
    for i in xrange(hlr_utils.get_length(left, right)):
        
        val1 = hlr_utils.get_value(left, i, l_descr, axis, axis_pos)
        err2_1 = hlr_utils.get_err2(left, i, l_descr, axis, axis_pos)

        val2 = hlr_utils.get_value(right, i, r_descr, axis, axis_pos)
        err2_2 = hlr_utils.get_err2(right, i, r_descr, axis, axis_pos)

        (descr_1, descr_2)=hlr_utils.get_descr(val1, val2)

        hlr_utils.math_compatible(val1, descr_1, val2, descr_2)

        value = array_manip.mult_ncerr(val1, err2_1, val2, err2_2)

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

    print "********** mult_ncerr"
    print "* so +scal:", mult_ncerr(som1[0], (1, 1))
    print "* so +so  :", mult_ncerr(som1[0], som1[1])
    print "* som+scal:", mult_ncerr(som1, (1, 1))
    print "* som+so  :", mult_ncerr(som1, som1[0])
    print "* som+som :", mult_ncerr(som1, som2)
