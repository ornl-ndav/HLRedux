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

def calibrate_dgs_data(datalist, conf, dkcur, **kwargs):
    """
    This function combines Steps 3 through 6 in Section 2.1.1 of the data
    reduction process for Direct Geometry Spectrometers as specified by the
    document at 
    U{http://neutrons.ornl.gov/asg/projects/SCL/reqspec/DR_Lib_RS.doc}. The
    function takes a list of file names, a L{hlr_utils.Configure} object and
    processes the data accordingly.
    
    @param datalist: A list containing the filenames of the data to be
                     processed.
    @type datalist: C{list} of C{string}s
    
    @param conf: Object that contains the current setup of the driver.
    @type conf: L{hlr_utils.Configure}

    @param dkcur: The object containing the TOF dark current data.
    @type dkcur: C{SOM.SOM}
    
    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword inst_geom_dst: File object that contains instrument geometry
                            information.
    @type inst_geom_dst: C{DST.GeomDST}

    @keyword tib_const: A time-independent background constant to subtract
                        from every pixel.
    @type tib_const: L{hlr_utils.DrParameter}
    
    @keyword dataset_type: The practical name of the dataset being processed.
                           The default value is I{data}.
    @type dataset_type: C{string}

    @keyword cwp: A list of chopper phase corrections in units of microseconds.
    @type cwp: C{list} of C{float}s
    
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
        tib_const = kwargs["tib_const"]
    except KeyError:
        tib_const = None
    
    try:
        dataset_type = kwargs["dataset_type"]
    except KeyError:
        dataset_type = "data"

    try:
        t = kwargs["timer"]
    except KeyError:
        t = None

    try:
        i_geom_dst = kwargs["inst_geom_dst"]
    except KeyError:
        i_geom_dst = None

    dataset_cwp = kwargs.get("cwp")

    # Open the appropriate datafiles
    if conf.verbose:
        print "Reading %s file" % dataset_type

    data_paths = conf.data_paths.toPath()
    if conf.no_mon_norm:
        mon_paths = None
    else:
        mon_paths = conf.usmon_path.toPath()

    # Check for mask file since normalization drive doesn't understand option
    try:
        mask_file = conf.mask_file
    except AttributeError:
        mask_file = None

    if t is not None:
        oldtime = t.getOldTime()

    (dp_som0, dm_som0) = dr_lib.add_files_dm(datalist, Data_Paths=data_paths,
                                             Mon_Paths=mon_paths,
                                             SO_Axis=conf.so_axis,
                                             Signal_ROI=conf.roi_file,
                                             Signal_MASK=mask_file,
                                             dataset_type=dataset_type,
                                             dataset_cwp=dataset_cwp,
                                             Verbose=conf.verbose, Timer=t)

    if t is not None:
        t.setOldTime(oldtime)
        t.getTime(msg="After reading %s file" % dataset_type)

    # Cut the spectra if necessary
    dp_somA = dr_lib.cut_spectra(dp_som0, conf.tof_cut_min, conf.tof_cut_max)

    del dp_som0

    dp_somB = dr_lib.fix_bin_contents(dp_somA)

    del dp_somA

    if dp_somB.attr_list.instrument.get_name() != "CNCS":

        if conf.verbose:
            print "Cutting spectrum at minimum TOF"
        
        if t is not None:
            t.getTime(False)

        # Calculate minimum TOF for physical neutrons
        if conf.initial_energy is not None:
            initial_wavelength = common_lib.energy_to_wavelength(\
            conf.initial_energy.toValErrTuple())
            initial_velocity = common_lib.wavelength_to_velocity(\
            initial_wavelength)
        else:
            # This should actually calculate it, but don't have a way right now
            pass

        if conf.time_zero_offset is not None:
            time_zero_offset = conf.time_zero_offset.toValErrTuple()
        else:
            # This should actually calculate it, but don't have a way right now
            time_zero_offset = (0.0, 0.0)

        ss_length = dp_somB.attr_list.instrument.get_primary()
        
        tof_min = (ss_length[0] / initial_velocity[0]) + time_zero_offset[0]

        # Cut all spectra a the minimum TOF
        dp_som1 = dr_lib.cut_spectra(dp_somB, tof_min, None)

        if t is not None:
            t.getTime(msg="After cutting spectrum at minimum TOF ")
    else:
        dp_som1 = dp_somB

    del dp_somB

    if dm_som0 is not None:
        dm_som1 = dr_lib.fix_bin_contents(dm_som0)
    else:
        dm_som1 = dm_som0

    del dm_som0    

    # Override geometry if necessary
    if conf.inst_geom is not None:
        i_geom_dst.setGeometry(data_paths, dp_som1)

    if conf.inst_geom is not None and dm_som1 is not None:
        i_geom_dst.setGeometry(mon_paths, dm_som1)
    
    # Step 3: Integrate the upstream monitor
    if dm_som1 is not None:
        if conf.verbose:
            print "Integrating upstream monitor spectrum"

        if t is not None:
            t.getTime(False)
        
        if conf.mon_int_range is None:
            start_val = float("inf")
            end_val = float("inf")
        else:
            start_val = conf.mon_int_range[0]
            end_val = conf.mon_int_range[1]
        
        dm_som2 = dr_lib.integrate_spectra(dm_som1, start=start_val,
                                           end=end_val,
                                           width=True)
        if t is not None:
            t.getTime(msg="After integrating upstream monitor spectrum ")
    else:
        dm_som2 = dm_som1

    del dm_som1

    tib_norm_const = None
    
    # Step 4: Divide data set by summed monitor spectrum
    if dm_som2 is not None:
        if conf.verbose:
            print "Normalizing %s by monitor sum" % dataset_type

        if t is not None:
            t.getTime(False)

        dp_som2 = common_lib.div_ncerr(dp_som1, dm_som2, length_one_som=True)

        tib_norm_const = dm_som2[0].y

        if t is not None:
            t.getTime(msg="After normalizing %s by monitor sum" % dataset_type)

    elif conf.pc_norm:
        if conf.verbose:
            print "Normalizing %s by proton charge" % dataset_type

        pc_tag = dataset_type+"-proton_charge"
        pc = dp_som1.attr_list[pc_tag]

        # Scale the proton charge and then set the scale PC back to attributes
        if conf.scale_pc is not None:
            if conf.verbose:
                print "Scaling %s proton charge" % dataset_type

            pc = hlr_utils.scale_proton_charge(pc, conf.scale_pc)
            dp_som1.attr_list[pc_tag] = pc

        tib_norm_const = pc.getValue()

        if t is not None:
            t.getTime(False)

        dp_som2 = common_lib.div_ncerr(dp_som1, (pc.getValue(), 0.0))

        if t is not None:
            t.getTime(msg="After normalizing %s by proton charge" \
                      % dataset_type)

    else:
        dp_som2 = dp_som1

    del dp_som1, dm_som2

    # Step 5: Scale dark current by data set measurement time
    if dkcur is not None:
        if conf.verbose:
            print "Scaling dark current by %s acquisition time" % dataset_type

        if t is not None:
            t.getTime(False)

        dstime_tag = dataset_type+"-duration"
        dstime = dp_som2.attr_list[dstime_tag]

        dkcur1 = common_lib.div_ncerr(dkcur, (dstime.getValue(), 0.0))

        if t is not None:
            t.getTime(msg="After scaling dark current by %s acquisition time" \
                      % dataset_type)        
    else:
        dkcur1 = dkcur

    del dkcur

    # Step 6: Subtract scaled dark current from data set
    if dkcur1 is not None:
        if conf.verbose:
            print "Subtracting %s by scaled dark current" % dataset_type

        if t is not None:
            t.getTime(False)

        dp_som3 = common_lib.sub_ncerr(dp_som2, dkcur1)

        if t is not None:
            t.getTime(msg="After subtracting %s by scaled dark current" \
                      % dataset_type)
    elif tib_const is not None and dkcur1 is None:
        if conf.verbose:
            print "Subtracting TIB constant from %s" % dataset_type

        # Normalize the TIB constant by dividing by the current normalization
        # the duration (if necessary) and the conversion from seconds to
        # microseconds
        tib_c = tib_const.toValErrTuple()

        conv_sec_to_usec = 1.0e-6

        if tib_norm_const is None:
            tib_norm_const = 1
            duration = 1
        else:
            duration_tag = dataset_type+"-duration"
            duration = dp_som2.attr_list[duration_tag].getValue()

        norm_const = (duration * conv_sec_to_usec) / tib_norm_const

        tib_val = tib_c[0] * norm_const
        tib_err2 = tib_c[1] * (norm_const * norm_const)

        if t is not None:
            t.getTime(False)
  
        dp_som3 = common_lib.sub_ncerr(dp_som2, (tib_val, tib_err2))

        if t is not None:
            t.getTime(msg="After subtracting TIB constant from %s" \
                      % dataset_type)
    elif conf.tib_range is not None and dkcur1 is None:
        if conf.verbose:
            print "Determining TIB constant from %s" % dataset_type

        if t is not None:
            t.getTime(False)

        TIB = dr_lib.determine_time_indep_bkg(dp_som2, conf.tib_range,
                                              is_range=True)

        if t is not None:
            t.getTime(msg="After determining TIB constant from %s" \
                      % dataset_type)

        if conf.dump_tib:
            file_comment = "TIB TOF Range: [%d, %d]" % (conf.tib_range[0],
                                                        conf.tib_range[1])
        
            hlr_utils.write_file(conf.output, "text/num-info", TIB,
                                 output_ext="tib",
                                 extra_tag=dataset_type,
                                 verbose=conf.verbose,
                                 data_ext=conf.ext_replacement,
                                 path_replacement=conf.path_replacement,
                                 message="time-independent background "\
                                 +"information",
                                 tag="Average TIB",
                                 units="counts/usec",
                                 comments=[file_comment])
            
        if conf.verbose:
            print "Subtracting TIB constant from %s" % dataset_type

        if t is not None:
            t.getTime(False)

        dp_som3 = common_lib.sub_ncerr(dp_som2, TIB)

        if t is not None:
            t.getTime(msg="After subtracting TIB constant from %s" \
                      % dataset_type)

        del TIB
    else:
        dp_som3 = dp_som2

    del dp_som2, dkcur1

    if conf.dump_ctof_comb:
        dp_som3_1 = dr_lib.sum_all_spectra(dp_som3)
        hlr_utils.write_file(conf.output, "text/Spec", dp_som3_1,
                             output_ext="ctof",
                             extra_tag=dataset_type,
                             data_ext=conf.ext_replacement,    
                             path_replacement=conf.path_replacement,
                             verbose=conf.verbose,
                             message="combined calibrated TOF information")
        
        del dp_som3_1
    
    return dp_som3
