def wavelength_to_scalar_k(obj,units="Angstroms"):
    """
    This function converts a primary axis of a SOM or SO from wavelength
    to scalar_k. The wavelength axis for a SOM must be in units of Angstroms.
    The primary axis of a SO is assumed to be in units of Angstroms. A tuple
    of [wavelength, wavelength_err2] (assumed to be in units of Angstroms) can
    be converted to [scalar_k, scalar_k_err2].

    Parameters:
    ----------
    -> obj is the SOM, SO or tuple to be converted

    Return:
    ------
    <- A SOM or SO with a primary axis in scalar_k or a tuple converted to
       scalar_k

    Exceptions:
    ----------
    <- TypeError is raised if the incoming object is not a type the function
       recognizes
    <- RuntimeError is raised if the SOM x-axis units are not Angstroms
    """

    # import the helper functions
    import hlr_utils

    # set up for working through data
    (result,res_descr)=hlr_utils.empty_result(obj)
    (o_descr,d_descr)=hlr_utils.get_descr(obj)

    if o_descr == "list":
        raise TypeError, "Do not know how to handle given type: %s" %\
              o_descr
    else:
        pass

    # Primary axis for transformation. If a SO is passed, the function, will
    # assume the axis for transformation is at the 0 position
    if o_descr == "SOM":
        axis = hlr_utils.hlr_1D_units(obj, units)
    else:
        axis = 0

    result=hlr_utils.copy_som_attr(result,res_descr,obj,o_descr)
    if res_descr == "SOM":
        result = hlr_utils.hlr_force_units(result, "1/Angstroms", axis)
        result.setAxisLabel(axis, "scalar wavevector")
        result.setYUnits("Counts/A-1")
        result.setYLabel("Intensity")
    else:
        pass

    # iterate through the values
    import axis_manip
    
    for i in range(hlr_utils.get_length(obj)):
        val = hlr_utils.get_value(obj,i,o_descr,"x",axis)
        err2 = hlr_utils.get_err2(obj,i,o_descr,"x",axis)

        value=axis_manip.wavelength_to_scalar_k(val, err2)
        if o_descr != "number":
            value1 = axis_manip.reverse_array_cp(value[0])
            value2 = axis_manip.reverse_array_cp(value[1])
            rev_value = (value1,value2)
        else:
            rev_value = value
            
        map_so = hlr_utils.get_map_so(obj,None,i)
        if map_so != None:
            map_so.y=axis_manip.reverse_array_cp(map_so.y)
            map_so.var_y=axis_manip.reverse_array_cp(map_so.var_y)
        else:
            pass
        
        hlr_utils.result_insert(result,res_descr,rev_value,map_so,"x",axis)

    return result


if __name__=="__main__":
    import hlr_test

    som1=hlr_test.generate_som()
    som1.setAllAxisUnits(["Angstroms"])

    som2=hlr_test.generate_som()
    som2.setAllAxisUnits(["Angstroms"])

    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1]

    print "********** SOM2"
    print "* ",som2[0]
    print "* ",som2[1]

    print "********** wavelength_to_scalar_k"
    print "* som  :",wavelength_to_scalar_k(som1)
    print "* so   :",wavelength_to_scalar_k(som2[0])
    print "* scal :",wavelength_to_scalar_k((1,1))


