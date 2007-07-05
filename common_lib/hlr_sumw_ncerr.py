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
    This function sums by weighting errors of two objects (C{SOM} or C{SO}) and
    returns the result of that action in an C{SOM}. The function does not
    handle the cases of C{SOM}+C{tuple}, C{SO}+C{tuple} or C{tuple}+C{tuple}.

    @param obj1:  First object in the weighted sum
    @type obj1: C{SOM.SOM} or C{SOM.SO} or C{tuple}
    
    @param obj2: Second object in the the weighted sum
    @type obj2: C{SOM.SOM} or C{SOM.SO} or C{tuple}

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
    
    @keyword length_one_som_pos: This is the argument position of the
                                 length 1 C{SOM} since the check is done
                                 before the arguments are swapped. The default
                                 value is 2.
    @type length_one_som_pos: C{int}=<1 or 2>
    

    @return: Object containing the results of the addition
    @rtype: C{SOM.SOM} or C{SOM.SO}


    @raise TypeError: The C{SOM}+C{tuple}, C{SO}+C{tuple} or C{tuple}+C{tuple}
                      cases are presented to the function
    
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
    (result, res_descr) = hlr_utils.empty_result(obj1, obj2)
    (o1_descr, o2_descr) = hlr_utils.get_descr(obj1, obj2)

    # error check information
    if o1_descr == "number" or o2_descr == "number":
        raise RuntimeError("Operations with tuples are not supported!")
    elif o2_descr == "SOM" and o1_descr == "SO":
        (obj1, obj2) = hlr_utils.swap_args(obj1, obj2)
        (o1_descr, o2_descr) = hlr_utils.swap_args(o1_descr, o2_descr)
    elif o2_descr == "SOM" and o1_descr == "SOM":
        hlr_utils.math_compatible(obj1, o1_descr, obj2, o2_descr)
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
        result = hlr_utils.copy_som_attr(result, res_descr, obj1, o1_descr,
                                         obj2, o2_descr)
    
    # iterate through the values
    import array_manip
    
    for i in xrange(hlr_utils.get_length(obj1, obj2)):
        val1 = hlr_utils.get_value(obj1, i, o1_descr, axis, axis_pos)
        err2_1 = hlr_utils.get_err2(obj1, i, o1_descr, axis, axis_pos)

        val2 = hlr_utils.get_value(obj2, i, o2_descr, axis, axis_pos)
        err2_2 = hlr_utils.get_err2(obj2, i, o2_descr, axis, axis_pos)
        
        (descr_1, descr_2) = hlr_utils.get_descr(val1, val2)

        hlr_utils.math_compatible(val1, descr_1, val2, descr_2)

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






