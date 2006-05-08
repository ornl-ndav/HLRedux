def frequency_to_energy(obj,units="THz"):
    """
    This function converts a primary axis of a SOM or SO from frequency
    to energy. The frequency axis for a SOM must be in units of THz.
    The primary axis of a SO is assumed to be in units of THz. A tuple
    of [frequency, frequency_err2] (assumed to be in units of THz) can be
    converted to [energy, energy_err2].

    Parameters:
    ----------
    -> obj is the SOM, SO or tuple to be converted

    Return:
    ------
    <- A SOM or SO with a primary axis in energy or a tuple converted to
       energy

    Exceptions:
    ----------
    <- TypeError is raised if the incoming object is not a type the function
       recognizes
    <- RuntimeError is raised if the SOM x-axis units are not THz
    """

    # import the helper functions
    import hlr_utils

    # set up for working through data
    (result,res_descr)=hlr_utils.empty_result(obj)
    (o_descr,d_descr)=hlr_utils.get_descr(obj)

    # Primary axis for transformation. If a SO is passed, the function, will
    # assume the axis for transformation is at the 0 position
    if o_descr == "SOM":
        axis = hlr_utils.hlr_1D_units(obj, units)
    else:
        axis = 0

    result=hlr_utils.copy_som_attr(result,res_descr,obj,o_descr)
    if o_descr == "SOM":
        result = hlr_utils.hlr_force_units(result, "meV", axis)
        result.setAxisLabel(axis, "energy transfer")
        result.setYUnits("Counts/meV")
        result.setYLabel("Intensity")

    # iterate through the values
    import axis_manip
    
    for i in range(hlr_utils.get_length(obj)):
        val = hlr_utils.get_value(obj,i,o_descr,"x",axis)
        err2 = hlr_utils.get_err2(obj,i,o_descr,"x",axis)

        value=axis_manip.frequency_to_energy(val, err2)

        map_so = hlr_utils.get_map_so(obj,None,i)
        hlr_utils.result_insert(result,res_descr,value,map_so,"x",axis)

    return result


if __name__=="__main__":
    import hlr_test

    som1=hlr_test.generate_som()
    som1.setAllAxisUnits(["THz"])

    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1]

    print "********** frequency_to_energy"
    print "* frequency_to_energy som  :",frequency_to_energy(som1)
    print "* frequency_to_energy so   :",frequency_to_energy(som1[0])
    print "* frequency_to_energy scal :",frequency_to_energy([1,1])



