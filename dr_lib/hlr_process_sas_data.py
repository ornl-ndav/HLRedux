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

def process_sas_data(datalist, conf, **kwargs):
    """
    This function combines Steps 1 through 9 of the data reduction process for
    Small-Angle Scattering section 2.5.1 as specified by the documents at
    U{http://neutrons.ornl.gov/asg/projects/SCL/reqspec/DR_Lib_RS.doc}. The
    function takes a list of file names, a L{hlr_utils.Configure} object and
    processes the data accordingly. This function should really only be used in
    the context of I{sas_reduction}.

    @param datalist: A list containing the filenames of the data to be
    processed.
    @type datalist: C{list} of C{string}s
    
    @param conf: Object that contains the current setup of the driver.
    @type conf: L{hlr_utils.Configure}
    
    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword inst_geom_dst: File object that contains instrument geometry
                            information.
    @type inst_geom_dst: C{DST.GeomDST}
    
    @keyword dataset_type: The practical name of the dataset being processed.
                           The default value is I{data}.
    @type dataset_type: C{string}

    @keyword trans_data: Alternate data for the transmission spectrum. This is
                         used in the absence of transmission monitors.
    @type trans_data: C{string}

    @keyword transmission: A flag that signals the function to stop after
                           doing the conversion from TOF to wavelength. The
                           default is I{False}.
    @type transmission: C{boolean}

    @keyword bkg_subtract: A list of coefficients that help determine the
                           wavelength dependent background subtraction.
    @type bkg_subtract: C{list}

    @keyword get_background: A flag that signals the function to convert the
                             main data to wavelength and exit before
                             normalizing to the beam monitor.
    @type get_background: C{boolean}

    @keyword acc_down_time: The information for the accelerator downtime.
    @type acc_down_time: C{tuple}

    @keyword bkg_scale: The scaling used for the axis dependent background
                        parameters.
    @type bkg_scale: C{float}

    @keyword timer: Timing object so the function can perform timing estimates.
    @type timer: C{sns_timer.DiffTime}


    @return: Object that has undergone all requested processing steps
    @rtype: C{SOM.SOM}
    """
    import common_lib
    import dr_lib
    import hlr_utils

    # Check keywords
    try:
        dataset_type = kwargs["dataset_type"]
    except KeyError:
        dataset_type = "data"

    try:
        i_geom_dst = kwargs["inst_geom_dst"]
    except KeyError:
        i_geom_dst = None

    try:
        t = kwargs["timer"]
    except KeyError:
        t = None

    try:
        transmission = kwargs["transmission"]
    except KeyError:
        transmission = False

    try:
        bkg_subtract = kwargs["bkg_subtract"]
    except KeyError:
        bkg_subtract = None

    try:
        trans_data = kwargs["trans_data"]
    except KeyError:
        trans_data = None

    try:
        get_background = kwargs["get_background"]
    except KeyError:
        get_background = False

    acc_down_time = kwargs.get("acc_down_time")
    bkg_scale = kwargs.get("bkg_scale")

    # Add so_axis to Configure object
    conf.so_axis = "time_of_flight"

    # Step 0: Open appropriate data files

    # Data
    if conf.verbose:
        print "Reading %s file" % dataset_type

    # The [0] is to get the data SOM and ignore the None background SOM
    dp_som = dr_lib.add_files(datalist, Data_Paths=conf.data_paths.toPath(),
                              SO_Axis=conf.so_axis, Signal_ROI=conf.roi_file,
                              dataset_type=dataset_type,
                              Verbose=conf.verbose, Timer=t)
    
    if t is not None:
        t.getTime(msg="After reading %s " % dataset_type)

    dp_som1 = dr_lib.fix_bin_contents(dp_som)

    del dp_som

    if conf.inst_geom is not None:
        i_geom_dst.setGeometry(conf.data_paths.toPath(), dp_som1)

    if conf.dump_tof_r:
        dp_som1_1 = dr_lib.create_param_vs_Y(dp_som1, "radius", "param_array",
                                             conf.r_bins.toNessiList(),
                                             y_label="counts",
                                             y_units="counts / (usec * m)",
                                             x_labels=["Radius", "TOF"], 
                                             x_units=["m", "usec"])

        hlr_utils.write_file(conf.output, "text/Dave2d", dp_som1_1,
                             output_ext="tvr",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             data_ext=conf.ext_replacement,
                             path_replacement=conf.path_replacement,
                             message="TOF vs radius information")

        del dp_som1_1

    if conf.dump_tof_theta:
        dp_som1_1 = dr_lib.create_param_vs_Y(dp_som1, "polar", "param_array",
                                             conf.theta_bins.toNessiList(),
                                             y_label="counts",
                                             y_units="counts / (usec * rads)",
                                             x_labels=["Polar Angle", "TOF"], 
                                             x_units=["rads", "usec"])

        hlr_utils.write_file(conf.output, "text/Dave2d", dp_som1_1,
                             output_ext="tvt",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             data_ext=conf.ext_replacement,
                             path_replacement=conf.path_replacement,
                             message="TOF vs polar angle information")        

        del dp_som1_1
        
    # Beam monitor
    if not get_background:
        if conf.beammon_over is None:
            if conf.verbose:
                print "Reading in beam monitor data from %s file" \
                      % dataset_type

                # The [0] is to get the data SOM and ignore the None
                # background SOM
                dbm_som0 = dr_lib.add_files(datalist,
                                            Data_Paths=conf.bmon_path.toPath(),
                                            SO_Axis=conf.so_axis,
                                            dataset_type=dataset_type,
                                            Verbose=conf.verbose,
                                            Timer=t)
            
                if t is not None:
                    t.getTime(msg="After reading beam monitor data ")

                if conf.inst_geom is not None:
                    i_geom_dst.setGeometry(conf.bmon_path.toPath(), dbm_som0)
        else:
            if conf.verbose:
                print "Reading in vanadium data"

                dbm_som0 = dr_lib.add_files(datalist,
                                          Data_Paths=conf.data_paths.toPath(),
                                            Signal_ROI=conf.roi_file,
                                            SO_Axis=conf.so_axis,
                                            dataset_type=dataset_type,
                                            Verbose=conf.verbose,
                                            Timer=t)
                if t is not None:
                    t.getTime(msg="After reading vanadium data ")

                if conf.inst_geom is not None:
                    i_geom_dst.setGeometry(conf.data_paths.toPath(), dbm_som0)


        dbm_som1 = dr_lib.fix_bin_contents(dbm_som0)
        
        del dbm_som0
    else:
        dbm_som1 = None

    # Transmission monitor
    if trans_data is None:
        if conf.verbose:
            print "Reading in transmission monitor data from %s file" \
                  % dataset_type
        try:
            dtm_som0 = dr_lib.add_files(datalist,
                                        Data_Paths=conf.tmon_path.toPath(),
                                        SO_Axis=conf.so_axis,
                                        dataset_type=dataset_type,
                                        Verbose=conf.verbose,
                                        Timer=t)
            if t is not None:
                t.getTime(msg="After reading transmission monitor data ")

                if conf.inst_geom is not None:
                    i_geom_dst.setGeometry(conf.tmon_path.toPath(), dtm_som0)
                    
            dtm_som1 = dr_lib.fix_bin_contents(dtm_som0)
                
            del dtm_som0
        # Transmission monitor cannot be found
        except KeyError:
            if conf.verbose:
                print "Transmission monitor not found"
            dtm_som1 = None
    else:
        dtm_som1 = None

    # Note: time_zero_offset_det MUST be a tuple
    if conf.time_zero_offset_det is not None:
        dp_som1.attr_list["Time_zero_offset_det"] = \
                                     conf.time_zero_offset_det.toValErrTuple()
    # Note: time_zero_offset_mon MUST be a tuple
    if conf.time_zero_offset_mon is not None and not get_background and \
           conf.beammon_over is None:
        dbm_som1.attr_list["Time_zero_offset_mon"] = \
                                     conf.time_zero_offset_mon.toValErrTuple()
    if conf.beammon_over is not None:
        dbm_som1.attr_list["Time_zero_offset_det"] = \
                                     conf.time_zero_offset_det.toValErrTuple()
    if trans_data is None and dtm_som1 is not None:
        dtm_som1.attr_list["Time_zero_offset_mon"] = \
                                     conf.time_zero_offset_mon.toValErrTuple()

    # Step 1: Convert TOF to wavelength for data and monitor
    if conf.verbose:
        print "Converting TOF to wavelength"

    if t is not None:
        t.getTime(False)

    if not get_background:
        # Convert beam monitor
        if conf.beammon_over is None:
            dbm_som2 = common_lib.tof_to_wavelength_lin_time_zero(
                dbm_som1,
                units="microsecond",
                time_zero_offset=conf.time_zero_offset_mon.toValErrTuple())
        else:
            dbm_som2 = common_lib.tof_to_wavelength_lin_time_zero(
                dbm_som1,
                units="microsecond",
                time_zero_offset=conf.time_zero_offset_det.toValErrTuple(),
                inst_param="total")
    else:
        dbm_som2 = None

    # Convert detector pixels
    dp_som2 = common_lib.tof_to_wavelength_lin_time_zero(
        dp_som1,
        units="microsecond",
        time_zero_offset=conf.time_zero_offset_det.toValErrTuple(),
        inst_param="total")

    if get_background:
        return dp_som2

    if dtm_som1 is not None:
        # Convert transmission  monitor
        dtm_som2 = common_lib.tof_to_wavelength_lin_time_zero(
            dtm_som1,
            units="microsecond",
            time_zero_offset=conf.time_zero_offset_mon.toValErrTuple())
    else:
        dtm_som2 = dtm_som1
        
    if t is not None:
        t.getTime(msg="After converting TOF to wavelength ")

    del dp_som1, dbm_som1, dtm_som1

    if conf.verbose and (conf.lambda_low_cut is not None or \
                         conf.lambda_high_cut is not None):
        print "Cutting data spectra"

    if t is not None:
        t.getTime(False)

    dp_som3 = dr_lib.cut_spectra(dp_som2, conf.lambda_low_cut,
                                 conf.lambda_high_cut)

    if t is not None:
        t.getTime(msg="After cutting data spectra ")

    del dp_som2

    if conf.beammon_over is not None:
        dbm_som2 = dr_lib.cut_spectra(dbm_som2, conf.lambda_low_cut,
                                       conf.lambda_high_cut)
        
    if conf.dump_wave:
        hlr_utils.write_file(conf.output, "text/Spec", dp_som3,
                             output_ext="pxl",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             data_ext=conf.ext_replacement,
                             path_replacement=conf.path_replacement,
                             message="pixel wavelength information")
    if conf.dump_bmon_wave:
        if conf.beammon_over is None:
            hlr_utils.write_file(conf.output, "text/Spec", dbm_som2,
                                 output_ext="bmxl",
                                 extra_tag=dataset_type,
                                 verbose=conf.verbose,
                                 data_ext=conf.ext_replacement,
                                 path_replacement=conf.path_replacement,
                                 message="beam monitor wavelength information")
        else:
            
            dbm_som2_1 = dr_lib.sum_by_rebin_frac(dbm_som2,
                                               conf.lambda_bins.toNessiList())
            hlr_utils.write_file(conf.output, "text/Spec", dbm_som2_1,
                                 output_ext="bmxl",
                                 extra_tag=dataset_type,
                                 verbose=conf.verbose,
                                 data_ext=conf.ext_replacement,
                                 path_replacement=conf.path_replacement,
                                 message="beam monitor override wavelength "\
                                 +"information")
            del dbm_som2_1

    # Step 2: Subtract wavelength dependent background if necessary
    if conf.verbose and bkg_subtract is not None:
        print "Subtracting wavelength dependent background"
        
    if bkg_subtract is not None:
        if t is not None:
            t.getTime(False)

        duration = dp_som3.attr_list["%s-duration" % dataset_type]
        scale = duration.getValue() - acc_down_time[0]
            
        dp_som4 = dr_lib.subtract_axis_dep_bkg(dp_som3, bkg_subtract,
                                               old_scale=bkg_scale,
                                               new_scale=scale)

        if t is not None:
            t.getTime(msg="After subtracting wavelength dependent background ")
    else:
        dp_som4 = dp_som3

    del dp_som3

    # Step 3: Efficiency correct beam monitor
    if conf.verbose and conf.mon_effc:
        print "Efficiency correct beam monitor data"

    if t is not None:
        t.getTime(False)

    if conf.mon_effc:
        dbm_som3 = dr_lib.feff_correct_mon(dbm_som2, inst_name=conf.inst,
                                           eff_const=conf.mon_eff_const)
    else:
        dbm_som3 = dbm_som2

    if t is not None and conf.mon_effc:
        t.getTime(msg="After efficiency correcting beam monitor ")

    if conf.dump_bmon_effc and conf.mon_effc:   
        hlr_utils.write_file(conf.output, "text/Spec", dbm_som3,
                             output_ext="bmel",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             data_ext=conf.ext_replacement,
                             path_replacement=conf.path_replacement,
                             message="beam monitor wavelength information "\
                             +"(efficiency)")

    del dbm_som2

    # Step 4: Efficiency correct transmission monitor    
    if dtm_som2 is not None:
        if conf.verbose and conf.mon_effc:
            print "Efficiency correct transmission monitor data"

        if t is not None:
            t.getTime(False)

        if conf.mon_effc:
            dtm_som3 = dr_lib.feff_correct_mon(dtm_som2)
        else:
            dtm_som3 = dtm_som2
    else:
        dtm_som3 = dtm_som2            

    if t is not None and conf.mon_effc and dtm_som2 is not None:
        t.getTime(msg="After efficiency correcting beam monitor ")

    # Step 5: Efficiency correct detector pixels
    if conf.det_effc:
        if conf.verbose:
            print "Calculating detector efficiency"

        if t is not None:
            t.getTime(False)

        det_eff = dr_lib.create_det_eff(dp_som4, inst_name=conf.inst,
                                      eff_scale_const=conf.det_eff_scale_const,
                                      eff_atten_const=conf.det_eff_atten_const)

        if t is not None:
            t.getTime(msg="After calculating detector efficiency")

        if conf.verbose:
            print "Applying detector efficiency"

        if t is not None:
            t.getTime(False)

        dp_som5 = common_lib.div_ncerr(dp_som4, det_eff)

        if t is not None:
            t.getTime(msg="After spplying detector efficiency")

    else:
        dp_som5 = dp_som4

    del dp_som4

    # Step 6: Rebin beam monitor axis onto detector pixel axis
    if conf.beammon_over is None:
        if not conf.no_bmon_norm:
            if conf.verbose:
                print "Rebin beam monitor axis to detector pixel axis"

            if t is not None:
                t.getTime(False)

            dbm_som4 = dr_lib.rebin_monitor(dbm_som3, dp_som5, rtype="frac")

            if t is not None:
                t.getTime(msg="After rebinning beam monitor ")
        else:
            dbm_som4 = dbm_som3
    else:
        dbm_som4 = dbm_som3

    del dbm_som3

    if conf.dump_bmon_rebin:
        hlr_utils.write_file(conf.output, "text/Spec", dbm_som4,
                             output_ext="bmrl",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             data_ext=conf.ext_replacement,
                             path_replacement=conf.path_replacement,
                             message="beam monitor wavelength information "\
                             +"(rebinned)")

    # Step 7: Normalize data by beam monitor
    if not conf.no_bmon_norm:
        if conf.verbose:
            print "Normalizing data by beam monitor"

        if t is not None:
            t.getTime(False)

        dp_som6 = common_lib.div_ncerr(dp_som5, dbm_som4)

        if t is not None:
            t.getTime(msg="After normalizing data by beam monitor ")
    else:
        dp_som6 = dp_som5

    del dp_som5

    if transmission:
        return dp_som6

    if conf.dump_wave_bmnorm:
        dp_som6_1 = dr_lib.sum_by_rebin_frac(dp_som6,
                                             conf.lambda_bins.toNessiList())

        write_message = "combined pixel wavelength information"
        write_message += " (beam monitor normalized)"
        
        hlr_utils.write_file(conf.output, "text/Spec", dp_som6_1,
                             output_ext="pbml",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             data_ext=conf.ext_replacement,
                             path_replacement=conf.path_replacement,
                             message=write_message)
        del dp_som6_1

    if conf.dump_wave_r:
        dp_som6_1 = dr_lib.create_param_vs_Y(dp_som6, "radius", "param_array",
                                   conf.r_bins.toNessiList(),
                                   rebin_axis=conf.lambda_bins.toNessiList(),
                                   y_label="counts",
                                   y_units="counts / (Angstrom * m)",
                                   x_labels=["Radius", "Wavelength"], 
                                   x_units=["m", "Angstrom"])

        hlr_utils.write_file(conf.output, "text/Dave2d", dp_som6_1,
                             output_ext="lvr",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             data_ext=conf.ext_replacement,
                             path_replacement=conf.path_replacement,
                             message="wavelength vs radius information")

        del dp_som6_1

    if conf.dump_wave_theta:
        dp_som6_1 = dr_lib.create_param_vs_Y(dp_som6, "polar", "param_array",
                                   conf.theta_bins.toNessiList(),
                                   rebin_axis=conf.lambda_bins.toNessiList(),
                                   y_label="counts",
                                   y_units="counts / (Angstrom * rads)",
                                   x_labels=["Polar Angle", "Wavelength"], 
                                   x_units=["rads", "Angstrom"])

        hlr_utils.write_file(conf.output, "text/Dave2d", dp_som6_1,
                             output_ext="lvt",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             data_ext=conf.ext_replacement,
                             path_replacement=conf.path_replacement,
                             message="wavelength vs polar angle information") 

        del dp_som6_1

    # Step 8: Rebin transmission monitor axis onto detector pixel axis
    if trans_data is not None:
        print "Reading in transmission monitor data from file"

        dtm_som3 = dr_lib.add_files([trans_data],
                                    dataset_type=dataset_type,
                                    dst_type="text/Spec",
                                    Verbose=conf.verbose,
                                    Timer=t)

    
    if conf.verbose and dtm_som3 is not None:
        print "Rebin transmission monitor axis to detector pixel axis"
        
    if t is not None:
        t.getTime(False)

    dtm_som4 = dr_lib.rebin_monitor(dtm_som3, dp_som6, rtype="frac")

    if t is not None and dtm_som3 is not None:
        t.getTime(msg="After rebinning transmission monitor ")

    del dtm_som3

    # Step 9: Normalize data by transmission monitor    
    if conf.verbose and dtm_som4 is not None:
        print "Normalizing data by transmission monitor"

    if t is not None:
        t.getTime(False)

    if dtm_som4 is not None:
        # The transmission spectra derived from sas_tranmission does not have
        # the same y information by convention as sample data or a
        # tranmission monitor. Therefore, we'll fake it by setting the
        # y information from the sample data into the transmission
        if trans_data is not None:
            dtm_som4.setYLabel(dp_som6.getYLabel())
            dtm_som4.setYUnits(dp_som6.getYUnits())
        dp_som7 = common_lib.div_ncerr(dp_som6, dtm_som4)
    else:
        dp_som7 = dp_som6

    if t is not None and dtm_som4 is not None:
        t.getTime(msg="After normalizing data by transmission monitor ")

    del dp_som6

    # Step 10: Convert wavelength to Q for data
    if conf.verbose:
        print "Converting data from wavelength to scalar Q"
    
    if t is not None:
        t.getTime(False)

    dp_som8 = common_lib.wavelength_to_scalar_Q(dp_som7)

    if t is not None:
        t.getTime(msg="After converting wavelength to scalar Q ")
        
    del dp_som7

    if conf.facility == "LENS":
        # Step 11: Apply SAS correction factor to data
        if conf.verbose:
            print "Applying geometrical correction"

        if t is not None:
            t.getTime(False)

        dp_som9 = dr_lib.apply_sas_correct(dp_som8)

        if t is not None:
            t.getTime(msg="After applying geometrical correction ")

        return dp_som9
    else:
        return dp_som8
