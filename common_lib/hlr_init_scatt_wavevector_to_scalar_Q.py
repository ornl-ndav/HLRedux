def init_scatt_wavevector_to_scalar_Q(initk,scattk,polar=None,
                                      units="1/Angstroms"):
    """
    This function takes an initial wavevector and a scattered wavevector as a
    tuple and a SOM, a tuple and a SO  or two tuples and calculates the
    quantity scalar_Q units of 1/Angstroms. The SOM principle axis must be in
    units of 1/Angstroms. The tuple(s) is(are) assumed to be in units of
    1/Angstroms.

    Parameters:
    ----------
    -> initk is a SOM, SO or tuple of the initial wavevector
    -> scattk is a SOM, SO or tuple of the scattered wavevector

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
    """

    # import the helper functions
    import hlr_utils

    # set up for working through data
    result,res_descr=hlr_utils.empty_result(initk,scattk)
    i_descr,s_descr=hlr_utils.get_descr(initk,scattk)

    # error checking for types
    if i_descr == "SOM" and s_descr == "SOM":
        raise TypeError, "SOM-SOM operation not supported"
    elif i_descr == "SOM" and s_descr == "SO":
        raise TypeError, "SOM-SO operation not supported"
    elif i_descr == "SO" and s_descr == "SOM":
        raise TypeError, "SO-SOM operation not supported"
    elif i_descr == "SO" and s_descr == "SO":
        raise TypeError, "SO-SO operation not supported"

    result=hlr_utils.copy_som_attr(result,res_descr,initk,i_descr,
                                   scattk,s_descr)
    if res_descr == "SOM":
        index = hlr_utils.hlr_1D_units(result, units)
        result = hlr_utils.hlr_force_units(result, units, index)
        result.setAxisLabel(index, "scalar_Q_transfer")

    if polar == None:
        polar = [0.785398163, 0.01]

    if i_descr == "number":
        size = len(initk)
        if size > 2:
            i_multi = True
        else:
            i_multi = False
    else:
        i_multi = False

    if s_descr == "number":
        size = len(scattk)
        if size > 2:
            s_multi = True
        else:
            s_multi = False
    else:
        s_multi = False

    # iterate through the values
    import axis_manip
    
    for i in range(hlr_utils.get_length(initk,scattk)):
        if i_multi:
            val1 = hlr_utils.get_value(initk,i,i_descr,"x")
            err2_1 = hlr_utils.get_err2(initk,i,i_descr,"x")
        else:
            val1 = hlr_utils.get_value(initk,0,i_descr,"x")
            err2_1 = hlr_utils.get_err2(initk,0,i_descr,"x")
        if s_multi:
            val2 = hlr_utils.get_value(scattk,i,s_descr,"x")
            err2_2 = hlr_utils.get_err2(scattk,i,s_descr,"x")
        else:
            val2 = hlr_utils.get_value(scattk,0,s_descr,"x")
            err2_2 = hlr_utils.get_err2(scattk,0,s_descr,"x")
            
        value=axis_manip.init_scatt_wavevector_to_scalar_Q(val1, err2_1,
                                                           val2, err2_2,
                                                           polar[0], polar[1])

        map_so = hlr_utils.get_map_so(initk,scattk,i)
        hlr_utils.result_insert(result,res_descr,value,map_so,"x")

    return result


if __name__=="__main__":
    import hlr_test

    som1=hlr_test.generate_som()
    som1.setAllAxisUnits(["1/Angstroms"])

    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1]

    print "********** init_scatt_wavevector_to_scalar_Q"
    print "* som -scal:",init_scatt_wavevector_to_scalar_Q(som1,(1,1))
    print "* scal-som :",init_scatt_wavevector_to_scalar_Q((1,1),som1)
    print "* so  -scal:",init_scatt_wavevector_to_scalar_Q(som1[0],(1,1))
    print "* scal-so  :",init_scatt_wavevector_to_scalar_Q((1,1),som1[0])
    print "* scal-scal:",init_scatt_wavevector_to_scalar_Q((2,1),(1,1))





