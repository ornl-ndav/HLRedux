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

"""
This program covers the functionality outlined in B{Section 2.4.5 Reduction
without Monitors} in
U{http://neutrons.ornl.gov/asg/projects/SCL/reqspec/DR_Lib_RS.doc}.
"""

def run(config, tim):
    """
    This method is where the data reduction process gets done.

    @param config: Object containing the data reduction configuration
                   information.
    @type config: L{hlr_utils.Configure}

    @param tim: Object that will allow the method to perform timing
                evaluations.
    @type tim: C{sns_time.DiffTime}
    """
    import DST
    import math
    if config.inst == "REF_M":
        import axis_manip
        import utils

    if tim is not None:
        tim.getTime(False)
        old_time = tim.getOldTime()

    if config.data is None:
        raise RuntimeError("Need to pass a data filename to the driver "\
                           +"script.")

    # Read in sample data geometry if one is provided
    if config.data_inst_geom is not None:
        if config.verbose:
            print "Reading in sample data instrument geometry file"
            
        data_inst_geom_dst = DST.getInstance("application/x-NxsGeom",
                                             config.data_inst_geom)
    else:
        data_inst_geom_dst = None

    # Read in normalization data geometry if one is provided
    if config.norm_inst_geom is not None:
        if config.verbose:
            print "Reading in normalization instrument geometry file"
            
        norm_inst_geom_dst = DST.getInstance("application/x-NxsGeom",
                                        config.norm_inst_geom)
    else:
        norm_inst_geom_dst = None        
    
    # Perform Steps 1-6 on sample data
    d_som1 = dr_lib.process_ref_data(config.data, config,
                                     config.data_roi_file,
                                     config.dbkg_roi_file,
                                     config.no_bkg,
                                     tof_cuts=config.tof_cuts,
                                     inst_geom_dst=data_inst_geom_dst,
                                     no_tof_cuts=True,
                                     timer=tim)

    # Perform Steps 1-6 on normalization data
    if config.norm is not None:
        n_som1 = dr_lib.process_ref_data(config.norm, config,
                                         config.norm_roi_file,
                                         config.nbkg_roi_file,
                                         config.no_norm_bkg,
                                         dataset_type="norm",
                                         tof_cuts=config.tof_cuts,
                                         inst_geom_dst=norm_inst_geom_dst,
                                         no_tof_cuts=True,
                                         timer=tim)
    else:
        n_som1 = None

    if config.Q_bins is None and config.scatt_angle is not None:
        import copy
        tof_axis = copy.deepcopy(d_som1[0].axis[0].val)

    # Closing sample data instrument geometry file
    if data_inst_geom_dst is not None:
        data_inst_geom_dst.release_resource()

    # Closing normalization data instrument geometry file
    if norm_inst_geom_dst is not None:
        norm_inst_geom_dst.release_resource()        

    # Step 7: Sum all normalization spectra together
    if config.norm is not None:
        n_som2 = dr_lib.sum_all_spectra(n_som1)
    else:
        n_som2 = None

    del n_som1

    # Step 8: Divide data by normalization
    if config.verbose and config.norm is not None:
        print "Scale data by normalization"

    if config.norm is not None:
        d_som2 = common_lib.div_ncerr(d_som1, n_som2, length_one_som=True)
    else:
        d_som2 = d_som1

    if tim is not None and config.norm is not None:
        tim.getTime(msg="After normalizing signal spectra")

    del d_som1, n_som2

    if config.dump_rtof_comb:
        d_som2_1 = dr_lib.sum_all_spectra(d_som2)
        d_som2_2 = dr_lib.data_filter(d_som2_1)
        del d_som2_1

        if config.inst == "REF_M":
            tof_bc = utils.calc_bin_centers(d_som2_2[0].axis[0].val)
            d_som2_2[0].axis[0].val = tof_bc[0]
            d_som2_2.setDataSetType("density")

        d_som2_3 = dr_lib.cut_spectra(d_som2_2, config.tof_cut_min,
                                      config.tof_cut_max)
        del d_som2_2
        
        hlr_utils.write_file(config.output, "text/Spec", d_som2_3,
                             output_ext="crtof",
                             verbose=config.verbose,
                             data_ext=config.ext_replacement,
                             path_replacement=config.path_replacement,
                             message="combined R(TOF) information")
        del d_som2_3

    if config.dump_rtof:
        if config.inst == "REF_M":
            d_som2_1 = d_som2
        else:
            d_som2_1 = dr_lib.filter_ref_data(d_som2)

        d_som2_2 = dr_lib.cut_spectra(d_som2_1, config.tof_cut_min,
                                      config.tof_cut_max)
        del d_som2_1
        hlr_utils.write_file(config.output, "text/Spec", d_som2_2,
                             output_ext="rtof",
                             verbose=config.verbose,
                             data_ext=config.ext_replacement,
                             path_replacement=config.path_replacement,
                             message="R(TOF) information")
        del d_som2_2

    # Step 9: Convert TOF to scalar Q
    if config.verbose:
        print "Converting TOF to scalar Q"
        if config.beamdiv_corr:
            print "Applying beam divergence correction"
    
    # Check to see if polar angle offset is necessary
    if config.angle_offset is not None:
        # Check on units, offset must be in radians
        p_offset = hlr_utils.angle_to_radians(config.angle_offset)
        d_som2.attr_list["angle_offset"] = config.angle_offset
    else:
        p_offset = None

    # Check to see if scattering angle is requested
    if config.scatt_angle is not None:
        scatt_angle = hlr_utils.angle_to_radians(config.scatt_angle)
    else:
        scatt_angle = None
    
    if tim is not None:
        tim.getTime(False)
    
    d_som3 = dr_lib.tof_to_ref_scalar_Q(d_som2, units="microsecond",
                                        angle_offset=p_offset,
                                        lojac=False,
                                        polar=scatt_angle,
                                        configure=config)
    
    del d_som2
            
    if tim is not None:
        tim.getTime(msg="After converting wavelength to scalar Q ")

    # Calculate the Q cut range from the TOF cuts range
    if scatt_angle is not None:
        polar_angle = scatt_angle
    else:
        polar_angle = (d_som3.attr_list["data-theta"][0], 0)

    if p_offset is not None:
        polar_angle = (polar_angle[0] + p_offset[0],
                       polar_angle[1] + p_offset[1])

    pl = d_som3.attr_list.instrument.get_total_path(det_secondary=True)
    if config.tof_cut_min is not None:
        Q_cut_min = dr_lib.tof_to_ref_scalar_Q((float(config.tof_cut_min), 0.0),
                                               pathlength=pl,
                                               polar=polar_angle)[0]
    else:
        Q_cut_min = None
        
    if config.tof_cut_max is not None:
        Q_cut_max = dr_lib.tof_to_ref_scalar_Q((float(config.tof_cut_max), 0.0),
                                               pathlength=pl,
                                               polar=polar_angle)[0]
    else:
        Q_cut_max = None
    
    if config.dump_rq:
        d_som3_1 = dr_lib.data_filter(d_som3, clean_axis=True)
        d_som3_2 = dr_lib.cut_spectra(d_som3_1, Q_cut_min, Q_cut_max)
        del d_som3_1
        hlr_utils.write_file(config.output, "text/Spec", d_som3_2,
                             output_ext="rq",
                             verbose=config.verbose,
                             data_ext=config.ext_replacement,
                             path_replacement=config.path_replacement,
                             message="pixel R(Q) information")
        del d_som3_2
                    
    if config.Q_bins is not None or config.beamdiv_corr:
        if config.verbose:
            print "Rebinning data"
        d_som4 = common_lib.rebin_axis_1D_frac(d_som3,
                                               config.Q_bins.toNessiList())
        
        if config.dump_rqr:
            d_som4_1 = dr_lib.data_filter(d_som4, clean_axis=True)
            d_som4_2 = dr_lib.cut_spectra(d_som4_1, Q_cut_min, Q_cut_max)
            del d_som4_2
            hlr_utils.write_file(config.output, "text/Spec", d_som4_2,
                                 output_ext="rqr",
                                 verbose=config.verbose,
                                 data_ext=config.ext_replacement,
                                 path_replacement=config.path_replacement,
                                 message="rebinned pixel R(Q) information")
            del d_som4_2
    else:
        d_som4 = d_som3

    del d_som3

    if not config.no_filter:
        if config.verbose:
            print "Filtering final data"
            
        if tim is not None:
            tim.getTime(False)
            
        d_som5 = dr_lib.data_filter(d_som4)
    
        if tim is not None:
            tim.getTime(msg="After filtering data")
    else:
        d_som5 = d_som4
    
    del d_som4

    # Sum all spectra since everything is on same axis
    d_som6 = dr_lib.sum_all_spectra(d_som5)
    #d_som6 = dr_lib.sum_spectra_weighted_ave(d_som5)
    
    del d_som5

    d_som7 = dr_lib.cut_spectra(d_som6, Q_cut_min, Q_cut_max)

    del d_som6

    hlr_utils.write_file(config.output, "text/Spec", d_som7,
                         replace_ext=False,
                         replace_path=False,
                         verbose=config.verbose,
                         message="combined Reflectivity information")

    d_som7.attr_list["config"] = config

    hlr_utils.write_file(config.output, "text/rmd", d_som7,
                         output_ext="rmd", verbose=config.verbose,
                         data_ext=config.ext_replacement,
                         path_replacement=config.path_replacement,
                         message="metadata")

    if tim is not None:
        tim.setOldTime(old_time)
        tim.getTime(msg="Total Running Time")

