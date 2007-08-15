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

    if tim is not None:
        tim.getTime(False)
        old_time = tim.getOldTime()

    if config.data is None:
        raise RuntimeError("Need to pass a data filename to the driver "\
                           +"script.")

    # Read in geometry if one is provided
    if config.inst_geom is not None:
        if config.verbose:
            print "Reading in instrument geometry file"
            
        inst_geom_dst = DST.getInstance("application/x-NxsGeom",
                                        config.inst_geom)
    else:
        inst_geom_dst = None
    
    # Perform Steps 1-5 on sample data
    d_som1 = dr_lib.process_ref_data(config.data, config,
                                     config.data_roi_file,
                                     config.no_bkg,
                                     inst_geom_dst=inst_geom_dst,
                                     timer=tim)

    # Perform Steps 1-5 on normalization data
    if config.norm is not None:
        n_som1 = dr_lib.process_ref_data(config.norm, config,
                                         config.norm_roi_file,
                                         config.no_norm_bkg,
                                         dataset_type="norm",
                                         inst_geom_dst=inst_geom_dst,
                                         timer=tim)
    else:
        n_som1 = None

    # Step 6: Sum all normalization spectra together
    if config.norm is not None:
        n_som2 = dr_lib.sum_all_spectra(n_som1)
    else:
        n_som2 = None

    del n_som1

    if inst_geom_dst is not None:
        inst_geom_dst.release_resource()

    # Step 7: Divide data by normalization
    if config.verbose and config.norm is not None:
        print "Scale data by normalization"

    if config.norm is not None:
        d_som2 = common_lib.div_ncerr(d_som1, n_som2, length_one_som=True)
    else:
        d_som2 = d_som1

    if tim is not None and config.norm is not None:
        tim.getTime(msg="After normalizing signal spectra")

    del d_som1, n_som2

    if config.dump_rtof:
        d_som2_1 = dr_lib.filter_ref_data(d_som2)
        
        hlr_utils.write_file(config.output, "text/Spec", d_som2_1,
                             output_ext="rtof",
                             verbose=config.verbose,
                             data_ext=config.ext_replacement,
                             path_replacement=config.path_replacement,
                             message="R(TOF) information")
        del d_som2_1

    # Step 8: Convert TOF to scalar Q
    if config.verbose:
        print "Converting TOF to scalar Q"

    if tim is not None:
        tim.getTime(False)

    d_som3 = common_lib.tof_to_scalar_Q(d_som2, units="microsecond")

    del d_som2
        
    if tim is not None:
        tim.getTime(msg="After converting wavelength to scalar Q ")


    if config.det_angle is None:
        d_som3.attr_list["detector_angle"] = (0.0, 0.0, "degree")
    else:
        d_som3.attr_list["detector_angle"] = config.det_angle

    if not config.no_filter:
        if config.verbose:
            print "Filtering final data"
        
        if tim is not None:
            tim.getTime(False)
        
        d_som4 = dr_lib.filter_ref_data(d_som3, zero_mode=True)

        if tim is not None:
            tim.getTime(msg="After filtering data")
    else:
        d_som4 = d_som3

    del d_som3

    # Rebin all spectra to final Q axis
    rebin_axis = config.Q_bins.toNessiList()
    d_som5 = dr_lib.sum_all_spectra(d_som4, rebin_axis=rebin_axis)

    del d_som4

    hlr_utils.write_file(config.output, "text/Spec", d_som5,
                         replace_ext=False,
                         replace_path=False,
                         verbose=config.verbose,
                         message="combined Reflectivity information")

    d_som5.attr_list["config"] = config

    hlr_utils.write_file(config.output, "text/rmd", d_som5,
                         output_ext="rmd", verbose=config.verbose,
                         data_ext=config.ext_replacement,
                         path_replacement=config.path_replacement,
                         message="metadata")

    if tim is not None:
        tim.setOldTime(old_time)
        tim.getTime(msg="Completing driver")

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
    parser = hlr_utils.RefRedOptions("usage: %prog [options] <datafile>", None,
                                     hlr_utils.program_version(), 'error',
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

    # Call the configuration setter for RefRedOptions
    hlr_utils.RefRedConfiguration(parser, configure, options, args)

    # Setup the timing object
    if options.timing:
        import sns_timing
        timer = sns_timing.DiffTime()
    else:
        timer = None

    # Run the program
    run(configure, timer)
