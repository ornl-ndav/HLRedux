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

def process_reflp_data(datalist, conf, roi_file, bkg_roi_file=None,
                     no_bkg=False, **kwargs):
    """
    This function combines Steps 1 through 3 in section 2.4.6.1 of the data
    reduction process for Reduction from TOF to lambda_T as specified by
    the document at
    U{http://neutrons.ornl.gov/asg/projects/SCL/reqspec/DR_Lib_RS.doc}. The
    function takes a list of file names, a L{hlr_utils.Configure} object,
    region-of-interest (ROI) file for the normalization dataset, a background
    region-of-interest (ROI) file and an optional flag about background
    subtractionand processes the data accordingly.

    @param datalist: The filenames of the data to be processed
    @type datalist: C{list} of C{string}s

    @param conf: Object that contains the current setup of the driver
    @type conf: L{hlr_utils.Configure}

    @param roi_file: The file containing the list of pixel IDs for the region
                     of interest. This only applies to normalization data. 
    @type roi_file: C{string}

    @param bkg_roi_file: The file containing the list of pixel IDs for the
                         (possible) background region of interest.
    @type bkg_roi_file: C{string}    
    
    @param no_bkg: (OPTIONAL) Flag which determines if the background will be
                              calculated and subtracted.
    @type no_bkg: C{boolean}    

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
    import hlr_utils
    import common_lib
    import dr_lib

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

    if len(conf.norm_data_paths) and dataset_type == "norm":
        data_path = conf.norm_data_paths.toPath()
    else:
        data_path = conf.data_paths.toPath()

    (d_som1, b_som1) = dr_lib.add_files_bg(datalist,
                                           Data_Paths=data_path,
                                           SO_Axis=so_axis,
                                           dataset_type=dataset_type,
                                           Signal_ROI=roi_file,
                                           Bkg_ROI=bkg_roi_file,
                                           Verbose=conf.verbose,
                                           Timer=t)

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
                                   Timer=t)
        
        if t is not None:
            t.getTime(msg="After reading monitor data ")
            
    else:
        dm_som1 = None

    # Step 1: Sum all spectra along the low resolution direction
    # Set sorting for REF_L
    if conf.verbose:
        print "Summing over low resolution direction"

    # Set sorting
    (y_sort,
     cent_pixel) = hlr_utils.get_ref_integration_direction(conf.int_dir,
                                                           conf.inst,
                                                  d_som1.attr_list.instrument)
    
    if t is not None:
        t.getTime(False)

    d_som2 = dr_lib.sum_all_spectra(d_som1, y_sort=y_sort, stripe=True,
                                    pixel_fix=cent_pixel)

    if b_som1 is not None:
        b_som2 = dr_lib.sum_all_spectra(b_som1, y_sort=y_sort, stripe=True,
                                        pixel_fix=cent_pixel)
        del b_som1
    else:
        b_som2 = b_som1

    if t is not None:
        t.getTime(msg="After summing low resolution direction ")
        
    del d_som1

    # Determine background spectrum
    if conf.verbose and not no_bkg:
        print "Determining %s background" % dataset_type

    if b_som2 is not None:
        B = dr_lib.calculate_ref_background(b_som2, no_bkg, conf.inst, None,
                                            aobj=d_som2)
    if t is not None:
        t.getTime(msg="After background determination")

    # Subtract background spectrum from data spectra
    if not no_bkg:
        d_som3 = dr_lib.subtract_bkg_from_data(d_som2, B,
                                               verbose=conf.verbose,
                                               timer=t,
                                               dataset1="data",
                                               dataset2="background")
    else:
        d_som3 = d_som2

    del d_som2

    # Zero the spectra if necessary
    if roi_file is None and (conf.tof_cut_min is not None or \
                             conf.tof_cut_max is not None):
        import utils
        # Find the indicies for the non zero range
        if conf.tof_cut_min is None:
            conf.TOF_min = d_som3[0].axis[0].val[0]
            start_index = 0
        else:
            start_index = utils.bisect_helper(d_som3[0].axis[0].val,
                                              conf.tof_cut_min)

        if conf.tof_cut_max is None:
            conf.TOF_max = d_som3[0].axis[0].val[-1]
            end_index = len(d_som3[0].axis[0].val) - 1
        else:
            end_index = utils.bisect_helper(d_som3[0].axis[0].val,
                                            conf.tof_cut_max)

        nz_list = []
        for i in xrange(hlr_utils.get_length(d_som3)):
            nz_list.append((start_index, end_index))
        
        d_som4 = dr_lib.zero_spectra(d_som3, nz_list, use_bin_index=True)
    else:
        conf.TOF_min = d_som3[0].axis[0].val[0]
        conf.TOF_max = d_som3[0].axis[0].val[-1]
        d_som4 = d_som3

    del d_som3

    # Step N: Convert TOF to wavelength
    if conf.verbose:
        print "Converting TOF to wavelength"

    if t is not None:
        t.getTime(False)

    d_som5 = common_lib.tof_to_wavelength(d_som4, inst_param="total",
                                          units="microsecond")
    if dm_som1 is not None:
        dm_som2 = common_lib.tof_to_wavelength(dm_som1, units="microsecond")
    else:
        dm_som2 = None

    del dm_som1

    if t is not None:
        t.getTime(msg="After converting TOF to wavelength ")

    del d_som4

    if conf.mon_norm:
        dm_som3 = dr_lib.rebin_monitor(dm_som2, d_som5, rtype="frac")
    else:
        dm_som3 = None

    del dm_som2

    if not conf.mon_norm:
        # Step 2: Multiply the spectra by the proton charge
        if conf.verbose:
            print "Multiply spectra by proton charge"

        pc_tag = dataset_type + "-proton_charge"
        proton_charge = d_som5.attr_list[pc_tag]

        if t is not None:
            t.getTime(False)

        d_som6 = common_lib.div_ncerr(d_som5, (proton_charge.getValue(), 0.0))

        if t is not None:
            t.getTime(msg="After scaling by proton charge ")
    else:
        if conf.verbose:
            print "Normalize by monitor spectrum"

        if t is not None:
            t.getTime(False)

        d_som6 = common_lib.div_ncerr(d_som5, dm_som3)

        if t is not None:
            t.getTime(msg="After monitor normalization ")

    del d_som5, dm_som3

    if roi_file is None:
        return d_som6
    else:
        # Step 3: Make one spectrum for normalization dataset
        # Need to create a final rebinning axis
        pathlength = d_som6.attr_list.instrument.get_total_path(
            det_secondary=True)
        
        delta_lambda = common_lib.tof_to_wavelength((conf.delta_TOF, 0.0),
                                                    pathlength=pathlength)

        lambda_bins = dr_lib.create_axis_from_data(d_som6,
                                                   width=delta_lambda[0])

        return dr_lib.sum_by_rebin_frac(d_som6, lambda_bins.toNessiList())