if __name__ == "__main__":
    import common_lib
    import dr_lib
    import hlr_utils

    # Make description for driver
    result = []
    result.append("This driver runs the data reduction for REF_M and REF_L")
    result.append("instruments. The standard output is a *.txt file (3-column")
    result.append("ASCII) for R(Q). Other intermediate files can be produced")
    result.append("by using the appropriate dump-X flag described in this")
    result.append("help. The file extensions are described in the option")
    result.append("documentation.")
    
    # Set up the options available
    parser = hlr_utils.SmhrOptions("usage: %prog [options] <datafile>", None,
                                   None, hlr_utils.program_version(), 'error',
                                   " ".join(result))

    # Defaults for REF
    parser.set_defaults(data_paths="/entry/bank1,1")

    # Setup REF specific options
    parser.add_option("", "--timing", action="store_true", dest="timing",
                      help="Flag to turn on timing of code")
    parser.set_defaults(timing=False)

    (options, args) = parser.parse_args()
    
    # Set up the configuration
    configure = hlr_utils.Configure()

    # Call the configuration setter for SmhrOptions
    hlr_utils.SmhrConfiguration(parser, configure, options, args)

    # Setup the timing object
    if options.timing:
        import sns_timing
        timer = sns_timing.DiffTime()
    else:
        timer = None

    # Run the program
    run(configure, timer)
