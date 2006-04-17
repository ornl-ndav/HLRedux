def energy_transfer(left,right,units="meV"):
    """
    This function takes a tuple and a SOM, a tuple and a SO or two tuples and
    calculates the energy transfer in units of THz. The SOM principle axis
    must be in units of meV. The SO and tuples are assumed to be in units of
    meV.

    Parameters:
    ----------
    -> left is a SOM, SO or tuple on the left side of the subtraction
    -> right is a SOM, SO or tuple on the right side of the subtraction

    Return:
    ------
    <- A SOM, SO or tuple based on left - right in units of THz

    Exceptions:
    ----------

    <- RuntimeError is raised if the x-axis units are not meV
    """

    # import the helper functions
    import hlr_utils

    # set up for working through data
    result,res_descr=hlr_utils.empty_result(left,right)
    l_descr,r_descr=hlr_utils.get_descr(left,right)

    # error checking for types
    if l_descr == "SOM" and r_descr == "SOM":
        raise TypeError, "SOM-SOM operation not supported"
    elif l_descr == "SOM" and r_descr == "SO":
        raise TypeError, "SOM-SO operation not supported"
    elif l_descr == "SO" and r_descr == "SOM":
        raise TypeError, "SO-SOM operation not supported"
    elif l_descr == "SO" and r_descr == "SO":
        raise TypeError, "SO-SO operation not supported"
    
    result=hlr_utils.copy_som_attr(result,res_descr,left,l_descr,right,r_descr)
    if res_descr == "SOM":
        index = hlr_utils.hlr_1D_units(result, units)
        result = hlr_utils.hlr_force_units(result, "THz", index)
        result.setAxisLabel(index, "energy_transfer")

    if l_descr == "number":
        size = len(left)
        if size > 2:
            l_multi = True
        else:
            l_multi = False
    else:
        l_multi = False

    if r_descr == "number":
        size = len(right)
        if size > 2:
            r_multi = True
        else:
            r_multi = False
    else:
        r_multi = False

    # iterate through the values
    import axis_manip
    
    for i in range(hlr_utils.get_length(left,right)):
        if l_multi:
            val1 = hlr_utils.get_value(left,i,l_descr,"x")
            err2_1 = hlr_utils.get_err2(left,i,l_descr,"x")
        else:
            val1 = hlr_utils.get_value(left,0,l_descr,"x")
            err2_1 = hlr_utils.get_err2(left,0,l_descr,"x")
        if r_multi:
            val2 = hlr_utils.get_value(right,i,r_descr,"x")
            err2_2 = hlr_utils.get_err2(right,i,r_descr,"x")
        else:
            val2 = hlr_utils.get_value(right,0,r_descr,"x")
            err2_2 = hlr_utils.get_err2(right,0,r_descr,"x")
            
        value=axis_manip.energy_transfer(val1, err2_1, val2, err2_2)

        map_so = hlr_utils.get_map_so(left,right,i)
        hlr_utils.result_insert(result,res_descr,value,map_so,"x")

    return result


if __name__=="__main__":
    import hlr_test

    som1=hlr_test.generate_som()
    som1.setAllAxisUnits(["meV"])
    som2=hlr_test.generate_som()
    som2.setAllAxisUnits(["meV"])

    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1]
    print "********** SOM2"
    print "* ",som2[0]
    print "* ",som2[1]

    print "********** energy_transfer"
    print "* som -scal:",energy_transfer(som1,(1,1))
    print "* scal-som :",energy_transfer((1,1),som1)
    print "* so  -scal:",energy_transfer(som1[0],(1,1))
    print "* scal-so  :",energy_transfer((1,1),som1[0])
    print "* scal-scal:",energy_transfer((2,1),(1,1))





