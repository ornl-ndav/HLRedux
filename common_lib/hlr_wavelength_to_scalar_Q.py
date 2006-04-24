def wavelength_to_scalar_Q(obj,polar=None,units="Angstroms"):
    """
    This function converts a primary axis of a SOM or SO from wavelength
    to scalar_Q. The wavelength axis for a SOM must be in units of
    Angstroms. The primary axis of a SO is assumed to be in units of
    Angstroms. A tuple of [wavelength, wavelength_err2] (assumed to be in
    units of Angstroms) can be converted to [scalar_Q, scalar_Q_err2].

    Parameters:
    ----------
    -> obj is the SOM, SO or tuple to be converted
     -> polar (OPTIONAL) is a tuple or list of tuples providing the polar angle
       information
 
    Return:
    ------
    <- A SOM or SO with a primary axis in wavelength or a tuple converted to
       scalar_Q

    Exceptions:
    ----------
    <- TypeError is raised if the incoming object is not a type the function
       recognizes
    <- RuntimeError is raised if the SOM x-axis units are not Angstroms
    """
    
    # import the helper functions
    import hlr_utils

    # set up for working through data
    result,res_descr=hlr_utils.empty_result(obj)
    o_descr,d_descr=hlr_utils.get_descr(obj)

    # Primary axis for transformation. If a SO is passed, the function, will
    # assume the axis for transformation is at the 0 position
    if o_descr == "SOM":
        axis = hlr_utils.hlr_1D_units(obj, units)
    else:
        axis = 0

    result=hlr_utils.copy_som_attr(result,res_descr,obj,o_descr)
    if res_descr == "SOM":
        result = hlr_utils.hlr_force_units(result, "1/Angstroms", axis)
        result.setAxisLabel(axis, "scalar wavevector transfer")
        result.setYUnits("Counts/A-1")
        result.setYLabel("Intensity")

    if polar == None:
        if o_descr == "SOM":
            try:
                obj.attr_list.instrument.get_primary()
                inst = obj.attr_list.instrument
            except RuntimeError:
                raise RuntimeError, "A detector was not provided!"
    else:
        p_descr,e_descr = hlr_utils.get_descr(polar)

    # iterate through the values
    import axis_manip
    
    for i in range(hlr_utils.get_length(obj)):
        val = hlr_utils.get_value(obj,i,o_descr,"x",axis)
        err2 = hlr_utils.get_err2(obj,i,o_descr,"x",axis)

        map_so = hlr_utils.get_map_so(obj,None,i)

        if polar == None:
            angle,angle_err2 = hlr_utils.get_parameter("polar",map_so,inst)
        else:
            angle = hlr_utils.get_value(polar,i,p_descr)
            angle_err2 = hlr_utils.get_err2(polar,i,p_descr) 

        value=axis_manip.wavelength_to_scalar_Q(val, err2, angle, angle_err2)

        if o_descr != "number":
            rev_value = []
            rev_value.append(axis_manip.reverse_array_cp(value[0]))
            rev_value.append(axis_manip.reverse_array_cp(value[1]))
        else:
            rev_value = value

        if map_so != None:
            map_so.y=axis_manip.reverse_array_cp(map_so.y)
            map_so.var_y=axis_manip.reverse_array_cp(map_so.var_y)
        
        hlr_utils.result_insert(result,res_descr,rev_value,map_so,"x",axis)

    return result


if __name__=="__main__":
    import hlr_test
    import SOM

    polar=(0.785, 0.005)

    som1=hlr_test.generate_som()
    som1.setAllAxisUnits(["Angstroms"])
    som1.attr_list.instrument = SOM.ASG_Instrument()

    som2=hlr_test.generate_som()
    som2.setAllAxisUnits(["Angstroms"])
    som2.attr_list.instrument = SOM.ASG_Instrument()

    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1]

    print "********** SOM2"
    print "* ",som2[0]
    print "* ",som2[1]

    print "********** wavelength_to_scalar_Q"
    print "* som  :",wavelength_to_scalar_Q(som1)
    print "* so   :",wavelength_to_scalar_Q(som2[0], polar)
    print "* scal :",wavelength_to_scalar_Q([1,1], polar)


