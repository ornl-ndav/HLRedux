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

def process_reflp_data(datalist, conf, roi_file, **kwargs):
    """
    This function combines Steps 1 through 3 in section 2.4.6.1 of the data
    reduction process for Reduction from TOF to lambda_T as specified by
    the document at
    U{http://neutrons.ornl.gov/asg/projects/SCL/reqspec/DR_Lib_RS.doc}. The
    function takes a list of file names, a L{hlr_utils.Configure} object,
    region-of-interest (ROI) file for the normalization dataset and processes
    the data accordingly.

    @param datalist: The filenames of the data to be processed
    @type datalist: C{list} of C{string}s

    @param conf: Object that contains the current setup of the driver
    @type conf: L{hlr_utils.Configure}

    @param roi_file: The file containing the list of pixel IDs for the region
                     of interest. This only applies to normalization data. 
    @type roi_file: C{string}

    @param kwargs: A list of keyword arguments that the function accepts:

    @keyword inst_geom_dst: File object that contains instrument geometry
                            information.
    @type inst_geom_dst: C{DST.GeomDST}

    @keyword timer:  Timing object so the function can perform timing
                     estimates.
    @type timer: C{sns_timer.DiffTime}


    @return: Object that has undergone all requested processing steps
    @rtype: C{SOM.SOM}
    """
    import common_lib
    import dr_lib
    import hlr_utils

    # Check keywords
    try:
        i_geom_dst = kwargs["inst_geom_dst"]
    except KeyError:
        i_geom_dst = None
    
    try:
        t = kwargs["timer"]
    except KeyError:
        t = None

    if roi_file is not None:
        # Normalization
        dataset_type = "norm"
    else:
        # Sample data
        dataset_type = "data"

    so_axis = "time_of_flight"

    # Step 0: Open data files and select ROI (if necessary)
    if conf.verbose:
        print "Reading %s file" % dataset_type

    d_som1 = dr_lib.add_files(datalist,
                              Data_Paths=conf.data_paths.toPath(),
                              SO_Axis=so_axis,
                              dataset_type=dataset_type,
                              Signal_ROI=roi_file,
                              Verbose=conf.verbose,
                              Timer=t)[0]

    if t is not None:
        t.getTime(msg="After reading %s " % dataset_type)

    # Override geometry if necessary
    if i_geom_dst is not None:
        i_geom_dst.setGeometry(conf.data_paths.toPath(), d_som1)

    if dataset_type == "data":
        # Get TOF bin width
        conf.delta_TOF = d_som1[0].axis[0].val[1] - d_som1[0].axis[0].val[0]

    if conf.mon_norm:
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
    else:
        dm_som1 = None

    # Step 1: Sum all spectra along the low resolution direction
    # Set sorting for REF_L
    if conf.verbose:
        print "Summing over low resolution direction"
        
    if conf.inst == "REF_L":
        y_sort = True
    else:
        y_sort = False

    if t is not None:
        t.getTime(False)

    d_som2 = dr_lib.sum_all_spectra(d_som1, y_sort=y_sort, stripe=True,
                                    pixel_fix=127)

    if t is not None:
        t.getTime(msg="After summing low resolution direction ")
        
    del d_som1

    # Step N: Convert TOF to wavelength
    if conf.verbose:
        print "Converting TOF to wavelength"

    if tim is not None:
        tim.getTime(False)

    d_som3 = common_lib.tof_to_wavelength(d_som2, units="microsecond")
    if dm_som1 is not None:
        dm_som2 = common_lib.tof_to_wavelength(dm_som1, units="microsecond")
    else:
        dm_som2 = None

    del dm_som1

    if tim is not None:
        tim.getTime(msg="After converting TOF to wavelength ")

    del d_som2

    if conf.mon_norm:
        dm_som3 = dr_lib.rebin_monitor(dm_som2, d_som3, rtype="frac")
    else:
        dm_som3 = None

    del dm_som2

    if not conf.mon_norm:
        # Step 2: Multiply the spectra by the proton charge
        if conf.verbose:
            print "Multiply spectra by proton charge"

        pc_tag = dataset_type + "-proton_charge"
        proton_charge = d_som2.attr_list[pc_tag]

        if t is not None:
            t.getTime(False)

        d_som3 = common_lib.mult_ncerr(d_som2, (proton_charge.getValue(), 0.0))

        if t is not None:
            t.getTime(msg="After scaling by proton charge ")
    else:
        if conf.verbose:
            print "Normalize by monitor spectrum"

        if t is not None:
            t.getTime(False)

        d_som3 = common_lib.div_ncerr(d_som2, dm_som3)

        if t is not None:
            t.getTime(msg="After monitor normalization ")

    del d_som2, dm_som3

    if roi_file is None:
        return d_som3
    else:
        # Step 3: Make one spectrum for normalization dataset
        # Need to create a final rebinning axis
        pathlength = d_som3.attr_list.instrument.get_total_path(
            det_secondary=True)
        
        delta_lambda = common_lib.tof_to_wavelength((config.delta_TOF, 0.0),
                                                    pathlength=pathlength)

        lambda_bins = dr_lib.create_axis_from_data(d_som3,
                                                   width=delta_lambda[0])

        return dr_lib.sum_by_rebin_frac(d_som3, lambda_bins.toNessiList())
