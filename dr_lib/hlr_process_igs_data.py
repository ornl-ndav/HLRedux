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

import common_lib
import dr_lib

def process_igs_data(datalist, conf, **kwargs):
    """
    This function combines Steps 1 through 8 of the data reduction process for
    Inverse Geometry Spectrometers as specified by the documenta at
    http://www.sns.gov/asg/projects/SCL/reqspec/DR_Lib_RS.doc. The function
    takes a list of file names, a Configure object and processes the data
    accordingly. This function should really only be used in the context of
    amorphous_reduction and calc_norm_eff.

    Parameters:
    ----------
    -> datalist is a list of strings containing the filenames of the data to be
       processed
    -> conf is a Configure object that contains the current setup of the
       driver
    -> kwargs is a list of key word arguments that the function accepts:
          inst_geom_dst=<DST> is a DST object that contains instrument
                              geometry information
          dataset_type=<string> is the practical name of the dataset being
                                processed. The default value is data.
          tib_const=<tuple> is a tuple providing the time-independent
                            background constant to subtract
          timer=<DiffTime> provides a DiffTime object so the function can
                           perform timing estimates

    Returns:
    -------
    <- A data SOM that has undergone all requested processing steps
    """
    import DST
    import hlr_utils

    # Check keywords
    try:
        dataset_type = kwargs["dataset_type"]
    except KeyError:
        dataset_type = "data"

    try:
        t = kwargs["timer"]
    except KeyError:
        t = None

    try:
        tib_const = kwargs["tib_const"]
    except KeyError:
        tib_const = None

    try:
        i_geom_dst = kwargs["inst_geom_dst"]
    except KeyError:
        i_geom_dst = None

    # Set output file names based on first file in list
    main_data = datalist[0]
        
    # Step 1: Open appropriate data files
    if not conf.mc:
        so_axis = "time_of_flight"
    else:
        so_axis = "Time_of_Flight__us_"

    if conf.verbose:
        print "Reading %s file" % dataset_type

    # The [0] is to get the data SOM and ignore the None background SOM
    dp_som1 = dr_lib.add_files(datalist, Data_Paths=conf.data_paths,
                               SO_Axis=so_axis, Signal_ROI=conf.roi_file,
                               dataset_type=dataset_type,
                               Verbose=conf.verbose, Timer=t)[0]

    if t is not None:
        t.getTime(msg="After reading %s " % dataset_type)

    if conf.inst_geom is not None:
        i_geom_dst.setGeometry(conf.data_paths, dp_som1)

    if conf.no_mon_norm:
        dm_som1 = None
    else:
        if conf.verbose:
            print "Reading in monitor data from %s file" % dataset_type

        # The [0] is to get the data SOM and ignore the None background SOM
        dm_som1 = dr_lib.add_files(datalist, Data_Paths=conf.mon_path,
                                   SO_Axis=so_axis,
                                   dataset_type=dataset_type,
                                   Verbose=conf.verbose,
                                   Timer=t)[0]
        
        if t is not None:
            t.getTime(msg="After reading monitor data ")

        if conf.inst_geom is not None:
            i_geom_dst.setGeometry(conf.mon_path, dm_som1)

    # Step 2: Dead Time Correction
    # No dead time correction is being applied to the data yet

    # Step 3: Time-independent background determination
    if conf.verbose and conf.tib_tofs is not None:
        print "Determining time-independent background from data"

    if t is not None and conf.tib_tofs is not None:
        t.getTime(False)
            
    B = dr_lib.determine_time_indep_bkg(dp_som1, conf.tib_tofs)

    if t is not None and B is not None:
        t.getTime(msg="After determining time-independent background ")

    if conf.dump_tib:
        attr_name = "time-independent-background"
        dp_som1.attr_list[attr_name] = B
        file_comment = "TOFs: %s" % conf.tib_tofs
        
        hlr_utils.write_file(main_data, "text/num-info", dp_som1,
                             output_ext="tib",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             message="time-independent background "\
                             +"information",
                             arguments=attr_name,
                             tag="Average",
                             units="counts",
                             comments=[file_comment])
        del dp_som1.attr_list[attr_name]

    # Step 4: Subtract time-independent background
    if conf.verbose and B is not None:
        print "Subtracting time-independent background from data"

    if t is not None:
        t.getTime(False)
            
    if B is not None:
        dp_som2 = common_lib.sub_ncerr(dp_som1, B)
    else:
        dp_som2 = dp_som1

    if B is not None and t is not None:
        t.getTime(msg="After subtracting time-independent background ")

    del dp_som1, B

    # Step 5: Subtract time-independent background constant
    if conf.verbose and tib_const is not None:
        print "Subtracting time-independent background constant from data"
            
    if t is not None and tib_const is not None:
        t.getTime(False)
                
    if tib_const is not None:
        dp_som3 = common_lib.sub_ncerr(dp_som2, tib_const)
    else:
        dp_som3 = dp_som2

    if t is not None and tib_const is not None:
        t.getTime(msg="After subtracting time-independent background "\
                  +"constant ")

    del dp_som2

    # Provide override capability for final wavelength, time-zero slope and
    # time-zero offset

    if conf.wavelength_final is not None:
        dp_som3.attr_list["Wavelength_final"] = conf.wavelength_final

    # Note: time_zero_slope MUST be a tuple
    if conf.time_zero_slope is not None:
        dp_som3.attr_list["Time_zero_slope"] = conf.time_zero_slope

    # Note: time_zero_offset MUST be a tuple
    if conf.time_zero_offset is not None:
        dp_som3.attr_list["Time_zero_offset"] = conf.time_zero_offset

    # Step 6: Convert TOF to wavelength for data and monitor
    if conf.verbose:
        print "Converting TOF to wavelength"

    if t is not None:
        t.getTime(False)

    # Convert monitor
    if dm_som1 is not None:
        dm_som2 = common_lib.tof_to_wavelength_lin_time_zero(
            dm_som1,
            units="microsecond")
    else:
        dm_som2 = None

    # Convert detector pixels
    dp_som4 = common_lib.tof_to_initial_wavelength_igs_lin_time_zero(
        dp_som3,
        units="microsecond",
        run_filter=conf.filter)

    if t is not None:
        t.getTime(msg="After converting TOF to wavelength ")

    if conf.dump_wave:
        hlr_utils.write_file(main_data, "text/Spec", dp_som4,
                             output_ext="pxl",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             message="pixel wavelength information")
    if conf.dump_mon_wave:        
        hlr_utils.write_file(main_data, "text/Spec", dm_som2,
                             output_ext="mxl",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             message="monitor wavelength information")
        
    del dp_som3, dm_som1

    # Step 7: Efficiency correct monitor
    if conf.verbose and dm_som2 is not None and not conf.no_mon_effc:
        print "Efficiency correct monitor data"

    if t is not None:
        t.getTime(False)

    if not conf.no_mon_effc:
        dm_som3 = dr_lib.feff_correct_mon(dm_som2)
    else:
        dm_som3 = dm_som2

    if t is not None and dm_som2 is not None and not conf.no_mon_effc:
        t.getTime(msg="After efficiency correcting monitor ")

    if conf.dump_mon_effc and not conf.no_mon_effc:        
        hlr_utils.write_file(main_data, "text/Spec", dm_som3,
                             output_ext="mel",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             message="monitor wavelength information "\
                             +"(efficiency)")

    del dm_som2

    # Step 8: Rebin monitor axis onto detector pixel axis
    if conf.verbose and dm_som3 is not None:
        print "Rebin monitor axis to detector pixel axis"

    if t is not None:
        t.getTime(False)

    dm_som4 = dr_lib.rebin_monitor(dm_som3, dp_som4)

    if t is not None and dm_som3 is not None:
        t.getTime(msg="After rebinning monitor ")

    del dm_som3

    if conf.dump_mon_rebin:        
        hlr_utils.write_file(main_data, "text/Spec", dm_som4,
                             output_ext="mrl",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             message="monitor wavelength information "\
                             +"(rebinned)")

    # Step 9: Normalize data by monitor
    if conf.verbose and dm_som4 is not None:
        print "Normalizing data by monitor"

    if t is not None:
        t.getTime(False)

    if dm_som4 is not None:
        dp_som5 = common_lib.div_ncerr(dp_som4, dm_som4)

        if t is not None:
            t.getTime(msg="After normalizing data by monitor ")
    else:
        dp_som5 = dp_som4

    if conf.dump_wave_mnorm:
        dp_som5_1 = dr_lib.sum_all_spectra(dp_som5,
                                           rebin_axis=conf.lambda_bins)
        hlr_utils.write_file(main_data, "text/Spec", dp_som5_1,
                             output_ext="pml",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             message="combined pixel wavelength information "\
                             +"(monitor normalized)")
        del dp_som5_1

    del dm_som4, dp_som4

    return dp_som5



