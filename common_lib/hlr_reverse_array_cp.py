def reverse_array_cp(obj):
    """
    This function reverses the y and var_y tuples of all the SOs in a SOM or
    an individual SO. This is assuming that there was a previous
    transformation on the x-axis of the SO or SOM.

    Parameters:
    ----------
    -> obj is the SOM or SO that needs to have its y and var_y tuples
       reversed

    Return:
    ------
    <- A SOM or SO containing the results of the reversal process

    Exceptions:
    ----------
    <- TypeError is raised if a tuple or list of tuples is presented to the
       function
    """

    # import the helper functions
    import hlr_utils

    # set up for working through data
    result,res_descr=hlr_utils.empty_result(obj)
    o_descr,d_descr=hlr_utils.get_descr(obj)

    if o_descr == "number" or o_descr == "list":
        raise TypeError, "Do not know how to handle given type: %s" %\
              +o_descr

    result=hlr_utils.copy_som_attr(result,res_descr,obj,o_descr)

    # iterate through the values
    import axis_manip
    
    for i in range(hlr_utils.get_length(obj)):
        val = hlr_utils.get_value(obj,i,o_descr)
        err2 = hlr_utils.get_err2(obj,i,o_descr)

        value1 = axis_manip.reverse_array_cp(val)
        value2 = axis_manip.reverse_array_cp(err2)

        map_so = hlr_utils.get_map_so(obj,None,i)
        hlr_utils.result_insert(result,res_descr,(value1,value2),map_so)

    return result

if __name__=="__main__":
    import hlr_test

    som1=hlr_test.generate_som()

    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1]

    print "********** reverse_array_cp"
    print "* rev som:",reverse_array_cp(som1)
    print "* rev so :",reverse_array_cp(som1[0])
