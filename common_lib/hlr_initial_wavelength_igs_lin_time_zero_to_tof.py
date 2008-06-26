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

def initial_wavelength_igs_lin_time_zero_to_tof(obj, **kwargs):
    """
    This function converts a primary axis of a C{SOM} or C{SO} from
    initial_wavelength_igs_lin_time_zero to time-of-flight. The
    initial_wavelength_igs_lin_time_zero axis for a C{SOM} must be in units of
    I{Angstroms}. The primary axis of a C{SO} is assumed to be in units of
    I{Angstroms}. A C{tuple} of C{(initial_wavelength_igs_lin_time_zero,
    initial_wavelength_igs_lin_time_zero_err2)} (assumed to be in units of
    I{Angstroms}) can be converted to C{(tof, tof_err2)}.

    @param obj: Object to be converted
    @type obj: C{SOM.SOM}, C{SOM.SO} or C{tuple}

    @param kwargs: A list of keyword arguments that the function accepts:

    @keyword lambda_f:The final wavelength and its associated error^2
    @type lambda_f: C{tuple}

    @keyword time_zero_slope: The time zero slope and its associated error^2
    @type time_zero_slope: C{tuple}

    @keyword time_zero_offset: The time zero offset and its associated error^2
    @type time_zero_offset: C{tuple}

    @keyword dist_source_sample: The source to sample distance information and
                                 its associated error^2
    @type dist_source_sample: C{tuple} or C{list} of C{tuple}s

    @keyword dist_sample_detector: The sample to detector distance information
                                   and its associated error^2
    @type dist_sample_detector: C{tuple} or C{list} of C{tuple}s

    @keyword lojac: A flag that allows one to turn off the calculation of the
                    linear-order Jacobian. The default action is True for
                    histogram data.
    @type lojac: C{boolean}

    @keyword units: The expected units for this function. The default for this
                    function is I{Angstroms}
    @type units: C{string}


    @return: Object with a primary axis in initial_wavelength_igs converted to
             time-of-flight
    @rtype: C{SOM.SOM}, C{SOM.SO} or C{tuple}


    @raise TypeError: The incoming object is not a type the function recognizes

    @raise RuntimeError: The C{SOM} x-axis units are not I{Angstroms}
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
        time_zero_slope = kwargs["time_zero_slope"]
    except KeyError:
        time_zero_slope = None

    # Current constants for Time Zero Slope
    TIME_ZERO_SLOPE = (float(0.0), float(0.0))

    try:
        time_zero_offset = kwargs["time_zero_offset"]
    except KeyError:
        time_zero_offset = None        

    # Current constants for Time Zero Offset
    TIME_ZERO_OFFSET = (float(0.0), float(0.0))

    try:
        dist_source_sample = kwargs["dist_source_sample"]
    except KeyError:
        dist_source_sample = None

    try:
        dist_sample_detector = kwargs["dist_sample_detector"]
    except KeyError:
        dist_sample_detector = None

    try:
        lojac = kwargs["lojac"]
    except KeyError:
        lojac = hlr_utils.check_lojac(obj)

    try:
        units = kwargs["units"]
    except KeyError:
        units = "Angstroms"

    # Primary axis for transformation. If a SO is passed, the function, will
    # assume the axis for transformation is at the 0 position
    if o_descr == "SOM":
        axis = hlr_utils.one_d_units(obj, units)
    else:
        axis = 0

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)
    if res_descr == "SOM":
        result = hlr_utils.force_units(result, "Microseconds", axis)
        result.setAxisLabel(axis, "time-of-flight")
        result.setYUnits("Counts/uS")
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
            

    if time_zero_slope is not None:
        t_0_slope_descr = hlr_utils.get_descr(time_zero_slope)
    else:
        if o_descr == "SOM":
            try:
                t_0_slope = obj.attr_list["Time_zero_slope"][0]
                t_0_slope_err2 = obj.attr_list["Time_zero_slope"][1]
            except KeyError:
                t_0_slope = TIME_ZERO_SLOPE[0]
                t_0_slope_err2 = TIME_ZERO_SLOPE[1]
        else:
            t_0_slope = TIME_ZERO_SLOPE[0]
            t_0_slope_err2 = TIME_ZERO_SLOPE[1]


    if time_zero_offset is not None:
        t_0_offset_descr = hlr_utils.get_descr(time_zero_offset)
    else:
        if o_descr == "SOM":
            try:
                t_0_offset = obj.attr_list["Time_zero_offset"][0]
                t_0_offset_err2 = obj.attr_list["Time_zero_offset"][1]
            except KeyError:
                t_0_offset = TIME_ZERO_OFFSET[0]
                t_0_offset_err2 = TIME_ZERO_OFFSET[1]
        else:
            t_0_offset = TIME_ZERO_OFFSET[0]
            t_0_offset_err2 = TIME_ZERO_OFFSET[1]
            
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
    if lojac:
        import utils

    len_obj = hlr_utils.get_length(obj)

    MNEUT_OVER_H = 1.0 / 0.003956034
    MNEUT_OVER_H2 = MNEUT_OVER_H * MNEUT_OVER_H

    for i in xrange(len_obj):
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

        if time_zero_slope is not None:
            t_0_slope = hlr_utils.get_value(time_zero_slope, i,
                                            t_0_slope_descr)
            t_0_slope_err2 = hlr_utils.get_err2(time_zero_slope, i,
                                                t_0_slope_descr)
        else:
            pass

        if time_zero_offset is not None:
            t_0_offset = hlr_utils.get_value(time_zero_offset, i,
                                             t_0_offset_descr)
            t_0_offset_err2 = hlr_utils.get_err2(time_zero_offset, i,
                                                 t_0_offset_descr)
        else:
            pass

        # Going to violate rules since the current usage is with a single
        # number. When an SCL equivalent function arises, this code can be
        # fixed. 
        front_const = MNEUT_OVER_H * L_s + t_0_slope
        term2 = MNEUT_OVER_H * l_f * L_d

        tof = (front_const * val) + term2 + t_0_offset
        
        front_const2 = front_const * front_const

        eterm1 = l_f * l_f * L_d_err2
        eterm2 = L_d * L_d * l_f_err2
        eterm3 = MNEUT_OVER_H2 * L_s_err2

        tof_err2 = (front_const2 * err2) + (val * val) * \
                   (eterm3 + t_0_slope_err2) + (MNEUT_OVER_H2 * \
                                                (eterm1 + eterm2))

        hlr_utils.result_insert(result, res_descr, (tof, tof_err2), None,
                                "all"))

    return result

if __name__ == "__main__":
    import hlr_test
    import SOM

    l_f_i = (7.0, 0.1)    
    d_ss = (15.0, 0.1)
    d_sd = (1.0, 0.05)
    t_0_s = (10.0, 1.0)
    t_0_o = (0.1, 0.001)

    som1 = hlr_test.generate_som()
    som1.setAllAxisUnits(["Angstroms"])
    som1.attr_list["Wavelength_final"] = l_f_i
    som1.attr_list["Time_zero_slope"] = t_0_s
    som1.attr_list["Time_zero_offset"] = t_0_o
    som1.attr_list.instrument = SOM.ASG_Instrument()
    
    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** initial_wavelength_igs_lin_time_zero_to_tof"
    print "* som  :", initial_wavelength_igs_lin_time_zero_to_tof(
        som1,
        run_filter=False)
    print "* so   :", initial_wavelength_igs_lin_time_zero_to_tof(
        som1[0],
        lambda_f=l_f_i,
        time_zero_slope=t_0_s,
        time_zero_offset=t_0_o,
        dist_source_sample=d_ss,
        dist_sample_detector=d_sd,
        run_filter=False)
    print "* scal :", initial_wavelength_igs_lin_time_zero_to_tof(
        [1, 1],
        lambda_f=l_f_i,
        time_zero_slope=t_0_s,
        time_zero_offset=t_0_o,
        dist_source_sample=d_ss,
        dist_sample_detector=d_sd,
        run_filter=False)

    
