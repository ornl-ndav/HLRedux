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

def tof_to_initial_wavelength_igs(obj, **kwargs):
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
    -> kwargs is a list of key word arguments that the function accepts:
          lambda_f= a tuple containing the final wavelength and its
                    associated error^2
          time_zero= a tuple containing the time zero offset and its
                     associated error^2
          dist_source_sample= a tuple or list of tuples containing the source
                              to sample distance information and its
                              associated error^2
          dist_sample_detector= a tuple or list of tuples containing the sample
                                to detector distance information and its
                                associated error^2
          run_filter=<True or False> This determines if the filter on the
                     negative wavelengths is run
          units= a string containing the expected units for this function.
                 The default for this function is microseconds

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
    (result, res_descr) = hlr_utils.empty_result(obj)
    o_descr = hlr_utils.get_descr(obj)

    # Setup keyword arguments
    try:
        lambda_f = kwargs["lambda_f"]
    except KeyError:
        lambda_f = None

    try:
        time_zero = kwargs["time_zero"]
    except KeyError:
        time_zero = None

    try:
        dist_source_sample = kwargs["dist_source_sample"]
    except KeyError:
        dist_source_sample = None

    try:
        dist_sample_detector = kwargs["dist_sample_detector"]
    except KeyError:
        dist_sample_detector = None

    try:
        units = kwargs["units"]
    except KeyError:
        units = "microseconds"

    try:
        run_filter = kwargs["run_filter"]
    except KeyError:
        run_filter = True

    # Primary axis for transformation. If a SO is passed, the function, will
    # assume the axis for transformation is at the 0 position
    if o_descr == "SOM":
        axis = hlr_utils.hlr_1D_units(obj, units)
    else:
        axis = 0

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)
    if res_descr == "SOM":
        result = hlr_utils.hlr_force_units(result, "Angstroms", axis)
        result.setAxisLabel(axis, "wavelength")
        result.setYUnits("Counts/A")
        result.setYLabel("Intensity")
    else:
        pass

    # Where to get instrument information
    if dist_source_sample is None or dist_sample_detector is None:
        if o_descr == "SOM":
            try:
                obj.attr_list.instrument.get_primary()
                inst = obj.attr_list.instrument
            except RuntimeError:
                raise RuntimeError("A detector was not provided!")
        else:
            if dist_source_sample is None and dist_sample_detector is None:
                raise RuntimeError("If a SOM is not passed, the "\
                                   +"source-sample and sample-detector "\
                                   +"distances must be provided.")
            elif dist_source_sample is None:
                raise RuntimeError("If a SOM is not passed, the "\
                                   +"source-sample distance must be provided.")
            elif dist_sample_detector is None:
                raise RuntimeError("If a SOM is not passed, the "\
                                   +"sample-detector distance must be "\
                                   +"provided.")
            else:
                raise RuntimeError("If you get here, see Steve Miller for "\
                                   +"your mug.")
    else:
        pass
        
    if lambda_f is not None:
        l_descr = hlr_utils.get_descr(lambda_f)
    else:
        if o_descr == "SOM":
            try:
                som_l_f = obj.attr_list["Wavelength_final"]
            except KeyError:
                raise RuntimeError("Please provide a final wavelength "\
                                   +"parameter either via the function call "\
                                   +"or the SOM")
        else:
            raise RuntimeError("You need to provide a final wavelength")
            

    if time_zero is not None:
        t_descr = hlr_utils.get_descr(time_zero)
    else:
        if o_descr == "SOM":
            try:
                obj.attr_list["Time_zero"]
                t_0 = obj.attr_list["Time_zero"][0]
                t_0_err2 = obj.attr_list["Time_zero"][1]
            except KeyError:
                raise RuntimeError("Please provide a time-zero "\
                                   +"parameter either via the function call "\
                                   +"or the SOM")
        else:
            t_0 = 0.0
            t_0_err2 = 0.0


    if dist_source_sample is not None:
        ls_descr = hlr_utils.get_descr(dist_source_sample)
    # Do nothing, go on
    else:
        pass

    if dist_sample_detector is not None:
        ld_descr = hlr_utils.get_descr(dist_sample_detector)
    # Do nothing, go on
    else:
        pass

    # iterate through the values
    import axis_manip
    
    for i in xrange(hlr_utils.get_length(obj)):
        val = hlr_utils.get_value(obj, i, o_descr, "x", axis)
        err2 = hlr_utils.get_err2(obj, i, o_descr, "x", axis)

        map_so = hlr_utils.get_map_so(obj, None, i)

        if dist_source_sample is None:
            (L_s, L_s_err2) = hlr_utils.get_parameter("primary", map_so, inst)
        else:
            L_s = hlr_utils.get_value(dist_source_sample, i, ls_descr)
            L_s_err2 = hlr_utils.get_err2(dist_source_sample, i, ls_descr)

        if dist_sample_detector is None:
            (L_d, L_d_err2) = hlr_utils.get_parameter("secondary", map_so,
                                                      inst)
        else:
            L_d = hlr_utils.get_value(dist_sample_detector, i, ld_descr)
            L_d_err2 = hlr_utils.get_err2(dist_sample_detector, i, ld_descr)

        if lambda_f is not None:
            l_f = hlr_utils.get_value(lambda_f, i, l_descr)
            l_f_err2 = hlr_utils.get_err2(lambda_f, i, l_descr)
        else:
            l_f_tuple = hlr_utils.get_special(som_l_f, map_so)
            l_f = l_f_tuple[0]
            l_f_err2 = l_f_tuple[1]
            
        if time_zero is not None:
            t_0 = hlr_utils.get_value(time_zero, i, t_descr)
            t_0_err2 = hlr_utils.get_err2(time_zero, i, t_descr)
        else:
            pass

        value = axis_manip.tof_to_initial_wavelength_igs(val, err2,
                                                         l_f, l_f_err2,
                                                         t_0, t_0_err2,
                                                         L_s, L_s_err2,
                                                         L_d, L_d_err2)

        # Remove all wavelengths < 0
        if run_filter:
            index = 0
            for val in value[0]:
                if val >= 0:
                    break
                index += 1

            value[0].__delslice__(0, index)
            value[1].__delslice__(0, index)
            map_so.y.__delslice__(0, index)
            map_so.var_y.__delslice__(0, index)
        else:
            pass

        hlr_utils.result_insert(result, res_descr, value, map_so, "x", axis)

    return result


if __name__ == "__main__":
    import hlr_test
    import SOM

    l_f_i = (7.0, 0.1)    
    t_0_i = (0.1, 0.001)
    d_ss = (15.0, 0.1)
    d_sd = (1.0, 0.05)

    som1 = hlr_test.generate_som()
    som1.setAllAxisUnits(["microseconds"])
    som1.attr_list["Wavelength_final"] = l_f_i
    som1.attr_list["Time_zero"] = t_0_i
    som1.attr_list.instrument = SOM.ASG_Instrument()
    
    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** tof_to_initial_wavelength_igs"
    print "* som  :", tof_to_initial_wavelength_igs(som1, run_filter=False)
    print "* so   :", tof_to_initial_wavelength_igs(som1[0], lambda_f=l_f_i,
                                                    time_zero=t_0_i,
                                                    dist_source_sample=d_ss,
                                                    dist_sample_detector=d_sd,
                                                    run_filter=False)
    print "* scal :", tof_to_initial_wavelength_igs([1, 1], lambda_f=l_f_i,
                                                    time_zero=t_0_i,
                                                    dist_source_sample=d_ss,
                                                    dist_sample_detector=d_sd,
                                                    run_filter=False)



