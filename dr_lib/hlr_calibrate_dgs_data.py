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

def calibrate_dgs_data(datalist, conf, **kwargs):
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
    
    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword inst_geom_dst: File object that contains instrument geometry
                            information.
    @type inst_geom_dst: C{DST.GeomDST}
    
    @keyword dataset_type: The practical name of the dataset being processed.
                           The default value is I{data}.
    @type dataset_type: C{string}
    
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
        t = kwargs["timer"]
    except KeyError:
        t = None

    try:
        i_geom_dst = kwargs["inst_geom_dst"]
    except KeyError:
        i_geom_dst = None

    # Open the appropriate datafiles
    if conf.verbose:
        print "Reading %s file" % dataset_type

    dst_type = "application/x-NeXus"
    data_paths = conf.data_paths.toPath()
    if conf.no_mon_norm:
        mon_paths = None
    else:
        mon_paths= conf.usmon_path.toPath()

    if t is not None:
        oldtime = t.getOldTime()

    (dp_som0, dm_som0) = dr_lib.add_files_dm(datalist, Data_Paths=data_paths,
                                             Mon_Paths=mon_paths,
                                             SO_Axis=conf.so_axis,
                                             Signal_ROI=conf.roi_file,
                                             dataset_type=dataset_type,
                                             Verbose=conf.verbose, Timer=t)

    if t is not None:
        t.setOldTime(oldtime)
        t.getTime(msg="After reading %s " % dataset_type)

    dp_som1 = dr_lib.fix_bin_contents(dp_som0)

    del dp_som0

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
            start_val = 0
            end_val = -1
            is_bin = True
        else:
            start_val = conf.mon_int_range[0]
            end_val = conf.mon_int_range[1]
            is_bin = False
        
        dm_som2 = dr_lib.integrate_spectra(dm_som1, start=start_val,
                                           end=end_val,
                                           bin_index=is_bin,
                                           width=True)
        if t is not None:
            t.getTime(msg="After integrating upstream monitor spectrum ")
    else:
        dm_som2 = dm_som1

    del dm_som1
    
    # Step 4: Divide data set by summed monitor spectrum
    if dm_som2 is not None:
        if conf.verbose:
            print "Normalizing %s by monitor sum" % dataset_type

        if t is not None:
            t.getTime(False)

        dp_som2 = common_lib.div_ncerr(dp_som1, dm_som2, length_one_som=True)

        if t is not None:
            t.getTime(msg="After normalizing %s by monitor sum" % dataset_type)

    elif conf.pc_norm:
        if conf.verbose:
            print "Normalizing %s by proton charge" % dataset_type

        pc_tag = dataset_type+"-proton_charge"
        pc = dp_som1.attr_list[pc_tag]

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

    # Step 6: Subtract scaled dark current from data set
    
    return dp_som2
