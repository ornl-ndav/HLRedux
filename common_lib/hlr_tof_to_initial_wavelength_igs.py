def tof_to_initial_wavelength_igs(obj,lambda_f=None,time_zero=None,
                                  dist_source_sample=None,
                                  dist_sample_detector=None,
                                  units="microseconds"):
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
    -> lambda_f (OPTIONAL) is a tuple or list of tuples that provides the final
       wavelength information
    -> time_zero (OPTIONAL) is a tuple or list of tuples that provides the
       t0 offset information
    -> dist_source_sample (OPTIONAL) is a tuple or list of tuples that
       provides the source to sample pathlength
    -> dist_sample_detector (OPTIONAL) is a tuple or list of tuples that
       provides the sample to detector pathlength

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

    # Where to get instrument information
    if o_descr == "SOM":
        try:
            obj.attr_list.instrument.get_primary()
            inst = obj.attr_list.instrument
        except RuntimeError:
            raise RuntimeError, "A detector was not provided!"

    if lambda_f != None:
        l_descr,e_descr = hlr_utils.get_descr(lambda_f)
    else:
        if o_descr == "SOM":
            try:
                obj.attr_list["Wavelength_final"]
                l_f = obj.attr_list["Wavelength_final"][0]
                l_f_err2 = obj.attr_list["Wavelength_final"][1]
            except KeyError:
                raise RuntimeError, "Please provide a final wavelength "\
                      +"parameter either via the function call or the SOM"
        else:
            raise RuntimeError, "You need to provide a final wavelength"
            

    if time_zero != None:
        t_descr,e_descr = hlr_utils.get_descr(time_zero)
    else:
        if o_descr == "SOM":
            try:
                obj.attr_list["Time_zero"]
                t_0 = obj.attr_list["Time_zero"][0]
                t_0_err2 = obj.attr_list["Time_zero"][1]
            except KeyError:
                raise RuntimeError, "Please provide a final wavelength "\
                      +"parameter either via the function call or the SOM"
        else:
            t_0 = 0.0
            t_0_err2 = 0.0


    if dist_source_sample != None:
        ls_descr,e_descr = hlr_utils.get_descr(dist_source_sample)

    if dist_sample_detector != None:
        ld_descr,e_descr = hlr_utils.get_descr(dist_sample_detector)


    # iterate through the values
    import axis_manip
    
    for i in range(hlr_utils.get_length(obj)):
        val = hlr_utils.get_value(obj,i,o_descr,"x",axis)
        err2 = hlr_utils.get_err2(obj,i,o_descr,"x",axis)

        map_so = hlr_utils.get_map_so(obj,None,i)

        if dist_source_sample == None:
            L_s,L_s_err2 = hlr_utils.get_parameter("primary",map_so,inst)
        else:
            L_s = hlr_utils.get_value(dist_source_sample,i,ls_descr)
            L_s_err2 = hlr_utils.get_err2(dist_source_sample,i,ls_descr)

        if dist_sample_detector == None:
            L_d,L_d_err2 = hlr_utils.get_parameter("secondary",map_so,inst)
        else:
            L_d = hlr_utils.get_value(dist_sample_detector,i,ld_descr)
            L_d_err2 = hlr_utils.get_err2(dist_sample_detector,i,ld_descr)

        if lambda_f != None:
            l_f = hlr_utils.get_value(lambda_f,i,t_descr)
            l_f_err2 = hlr_utils.get_err2(lambda_f,i,t_descr)
            
        if time_zero != None:
            t_0 = hlr_utils.get_value(time_zero,i,t_descr)
            t_0_err2 = hlr_utils.get_err2(time_zero,i,t_descr)

        value=axis_manip.tof_to_initial_wavelength_igs(val, err2,
                                                       l_f, l_f_err2,
                                                       t_0, t_0_err2,
                                                       L_s, L_s_err2,
                                                       L_d, L_d_err2)

        hlr_utils.result_insert(result,res_descr,value,map_so,"x",axis)

    return result


if __name__=="__main__":
    import hlr_test
    import SOM

    lambda_f = (7.0, 0.1)    
    time_zero = (0.1, 0.001)
    dist_source_sample = (15.0, 0.1)
    dist_sample_detector = (1.0, 0.05)

    som1=hlr_test.generate_som()
    som1.setAllAxisUnits(["microseconds"])
    som1.attr_list["Wavelength_final"] = lambda_f
    som1.attr_list["Time_zero"] = time_zero
    som1.attr_list.instrument = SOM.ASG_Instrument()
    
    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1]

    print "********** tof_to_initial_wavelength_igs"
    print "* som  :",tof_to_initial_wavelength_igs(som1)
    print "* so   :",tof_to_initial_wavelength_igs(som1[0],lambda_f,time_zero,
                                                   dist_source_sample,
                                                   dist_sample_detector)
    print "* scal :",tof_to_initial_wavelength_igs([1,1],lambda_f,time_zero,
                                                   dist_source_sample,
                                                   dist_sample_detector)



