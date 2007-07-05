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

def process_ref_data(datalist, conf, signal_roi_file, bkg_roi_file,
                     no_bkg=False, **kwargs):
    """
    This function combines Steps 1 through 11 in section 2.4.5 of the data
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
                         background region of interest.
    @type bkg_roi_file: C{string}
    
    @param no_bkg: (OPTIONAL) Flag which determines if the background will be
                              calculated nad subtracted.
    @type no_bkg: C{boolean}
    
    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword inst_geom_dst: Object that contains the instrument geometry
                            information.
    @type inst_geom_dst: C{DST.getInstance()}
    
    @keyword dataset_type: The practical name of the dataset being processed.
                           The default value is I{data}.
    @type dataset_type: C{string}
    
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
    
    so_axis = "time_of_flight"

    # Steps 1 and 2: Open data files and select signal and background ROIs
    if conf.verbose:
        print "Reading %s file" % dataset_type

    (d_som1, b_som1) = dr_lib.add_files(datalist,
                                        Data_Paths=conf.data_paths.toPath(),
                                        SO_Axis=so_axis,
                                        dataset_type=dataset_type,
                                        Signal_ROI=signal_roi_file,
                                        Bkg_ROI=bkg_roi_file,
                                        Verbose=conf.verbose,
                                        Timer=t)

    if t is not None:
        t.getTime(msg="After reading %s " % dataset_type)

    if conf.dump_specular:
        d_som1_1 = dr_lib.sum_all_spectra(d_som1)
        hlr_utils.write_file(conf.output, "text/Spec", d_som1_1,
                             output_ext="sdc",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             data_ext=conf.ext_replacement,
                             path_replacement=conf.path_replacement,
                             message="combined specular TOF information")
        del d_som1_1

    # Calculate delta t over t
    if not conf.no_dtot:
        if conf.verbose:
            print "Calculating delta t over t"
        
        dtot = dr_lib.calc_deltat_over_t(d_som1[0].axis[0].val)
    else:
        dtot = None

    # Steps 3 and 4: Determine background spectrum
    if conf.verbose and not no_bkg:
        print "Determining %s background" % dataset_type

    B = dr_lib.determine_ref_background(b_som1, no_bkg)

    if t is not None:
        t.getTime(msg="After background determination")

    if not no_bkg and conf.dump_bkg:
        hlr_utils.write_file(conf.output, "text/Spec", B,
                             output_ext="bkg",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             data_ext=conf.ext_replacement,
                             path_replacement=conf.path_replacement,
                             message="combined background TOF information")

    del b_som1

    # Step 5: Subtract background spectrum from data spectra
    if not no_bkg:
        d_som2 = dr_lib.subtract_bkg_from_data(d_som1, B[0],
                                               verbose=conf.verbose,
                                               timer=t,
                                               dataset1="data",
                                               dataset2="background")
    else:
        d_som2 = d_som1

    del d_som1

    # Set sorting for REF_L if split spectra required
    if conf.inst == "REF_L":
        y_sort = True
    else:
        y_sort = False

    rebin_axis = None

    if conf.step_stop == 0:
        d_som4 = d_som2
        del d_som2

    # Step 6: Convert TOF to wavelength for data
    if conf.step_stop > 0:
        if conf.inst_geom is not None:
            inst_geom_dst.setGeometry(conf.data_paths.toPath(), d_som2)

        if conf.verbose:
            print "Converting TOF to wavelength"

        if t is not None:
            t.getTime(False)

        d_som3 = common_lib.tof_to_wavelength(d_som2, inst_param="total",
                                              units="microsecond")
        
        if t is not None:
            t.getTime(msg="After converting TOF to wavelength ")

        del d_som2

        if conf.step_stop == 1:
            d_som4 = d_som3
            del d_som3
            rebin_axis = conf.lambda_bins.toNessiList()

    # Step 7: Convert wavelength to scalar Q
    if conf.step_stop > 1:
        if conf.verbose:
            print "Converting wavelength to scalar Q"

        if t is not None:
            t.getTime(False)

        d_som4 = common_lib.wavelength_to_scalar_Q(d_som3)
        del d_som3
        
        rebin_axis = conf.Q_bins.toNessiList()

        if t is not None:
            t.getTime(msg="After converting wavelength to scalar Q ")

    # Steps 8 to 11: Combine the spectra from the dataset
    if conf.verbose:
        print "Combining %s spectra" % dataset_type

    if dataset_type == "norm":
        d_som5 = dr_lib.sum_all_spectra(d_som4, rebin_axis=rebin_axis)
    else:
        d_som5 = dr_lib.sum_all_spectra(d_som4, y_sort=y_sort,
                                        stripe=conf.split,
                                        rebin_axis=rebin_axis)

    del d_som4

    if conf.dump_sub:
        hlr_utils.write_file(conf.output, "text/Spec", d_som5,
                             output_ext="sub",
                             extra_tag=dataset_type,
                             verbose=conf.verbose,
                             data_ext=conf.ext_replacement,
                             path_replacement=conf.path_replacement,
                             message="combined subtracted information")

    if conf.step_stop == 0 and dtot is not None:
        d_som5.attr_list["extra_som"] = dtot

    if dtot is not None:
        dtot_int = dr_lib.integrate_axis(dtot, avg=True)
        param_key = dataset_type+"-dt_over_t"
        d_som5.attr_list[param_key] = dtot_int[0]
        
    return d_som5
