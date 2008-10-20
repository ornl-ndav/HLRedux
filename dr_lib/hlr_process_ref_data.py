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

def process_ref_data(datalist, conf, signal_roi_file, bkg_roi_file=None,
                     no_bkg=False, **kwargs):
    """
    This function combines Steps 1 through 6 in section 2.4.5 of the data
    reduction process for Reflectometers (without Monitors) as specified by
    the document at
    U{http://neutrons.ornl.gov/asg/projects/SCL/reqspec/DR_Lib_RS.doc}. The
    function takes a list of file names, a L{hlr_utils.Configure} object,
    signal and background region-of-interest (ROI) files and an optional flag
    about background subtraction and processes the data accordingly.
    
    @param datalist: The filenames of the data to be processed
    @type datalist: C{list} of C{string}s
    
    @param conf: Object that contains the current setup of the driver
    @type conf: L{hlr_utils.Configure}
    
    @param signal_roi_file: The file containing the list of pixel IDs for the
                            signal region of interest.
    @type signal_roi_file: C{string}

    @param bkg_roi_file: The file containing the list of pixel IDs for the
                         (possible) background region of interest.
    @type bkg_roi_file: C{string}    
    
    @param no_bkg: (OPTIONAL) Flag which determines if the background will be
                              calculated and subtracted.
    @type no_bkg: C{boolean}
    
    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword inst_geom_dst: Object that contains the instrument geometry
                            information.
    @type inst_geom_dst: C{DST.getInstance()}
    
    @keyword dataset_type: The practical name of the dataset being processed.
                           The default value is I{data}.
    @type dataset_type: C{string}

    @keyword tof_cuts: Time-of-flight bins to remove (zero) from the data
    @type tof_cuts: C{list} of C{string}s
    
    @keyword timer:  Timing object so the function can perform timing
                     estimates.
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

    if dataset_type != "data" and dataset_type != "norm":
        raise RuntimeError("Please use data or norm to specify the dataset "\
                           +"type. Do not understand how to handle %s." \
                           % dataset_type)

    try:
        t = kwargs["timer"]
    except KeyError:
        t = None

    try:
        i_geom_dst = kwargs["inst_geom_dst"]
    except KeyError:
        i_geom_dst = None

    try:
        tof_cuts = kwargs["tof_cuts"]
    except KeyError:
        tof_cuts = None
    
    so_axis = "time_of_flight"

    # Step 0: Open data files and select signal (and possible background) ROIs
    if conf.verbose:
        print "Reading %s file" % dataset_type

    (d_som1, b_som1) = dr_lib.add_files_bg(datalist,
                                           Data_Paths=conf.data_paths.toPath(),
                                           SO_Axis=so_axis,
                                           dataset_type=dataset_type,
                                           Signal_ROI=signal_roi_file,
                                           Bkg_ROI=bkg_roi_file,
                                           Verbose=conf.verbose,
                                           Timer=t)

    if t is not None:
        t.getTime(msg="After reading %s " % dataset_type)

    if i_geom_dst is not None:
        i_geom_dst.setGeometry(conf.data_paths.toPath(), d_som1)

    # Calculate delta t over t
    if conf.verbose:
        print "Calculating delta t over t"
        
    dtot = dr_lib.calc_deltat_over_t(d_som1[0].axis[0].val)

    # Calculate delta theta over theta
    if conf.verbose:
        print "Calculating delta theta over theta"

    dr_lib.calc_delta_theta_over_theta(d_som1, dataset_type)

    # Step 1: Sum all spectra along the low resolution direction
    
    # Set sorting for REF_L 
    if conf.inst == "REF_L":
        y_sort = True
    else:
        y_sort = False

    d_som2 = dr_lib.sum_all_spectra(d_som1, y_sort=y_sort, stripe=True,
                                    pixel_fix=127)

    del d_som1
    
    if b_som1 is not None:
        b_som2 = dr_lib.sum_all_spectra(b_som1, y_sort=y_sort, stripe=True,
                                        pixel_fix=127)
        del b_som1
    else:
        b_som2 = b_som1

    # Fix TOF cuts to make them list of integers
    try:
        tof_cuts = [int(x) for x in tof_cuts]
    # This will trigger if tof_cuts is None
    except TypeError:
        pass

    d_som3 = dr_lib.zero_bins(d_som2, tof_cuts)

    del d_som2

    if b_som2 is not None:
        b_som3 = dr_lib.zero_bins(b_som2, tof_cuts)
        
        del b_som2
    else:
        b_som3 = b_som2
        
    if conf.dump_specular:
        hlr_utils.write_file(conf.output, "text/Spec", d_som3,
                             output_ext="sdc",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             data_ext=conf.ext_replacement,
                             path_replacement=conf.path_replacement,
                             message="specular TOF information")

    # Steps 2-4: Determine background spectrum
    if conf.verbose and not no_bkg:
        print "Determining %s background" % dataset_type

    if dataset_type == "data":
        peak_excl = conf.data_peak_excl
    elif dataset_type == "norm":
        peak_excl = conf.norm_peak_excl

    if b_som3 is not None:
        B = dr_lib.calculate_ref_background(b_som3, no_bkg, conf.inst, None,
                                            aobj=d_som3)
    else:
        B = dr_lib.calculate_ref_background(d_som3, no_bkg, conf.inst,
                                            peak_excl)

    if t is not None:
        t.getTime(msg="After background determination")

    if not no_bkg and conf.dump_bkg:
        hlr_utils.write_file(conf.output, "text/Spec", B,
                             output_ext="bkg",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             data_ext=conf.ext_replacement,
                             path_replacement=conf.path_replacement,
                             message="background TOF information")

    # Step 5: Subtract background spectrum from data spectra
    if not no_bkg:
        d_som4 = dr_lib.subtract_bkg_from_data(d_som3, B,
                                               verbose=conf.verbose,
                                               timer=t,
                                               dataset1="data",
                                               dataset2="background")
    else:
        d_som4 = d_som3

    del d_som3

    if not no_bkg and conf.dump_sub:
        hlr_utils.write_file(conf.output, "text/Spec", d_som4,
                             output_ext="sub",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             data_ext=conf.ext_replacement,
                             path_replacement=conf.path_replacement,
                             message="subtracted TOF information")


    dtot_int = dr_lib.integrate_axis_py(dtot, avg=True)
    param_key = dataset_type+"-dt_over_t"
    d_som4.attr_list[param_key] = dtot_int[0]

    if conf.store_dtot:
        d_som4.attr_list["extra_som"] = dtot

    return d_som4
