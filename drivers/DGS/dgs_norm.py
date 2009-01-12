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
This program covers the functionality outlined in B{Section 2.1.1 General
sample reduction} in
U{http://neutrons.ornl.gov/asg/projects/SCL/reqspec/DR_Lib_RS.doc}
"""
def run(config, tim=None):
    """
    This method is where the data reduction process gets done.

    @param config: Object containing the data reduction configuration
                   information.
    @type config: L{hlr_utils.Configure}

    @param tim: (OPTIONAL) Object that will allow the method to perform
                           timing evaluations.
    @type tim: C{sns_time.DiffTime}
    """
    import common_lib
    import dr_lib
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

    config.so_axis = "time_of_flight"

    # Steps 1-3: Produce a scaled summed dark current dataset
    dc_som = dr_lib.scaled_summed_data(config.dkcur, config,
                                       dataset_type="dark_current",
                                       timer=tim)

    # Perform Steps 3-6 on black can data
    if config.bcan is not None:
        b_som1 = dr_lib.calibrate_dgs_data(config.bcan, config, dc_som,
                                           dataset_type="black_can",
                                           inst_geom_dst=inst_geom_dst,
                                           tib_const=config.tib_const,
                                           timer=tim)
    else:
        b_som1 = None

    # Perform Steps 3-6 on empty can data    
    if config.ecan is not None:
        e_som1 = dr_lib.calibrate_dgs_data(config.ecan, config, dc_som,
                                           dataset_type="empty_can",
                                           inst_geom_dst=inst_geom_dst,
                                           tib_const=config.tib_const,
                                           timer=tim)
    else:
        e_som1 = None

    # Perform Steps 3-6 on normalization data
    n_som1 = dr_lib.calibrate_dgs_data(config.data, config, dc_som,
                                       dataset_type="normalization",
                                       inst_geom_dst=inst_geom_dst,
                                       tib_const=config.tib_const,
                                       timer=tim)

    # Perform Steps 7-16 on normalization data
    if config.norm_trans_coeff is None:
        norm_trans_coeff = None
    else:
        norm_trans_coeff = config.norm_trans_coeff.toValErrTuple()

    n_som2 = dr_lib.process_dgs_data(n_som1, config, b_som1, e_som1,
                                     norm_trans_coeff,
                                     dataset_type="normalization",
                                     timer=tim)
        
    del n_som1, b_som1, e_som1

    # Step 17: Integrate normalization spectra
    if config.verbose:
        print "Integrating normalization spectra"

    if tim is not None:
        tim.getTime(False)

    if config.norm_int_range is None:
        start_val = float("inf")
        end_val = float("inf")
    else:
        start_val = common_lib.energy_to_wavelength(\
                (config.norm_int_range[1], 0.0))[0]
        end_val = common_lib.energy_to_wavelength(\
                (config.norm_int_range[0], 0.0))[0]
        
    n_som3 = dr_lib.integrate_spectra(n_som2, start=start_val,
                                        end=end_val, width=True)

    del n_som2
    
    if tim is not None:
        tim.getTime(msg="After integrating normalization spectra ")

    if config.dump_norm:
        file_comment = "Normalization Integration range: %0.3fA, %0.3fA" \
                       % (start_val, end_val)
        
        hlr_utils.write_file(config.output, "text/num-info", n_som3,
                             output_ext="norm",
                             data_ext=config.ext_replacement,
                             path_replacement=config.path_replacement,
                             verbose=config.verbose,
                             message="normalization values",
                             comments=[file_comment],
                             tag="Integral", units="counts")   

    if tim is not None:
        tim.getTime(False)

    if config.verbose:
        print "Making mask file"

    # Make mask file from threshold
    dr_lib.filter_normalization(n_som3, config.threshold, config)

    if tim is not None:
        tim.getTime(msg="After making mask file ")

    # Write out RMD file
    n_som3.attr_list["config"] = config

    hlr_utils.write_file(config.output, "text/rmd", n_som3,
                         output_ext="rmd",
                         data_ext=config.ext_replacement,         
                         path_replacement=config.path_replacement,
                         verbose=config.verbose,
                         message="metadata")
    
    if tim is not None:
        tim.setOldTime(old_time)
        tim.getTime(msg="Total Running Time")

if __name__ == "__main__":
    import hlr_utils

    # Make description for driver
    description = []
    description.append("This driver runs the reduction steps on")
    description.append("normalization data for the Direct")
    description.append("Geometry Spectrometer class of instruments.")
    description.append("The result of running the driver will be a list of")
    description.append("pixel IDs that are below a given threshold.")
    
    # Set up the options available
    parser = hlr_utils.DgsOptions("usage: %prog [options] <datafile>", None,
                                  None, hlr_utils.program_version(), 'error',
                                  " ".join(description))

    # Remove unneeded options
    parser.remove_option("--norm")
    parser.remove_option("--data-trans-coeff")

    # Set defaults for options
    parser.set_defaults(usmon_path="/entry/monitor1,1")
    parser.set_defaults(dsmon_path="/entry/monitor2,1")

    # Add dgs_norm specific options
    parser.add_option("", "--threshold", type="float", dest="threshold",
                      help="Set the cutoff value for the normalization that "\
                      +"below which a pixel will be masked out. The default "\
                      +"is 0.0.")
    parser.set_defaults(threshold=0.0)
    
    parser.add_option("", "--timing", action="store_true", dest="timing",
                      help="Flag to turn on timing of code")
    parser.set_defaults(timing=False)

    (options, args) = parser.parse_args()

    # Set up the configuration
    configure = hlr_utils.Configure()

    # Call the configuration setter for DgsOptions
    hlr_utils.DgsConfiguration(parser, configure, options, args)

    # Set default for upstream monitor for CNCS
    if configure.inst == "CNCS":
        configure.usmon_path = hlr_utils.NxPath("/entry/monitor3,1")

    # Set timer object if timing option is used
    if options.timing:
        import sns_timing
        timer = sns_timing.DiffTime()
    else:
        timer = None
    
    # Run the program
    run(configure, timer)
