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
        i_geom_dst = kwargs["inst_geom_dst"]
    except KeyError:
        i_geom_dst = None
        
    # Step 1: Open appropriate data files
    try:
        data_dst = DST.getInstance("application/x-NeXus", datalist)
    except SystemError:
        print "ERROR: Failed to read file %s" % datalist
        sys.exit(-1)

    if not conf.mc:
        so_axis = "time_of_flight"
    else:
        so_axis = "Time_of_Flight__us_"

    if conf.verbose:
        print "Reading %s file" % dataset_type

    dp_som1 = data_dst.getSOM(conf.data_paths, so_axis,
                              roi_file=conf.roi_file)

    if t is not None:
        t.getTime(msg="After reading %s " % dataset_type)

    if conf.inst_geom is not None:
        i_geom_dst.setGeometry(conf.data_paths, dp_som1)

    if conf.no_mon_norm:
        dm_som1 = None
    else:
        if conf.verbose:
            print "Reading in monitor data from %s file" % dataset_type
        som_id = conf.mon_path
        dm_som1 = data_dst.getSOM(som_id, so_axis)
        
        if t is not None:
            t.getTime(msg="After reading monitor data ")

        if conf.inst_geom is not None:
            i_geom_dst.setGeometry(conf.mon_path, dm_som1)

    data_dst.release_resource()

    # Step 2: Dead Time Correction
    # No dead time correction is being applied to the data yet

    # Step 3: Time-independent background determination
    if not conf.no_tib:
        if conf.verbose:
            print "Determining time-independent background from data"
            
        B = determine_time_indep_bkg(conf, dp_som1)
        if t is not None:
            t.getTime(msg="After determining time-independent background ")
    else:
        B = None

    # Step 4: Subtract time-independent background
    if conf.verbose and B is not None:
        print "Subtracting time-independent background from data"
        
    dp_som2 = subtract_time_indep_bkg(dp_som1, B)

    if B is not None:
        if t is not None:
            t.getTime(msg="After subtracting time-independent background ")

    del dp_som1, B

    # Provide override capability for final wavelength, time-zero slope and
    # time-zero offset

    if conf.wavelength_final is not None:
        dp_som1.attr_list["Wavelength_final"] = conf.wavelength_final

    # Note: time_zero_slope MUST be a tuple
    if conf.time_zero_slope is not None:
        dp_som1.attr_list["Time_zero_slope"] = conf.time_zero_slope

    # Note: time_zero_offset MUST be a tuple
    if conf.time_zero_offset is not None:
        dp_som1.attr_list["Time_zero_offset"] = conf.time_zero_offset


    # Step 5: Convert TOF to wavelength for data and monitor
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
    dp_som3 = common_lib.tof_to_initial_wavelength_igs_lin_time_zero(
        dp_som2,
        units="microsecond",
        run_filter=conf.filter)

    if t is not None:
        t.getTime(msg="After converting TOF to wavelength ")

    if conf.dump_wave:
        hlr_utils.write_file(datalist, "text/Spec", dp_som3,
                             output_ext="pxl",
                             verbose=conf.verbose,
                             message="pixel wavelength information")
    if conf.dump_mon_wave:        
        hlr_utils.write_file(datalist, "text/Spec", dm_som2,
                             output_ext="mxl",
                             verbose=conf.verbose,
                             message="monitor wavelength information")
        
    del dp_som2, dm_som1

    # Step 6: Efficiency correct monitor
    if conf.verbose and dm_som2 is not None:
        print "Efficiency correct monitor data"

    dm_som3 = dr_lib.feff_correct_mon(dm_som2)

    del dm_som2

    # Step 7: Rebin monitor axis onto detector pixel axis
    if conf.verbose and dm_som3 is not None:
        print "Rebin monitor axis to detector pixel axis"

    dm_som4 = dr_lib.rebin_efficiency(dm_som3, dp_som3)

    del dm_som3

    # Step 8: Normalize data by monitor
    if conf.verbose and dm_som4 is not None:
        print "Normalizing data by monitor"

    if dm_som4 is not None:
        dp_som4 = common_lib.div_ncerr(dp_som3, dm_som4)
    else:
        dp_som4 = dp_som3

    del dm_som4, dp_som3

    return dp_som4

def determine_time_indep_bkg(conf, data_som):
    """Step 3. Determine the sample dependent, time independent
    background B by fitting a line to predetermined end points of
    ItdDXY(TOF) using function 3.43."""

    kwargs = {}

    if conf.TOF_start is not None:
        kwargs["start"] = conf.TOF_start

    if conf.TOF_end is not None:
        kwargs["end"] = conf.TOF_end

    return common_lib.weighted_average(data_som, **kwargs)

def subtract_time_indep_bkg(data_som, B):
    """Step 4. Subtract B from the data spectrum using function 3.2
    with ItdDXY(TOF) as data1 and B as a. The result is ItdsDXY(TOF)."""

    if B is None:
        return data_som

    return dr_lib.subtract_time_indep_bkg(data_som, B)



