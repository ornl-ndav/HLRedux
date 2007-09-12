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
    Inverse Geometry Spectrometers as specified by the documents at
    U{http://neutrons.ornl.gov/asg/projects/SCL/reqspec/DR_Lib_RS.doc}. The
    function takes a list of file names, a L{hlr_utils.Configure} object and
    processes the data accordingly. This function should really only be used in
    the context of I{amorphous_reduction} and I{calc_norm_eff}.

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
    
    @keyword tib_const: Object providing the time-independent background
    constant to subtract.
    @type tib_const: L{hlr_utils.DrParameter}

    @keyword bkg_som: Object that will be used for early background subtraction
    @type bkg_som: C{SOM.SOM}
    
    @keyword timer: Timing object so the function can perform timing estimates.
    @type timer: C{sns_timer.DiffTime}


    @return: Object that has undergone all requested processing steps
    @rtype: C{SOM.SOM}
    """
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
        if kwargs["tib_const"] is not None:
            tib_const = kwargs["tib_const"].toValErrTuple()
        else:
            tib_const = None
    except KeyError:
        tib_const = None

    try:
        i_geom_dst = kwargs["inst_geom_dst"]
    except KeyError:
        i_geom_dst = None

    try:
        bkg_som = kwargs["bkg_som"]
    except KeyError:
        bkg_som = None    

    # Step 1: Open appropriate data files
    if not conf.mc:
        so_axis = "time_of_flight"
    else:
        so_axis = "Time_of_Flight"

    # Add so_axis to Configure object
    conf.so_axis = so_axis

    if conf.verbose:
        print "Reading %s file" % dataset_type

    # The [0] is to get the data SOM and ignore the None background SOM
    dp_som1 = dr_lib.add_files(datalist, Data_Paths=conf.data_paths.toPath(),
                               SO_Axis=so_axis, Signal_ROI=conf.roi_file,
                               dataset_type=dataset_type,
                               Verbose=conf.verbose, Timer=t)[0]

    if t is not None:
        t.getTime(msg="After reading %s " % dataset_type)

    if conf.inst_geom is not None:
        i_geom_dst.setGeometry(conf.data_paths.toPath(), dp_som1)

    if conf.no_mon_norm:
        dm_som1 = None
    else:
        if conf.verbose:
            print "Reading in monitor data from %s file" % dataset_type

        # The [0] is to get the data SOM and ignore the None background SOM
        dm_som1 = dr_lib.add_files(datalist, Data_Paths=conf.mon_path.toPath(),
                                   SO_Axis=so_axis,
                                   dataset_type=dataset_type,
                                   Verbose=conf.verbose,
                                   Timer=t)[0]
        
        if t is not None:
            t.getTime(msg="After reading monitor data ")

        if conf.inst_geom is not None:
            i_geom_dst.setGeometry(conf.mon_path.toPath(), dm_som1)


    if bkg_som is not None:
        bkg_pcharge = bkg_som.attr_list["background-proton_charge"].getValue()
        data_pcharge = dp_som1.attr_list[dataset_type+
                                         "-proton_charge"].getValue()

        ratio = data_pcharge / bkg_pcharge

        bkg_som1 = common_lib.mult_ncerr(bkg_som, (ratio, 0.0))
        
        del bkg_som

        dp_som2 = dr_lib.subtract_bkg_from_data(dp_som1, bkg_som1,
                                                verbose=conf.verbose,
                                                timer=t,
                                                dataset1=dataset_type,
                                                dataset2="background")
        
    else:
        dp_som2 = dp_som1

    del dp_som1

    # Step 2: Dead Time Correction
    # No dead time correction is being applied to the data yet

    # Step 3: Time-independent background determination
    if conf.verbose and conf.tib_tofs is not None:
        print "Determining time-independent background from data"

    if t is not None and conf.tib_tofs is not None:
        t.getTime(False)
            
    B = dr_lib.determine_time_indep_bkg(dp_som2, conf.tib_tofs)

    if t is not None and B is not None:
        t.getTime(msg="After determining time-independent background ")

    if conf.dump_tib and B is not None:
        attr_name = "time-independent-background"
        dp_som2.attr_list[attr_name] = B
        file_comment = "TOFs: %s" % conf.tib_tofs
        
        hlr_utils.write_file(conf.output, "text/num-info", dp_som2,
                             output_ext="tib",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             data_ext=conf.ext_replacement,
                             path_replacement=conf.path_replacement,
                             message="time-independent background "\
                             +"information",
                             arguments=attr_name,
                             tag="Average",
                             units="counts",
                             comments=[file_comment])
        del dp_som2.attr_list[attr_name]

    # Step 4: Subtract time-independent background
    if conf.verbose and B is not None:
        print "Subtracting time-independent background from data"

    if t is not None:
        t.getTime(False)
            
    if B is not None:
        dp_som3 = common_lib.sub_ncerr(dp_som2, B)
    else:
        dp_som3 = dp_som2

    if B is not None and t is not None:
        t.getTime(msg="After subtracting time-independent background ")

    del dp_som2, B

    # Step 5: Subtract time-independent background constant
    if conf.verbose and tib_const is not None:
        print "Subtracting time-independent background constant from data"
            
    if t is not None and tib_const is not None:
        t.getTime(False)
                
    if tib_const is not None:
        dp_som4 = common_lib.sub_ncerr(dp_som3, tib_const)
    else:
        dp_som4 = dp_som3

    if t is not None and tib_const is not None:
        t.getTime(msg="After subtracting time-independent background "\
                  +"constant ")

    del dp_som3

    # Provide override capability for final wavelength, time-zero slope and
    # time-zero offset

    if conf.wavelength_final is not None:
        dp_som4.attr_list["Wavelength_final"] = \
                                     conf.wavelength_final.toValErrTuple()

    # Note: time_zero_slope MUST be a tuple
    if conf.time_zero_slope is not None:
        dp_som4.attr_list["Time_zero_slope"] = \
                                     conf.time_zero_slope.toValErrTuple()

    # Note: time_zero_offset MUST be a tuple
    if conf.time_zero_offset is not None:
        dp_som4.attr_list["Time_zero_offset"] = \
                                     conf.time_zero_offset.toValErrTuple()

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
    dp_som5 = common_lib.tof_to_initial_wavelength_igs_lin_time_zero(
        dp_som4,
        units="microsecond",
        run_filter=conf.filter)

    if t is not None:
        t.getTime(msg="After converting TOF to wavelength ")

    if conf.dump_wave:
        hlr_utils.write_file(conf.output, "text/Spec", dp_som5,
                             output_ext="pxl",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             data_ext=conf.ext_replacement,
                             path_replacement=conf.path_replacement,
                             message="pixel wavelength information")
    if conf.dump_mon_wave:        
        hlr_utils.write_file(conf.output, "text/Spec", dm_som2,
                             output_ext="mxl",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             data_ext=conf.ext_replacement,
                             path_replacement=conf.path_replacement,
                             message="monitor wavelength information")
        
    del dp_som4, dm_som1

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
        hlr_utils.write_file(conf.output, "text/Spec", dm_som3,
                             output_ext="mel",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             data_ext=conf.ext_replacement,
                             path_replacement=conf.path_replacement,
                             message="monitor wavelength information "\
                             +"(efficiency)")

    del dm_som2

    # Step 8: Rebin monitor axis onto detector pixel axis
    if conf.verbose and dm_som3 is not None:
        print "Rebin monitor axis to detector pixel axis"

    if t is not None:
        t.getTime(False)

    dm_som4 = dr_lib.rebin_monitor(dm_som3, dp_som5)

    if t is not None and dm_som3 is not None:
        t.getTime(msg="After rebinning monitor ")

    del dm_som3

    if conf.dump_mon_rebin:        
        hlr_utils.write_file(conf.output, "text/Spec", dm_som4,
                             output_ext="mrl",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             data_ext=conf.ext_replacement,
                             path_replacement=conf.path_replacement,
                             message="monitor wavelength information "\
                             +"(rebinned)")

    # Step 9: Normalize data by monitor
    if conf.verbose and dm_som4 is not None:
        print "Normalizing data by monitor"

    if t is not None:
        t.getTime(False)

    if dm_som4 is not None:
        dp_som6 = common_lib.div_ncerr(dp_som5, dm_som4)

        if t is not None:
            t.getTime(msg="After normalizing data by monitor ")
    else:
        dp_som6 = dp_som5

    if conf.dump_wave_mnorm:
        dp_som6_1 = dr_lib.sum_all_spectra(dp_som6,\
                                   rebin_axis=conf.lambda_bins.toNessiList())
        
        hlr_utils.write_file(conf.output, "text/Spec", dp_som6_1,
                             output_ext="pml",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             data_ext=conf.ext_replacement,
                             path_replacement=conf.path_replacement,
                             message="combined pixel wavelength information "\
                             +"(monitor normalized)")
        del dp_som6_1

    del dm_som4, dp_som5

    return dp_som6



