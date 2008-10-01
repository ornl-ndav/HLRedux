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

    dp_som0 = dr_lib.add_files(datalist, Data_Paths=data_paths,
                               SO_Axis=conf.so_axis, Signal_ROI=conf.roi_file,
                               dataset_type=dataset_type,
                               dst_type=dst_type,
                               Verbose=conf.verbose, Timer=t)

    if t is not None:
        t.getTime(msg="After reading %s " % dataset_type)

    dp_som1 = dr_lib.fix_bin_contents(dp_som0)

    del dp_som0    

    if conf.inst_geom is not None:
        i_geom_dst.setGeometry(conf.data_paths.toPath(), dp_som1)

    # Open the downstream monitor
    if conf.verbose:
        print "Reading in monitor data from %s file" % dataset_type

    dm_som0 = dr_lib.add_files(datalist, Data_Paths=conf.dsmon_path.toPath(),
                               SO_Axis=conf.so_axis,
                               dataset_type=dataset_type,
                               Verbose=conf.verbose,
                               Timer=t)
        
    if t is not None:
        t.getTime(msg="After reading monitor data ")

    dm_som1 = dr_lib.fix_bin_contents(dm_som0)
    
    del dm_som0

    if conf.inst_geom is not None:
        i_geom_dst.setGeometry(conf.dsmon_path.toPath(), dm_som1)
    
    # Step 3: Integrate the downstream monitor
    if conf.verbose:
        print "Integrating downstream monitor spectrum"

    if t is not None:
        t.getTime(False)


    if t is not None:
        t.getTime(msg="After integrating downstream monitor spectrum ")

    return dp_som1
