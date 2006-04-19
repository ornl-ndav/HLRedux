def tof_to_initial_wavelength_igs(obj,lambda_f=None,t_0=None,L_s=None,
                                  L_d=None,units="microseconds"):
    """
    This function converts a primary axis of a SOM or SO from time-of-flight
    to initial_wavelength_igs. The time-of-flight axis for a SOM must be in
    units of microseconds. The primary axis of a SO is assumed to be in units
    of microseconds. A tuple of [tof, tof_err2] (assumed to be in units of
    microseconds) can be converted to [initial_wavelength_igs,
    initial_wavelength_igs_err2].

    Parameters:
    ----------
    -> obj is the SOM, SO or tuple to be converted

    Return:
    ------
    <- A SOM or SO with a primary axis in time-of-flight or a tuple converted
       to initial_wavelength_igs

    Exceptions:
    ----------
    <- TypeError is raised if the incoming object is not a type the function
       recognizes
    <- RuntimeError is raised if the SOM x-axis units are not microseconds
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
        result = hlr_utils.hlr_force_units(result, "Angstroms", axis)
        result.setAxisLabel(axis, "wavelength")
        result.setYUnits("Counts/A")
        result.setYLabel("Intensity")

    if lambda_f == None:
        lambda_f = [7.0, 0.1]
    if t_0 == None:
        t_0 = [0.1, 0.001]
    if L_s == None:
        L_s = [15.0, 0.1]
    if L_d == None:
        L_d = [1.0, 0.05]

    # iterate through the values
    import axis_manip
    
    for i in range(hlr_utils.get_length(obj)):
        val = hlr_utils.get_value(obj,i,o_descr,"x",axis)
        err2 = hlr_utils.get_err2(obj,i,o_descr,"x",axis)

        value=axis_manip.tof_to_initial_wavelength_igs(val, err2,
                                                       lambda_f[0],
                                                       lambda_f[1],
                                                       t_0[0], t_0[1],
                                                       L_s[0], L_s[1],
                                                       L_d[0], L_d[1])

        map_so = hlr_utils.get_map_so(obj,None,i)
        hlr_utils.result_insert(result,res_descr,value,map_so,"x",axis)

    return result


if __name__=="__main__":
    import hlr_test

    som1=hlr_test.generate_som()
    som1.setAllAxisUnits(["microseconds"])

    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1]

    print "********** tof_to_initial_wavelength_igs"
    print "* som  :",tof_to_initial_wavelength_igs(som1)
    print "* so   :",tof_to_initial_wavelength_igs(som1[0])
    print "* scal :",tof_to_initial_wavelength_igs([1,1])



