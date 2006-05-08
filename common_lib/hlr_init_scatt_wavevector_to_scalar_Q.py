def init_scatt_wavevector_to_scalar_Q(initk,scattk,polar=None,
                                      units="1/Angstroms"):
    """
    This function takes an initial wavevector and a scattered wavevector as a
    tuple and a SOM, a tuple and a SO  or two tuples and calculates the
    quantity scalar_Q units of 1/Angstroms. The SOM principle axis must be in
    units of 1/Angstroms. The SOs and tuple(s) is(are) assumed to be in units
    of 1/Angstroms. The polar angle must be provided if one of the initial
    arguments is not a SOM. If a SOM is passed, by providing the polar angle
    at the function call time, the polar angle carried in the SOM instrument
    will be overridden.

    Parameters:
    ----------
    -> initk is a SOM, SO or tuple of the initial wavevector
    -> scattk is a SOM, SO or tuple of the scattered wavevector
    -> polar (OPTIONAL) is a tuple or list of tuples providing the polar angle
       information

    Return:
    ------
    <- A SOM, SO or tuple calculated for scalar_Q

    Exceptions:
    ----------
    <- TypeError is raised if the SOM-SOM operation is attempted
    <- TypeError is raised if the SOM-SO operation is attempted
    <- TypeError is raised if the SO-SOM operation is attempted
    <- TypeError is raised if the SO-SO operation is attempted
    <- RuntimeError is raised if the SOM x-axis units are not 1/Angstroms
    <- RuntimeError is raised if a SOM is not passed and no polar angle is
       provided
    <- RuntimeError is raised if no instrument is provided in a SOM
    """

    # import the helper functions
    import hlr_utils

    # set up for working through data
    (result,res_descr)=hlr_utils.empty_result(initk,scattk)
    (i_descr,s_descr)=hlr_utils.get_descr(initk,scattk)

    # error checking for types
    if i_descr == "SOM" and s_descr == "SOM":
        raise TypeError, "SOM-SOM operation not supported"
    elif i_descr == "SOM" and s_descr == "SO":
        raise TypeError, "SOM-SO operation not supported"
    elif i_descr == "SO" and s_descr == "SOM":
        raise TypeError, "SO-SOM operation not supported"
    elif i_descr == "SO" and s_descr == "SO":
        raise TypeError, "SO-SO operation not supported"
    else:
        pass

    result=hlr_utils.copy_som_attr(result,res_descr,initk,i_descr,
                                   scattk,s_descr)
    if res_descr == "SOM":
        index = hlr_utils.hlr_1D_units(result, units)
        result = hlr_utils.hlr_force_units(result, units, index)
        result.setAxisLabel(index, "scalar wavevector transfer")
        result.setYUnits("Counts/A-1")
        result.setYLabel("Intensity")
    else:
        pass

    if polar == None:
        if i_descr == "SOM":
            try:
                initk.attr_list.instrument.get_primary()
                inst = initk.attr_list.instrument
            except RuntimeError:
                raise RuntimeError, "A detector was not provided!"

        elif s_descr == "SOM":
            try:
                scattk.attr_list.instrument.get_primary()
                inst = scattk.attr_list.instrument
            except RuntimeError:
                raise RuntimeError, "A detector was not provided!"

        else:
            raise RuntimeError, "If no SOM is provided, then polar "\
                  +"information must be given."
    else:
        (p_descr,e_descr) = hlr_utils.get_descr(polar)

    # iterate through the values
    import axis_manip
    
    for i in range(hlr_utils.get_length(initk,scattk)):
        val1 = hlr_utils.get_value(initk,i,i_descr,"x")
        err2_1 = hlr_utils.get_err2(initk,i,i_descr,"x")
        
        val2 = hlr_utils.get_value(scattk,i,s_descr,"x")
        err2_2 = hlr_utils.get_err2(scattk,i,s_descr,"x")

        map_so = hlr_utils.get_map_so(initk,scattk,i)

        if polar == None:
            (angle,angle_err2) = hlr_utils.get_parameter("polar",map_so,inst)
        else:
            angle = hlr_utils.get_value(polar,i,p_descr)
            angle_err2 = hlr_utils.get_err2(polar,i,p_descr)
            
        value=axis_manip.init_scatt_wavevector_to_scalar_Q(val1, err2_1,
                                                           val2, err2_2,
                                                           angle, angle_err2)

        hlr_utils.result_insert(result,res_descr,value,map_so,"x")

    return result


if __name__=="__main__":
    import hlr_test
    import SOM

    som1=hlr_test.generate_som()
    som1.setAllAxisUnits(["1/Angstroms"])
    som1.attr_list.instrument = SOM.ASG_Instrument()
    polar = (0.785,0.005)

    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1]

    print "********** init_scatt_wavevector_to_scalar_Q"
    print "* som -scal:",init_scatt_wavevector_to_scalar_Q(som1,(1,1))
    print "* scal-som :",init_scatt_wavevector_to_scalar_Q((1,1),som1)
    print "* so  -scal:",init_scatt_wavevector_to_scalar_Q(som1[0],(1,1),
                                                           polar)
    print "* scal-so  :",init_scatt_wavevector_to_scalar_Q((1,1),som1[0],
                                                           polar)
    print "* scal-scal:",init_scatt_wavevector_to_scalar_Q((2,1),(1,1),
                                                           polar)




