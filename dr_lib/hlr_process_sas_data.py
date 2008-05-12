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

    @keyword transmission: A flag that signals the function to stop after
                           doing the conversion from TOF to wavelength.
    @type transmission: C{boolean}

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

    # Add so_axis to Configure object
    conf.so_axis = "time_of_flight"

    # Step 0: Open appropriate data files

    if conf.verbose:
        print "Reading %s file" % dataset_type

    # The [0] is to get the data SOM and ignore the None background SOM
    dp_som0 = dr_lib.add_files(datalist, Data_Paths=conf.data_paths.toPath(),
                               SO_Axis=conf.so_axis, Signal_ROI=conf.roi_file,
                               dataset_type=dataset_type,
                               Verbose=conf.verbose, Timer=t)[0]

    if t is not None:
        t.getTime(msg="After reading %s " % dataset_type)

    dp_som1 = dr_lib.fix_bin_contents(dp_som0)

    del dp_som0    

    if conf.inst_geom is not None:
        i_geom_dst.setGeometry(conf.data_paths.toPath(), dp_som1)

    if conf.verbose:
        print "Reading in monitor data from %s file" % dataset_type
        
    # The [0] is to get the data SOM and ignore the None background SOM
    dbm_som0 = dr_lib.add_files(datalist, Data_Paths=conf.bmon_path.toPath(),
                                SO_Axis=conf.so_axis,
                                dataset_type=dataset_type,
                                Verbose=conf.verbose,
                                Timer=t)[0]
        
    if t is not None:
        t.getTime(msg="After reading monitor data ")

    dbm_som1 = dr_lib.fix_bin_contents(dbm_som0)
    
    del dbm_som0
    
    # Note: time_zero_offset_det MUST be a tuple
    if conf.time_zero_offset_det is not None:
        dp_som1.attr_list["Time_zero_offset_det"] = \
                                     conf.time_zero_offset_det.toValErrTuple()
    # Note: time_zero_offset_mon MUST be a tuple
    if conf.time_zero_offset_mon is not None:
        dbm_som1.attr_list["Time_zero_offset_mon"] = \
                                     conf.time_zero_offset_mon.toValErrTuple()

    # Step 1: Convert TOF to wavelength for data and monitor
    if conf.verbose:
        print "Converting TOF to wavelength"

    if t is not None:
        t.getTime(False)

    # Convert beam monitor
    dbm_som2 = common_lib.tof_to_wavelength_lin_time_zero(
        dbm_som1,
        units="microsecond",
        time_zero_offset=conf.time_zero_offset_mon.toValErrTuple())

    # Convert detector pixels
    dp_som2 = common_lib.tof_to_wavelength_lin_time_zero(
        dp_som1,
        units="microsecond",
        time_zero_offset=conf.time_zero_offset_det.toValErrTuple(),
        inst_param="total")

    if t is not None:
        t.getTime(msg="After converting TOF to wavelength ")

    if conf.dump_wave:
        hlr_utils.write_file(conf.output, "text/Spec", dp_som2,
                             output_ext="pxl",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             data_ext=conf.ext_replacement,
                             path_replacement=conf.path_replacement,
                             message="pixel wavelength information")
    if conf.dump_bmon_wave:
        hlr_utils.write_file(conf.output, "text/Spec", dbm_som2,
                             output_ext="bmxl",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             data_ext=conf.ext_replacement,
                             path_replacement=conf.path_replacement,
                             message="beam monitor wavelength information")
        
    del dp_som1, dbm_som1

    # Step 2: Efficiency correct beam monitor
    if conf.verbose and conf.mon_effc:
        print "Efficiency correct beam monitor data"

    if t is not None:
        t.getTime(False)

    if conf.mon_effc:
        dbm_som3 = dr_lib.feff_correct_mon(dbm_som2)
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

    # Step 3: Efficiency correct transmission monitor    

    # Step 4: Efficiency correct detector pixels

    # Step 5: Rebin beam monitor axis onto detector pixel axis
    if conf.verbose:
        print "Rebin beam monitor axis to detector pixel axis"

    if t is not None:
        t.getTime(False)

    dbm_som4 = dr_lib.rebin_monitor(dbm_som3, dp_som2)

    if t is not None:
        t.getTime(msg="After rebinning beam monitor ")

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


    # Step 6: Normalize data by beam monitor
    if conf.verbose:
        print "Normalizing data by beam monitor"

    if t is not None:
        t.getTime(False)

    dp_som3 = common_lib.div_ncerr(dp_som2, dbm_som4)

    if t is not None:
        t.getTime(msg="After normalizing data by beam monitor ")

    del dp_som2

    if transmission:
        return dp_som3

    if conf.dump_wave_bmnorm:
        dp_som3_1 = dr_lib.sum_all_spectra(dp_som3,\
                                   rebin_axis=conf.lambda_bins.toNessiList())

        write_message = "combined pixel wavelength information"
        write_message += " (beam monitor normalized)"
        
        hlr_utils.write_file(conf.output, "text/Spec", dp_som3_1,
                             output_ext="pbml",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             data_ext=conf.ext_replacement,
                             path_replacement=conf.path_replacement,
                             message=write_message)
        del dp_som3_1

    # Step 7: Rebin transmission monitor axis onto detector pixel axis

    # Step 8: Normalize data by transmission monitor    

    # Step 9: Convert wavelength to Q for data
    if conf.verbose:
        print "Converting data from wavelength to scalar Q"
    
    if t is not None:
        t.getTime(False)

    dp_som4 = common_lib.wavelength_to_scalar_Q(dp_som3)

    if t is not None:
        t.getTime(msg="After converting wavelength to scalar Q ")
        
    del dp_som3
 
    return dp_som4
