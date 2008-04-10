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

    # Add so_axis to Configure object
    conf.so_axis = "time_of_flight"

    # Step 0: Open appropriate data files

    if conf.verbose:
        print "Reading %s file" % dataset_type

    # The [0] is to get the data SOM and ignore the None background SOM
    dp_som0 = dr_lib.add_files(datalist, Data_Paths=data_paths,
                               SO_Axis=conf.so_axis, Signal_ROI=conf.roi_file,
                               dataset_type=dataset_type,
                               dst_type=dst_type,
                               Verbose=conf.verbose, Timer=t)[0]

    if t is not None:
        t.getTime(msg="After reading %s " % dataset_type)

    dp_som1 = dr_lib.fix_bin_contents(dp_som0)

    del dp_som0    

    if conf.verbose:
        print "Reading in monitor data from %s file" % dataset_type
        
    # The [0] is to get the data SOM and ignore the None background SOM
    dm_som0 = dr_lib.add_files(datalist, Data_Paths=conf.mon_path.toPath(),
                               SO_Axis=conf.so_axis,
                               dataset_type=dataset_type,
                               Verbose=conf.verbose,
                               Timer=t)[0]
        
    if t is not None:
        t.getTime(msg="After reading monitor data ")

    dm_som1 = dr_lib.fix_bin_contents(dm_som0)
    
    del dm_som0
    
    # Note: time_zero_offset_det MUST be a tuple
    if conf.time_zero_offset_det is not None:
        dp_som1.attr_list["Time_zero_offset_det"] = \
                                     conf.time_zero_offset_det.toValErrTuple()
    # Note: time_zero_offset_mon MUST be a tuple
    if conf.time_zero_offset_mon is not None:
        dm_som1.attr_list["Time_zero_offset_mon"] = \
                                     conf.time_zero_offset_mon.toValErrTuple()

    # Step 1: Convert TOF to wavelength for data and monitor
    if conf.verbose:
        print "Converting TOF to wavelength"

    if t is not None:
        t.getTime(False)

    # Convert monitor
    dm_som2 = common_lib.tof_to_wavelength_lin_time_zero(
        dm_som1,
        units="microsecond",
        time_zero_offset=conf.time_zero_offset_mon.toValErrTuple())
    else:
        dm_som2 = None

    # Convert detector pixels
    dp_som2 = common_lib.tof_to_wavelength_lin_time_zero(
        dp_som1,
        units="microsecond",
        time_zero_offset=conf.time_zero_offset_det.toValErrTuple())

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
    if conf.dump_mon_wave:
        hlr_utils.write_file(conf.output, "text/Spec", dm_som2,
                             output_ext="mxl",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             data_ext=conf.ext_replacement,
                             path_replacement=conf.path_replacement,
                             message="monitor wavelength information")
        
    del dp_som1, dm_som1

