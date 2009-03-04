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

    if type(config.mask_file) == type([]):
        config.mask_file = hlr_utils.merge_roi_files(config.mask_file)

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
    if config.norm is not None:
        n_som1 = dr_lib.calibrate_dgs_data(config.norm, config, dc_som,
                                           dataset_type="normalization",
                                           inst_geom_dst=inst_geom_dst,
                                           tib_const=config.tib_const,
                                           timer=tim)
    else:
        n_som1 = None

    # Perform Steps 3-6 on sample data
    d_som1 = dr_lib.calibrate_dgs_data(config.data, config, dc_som,
                                       inst_geom_dst=inst_geom_dst,
                                       tib_const=config.tib_const,
                                       timer=tim)

    # Perform Steps 7-16 on sample data
    if config.data_trans_coeff is None:
        data_trans_coeff = None
    else:
        data_trans_coeff = config.data_trans_coeff.toValErrTuple()
    
    d_som2 = dr_lib.process_dgs_data(d_som1, config, b_som1, e_som1,
                                     data_trans_coeff,
                                     timer=tim)

    del d_som1

    # Perform Steps 7-16 on normalization data
    if n_som1 is not None:
        if config.norm_trans_coeff is None:
            norm_trans_coeff = None
        else:
            norm_trans_coeff = config.norm_trans_coeff.toValErrTuple()

        
        n_som2 = dr_lib.process_dgs_data(n_som1, config, b_som1, e_som1,
                                         norm_trans_coeff,
                                         dataset_type="normalization",
                                         timer=tim)
    else:
        n_som2 = n_som1
        
    del n_som1, b_som1, e_som1

    # Step 17: Integrate normalization spectra
    if n_som2 is not None:
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
            
        norm_int = dr_lib.integrate_spectra(n_som2, start=start_val,
                                            end=end_val, width=True)

        if tim is not None:
            tim.getTime(msg="After integrating normalization spectra ")

        if config.dump_norm:
            file_comment = "Normalization Integration range: %0.3fA, %0.3fA" \
                           % (start_val, end_val)
            
            hlr_utils.write_file(config.output, "text/num-info", norm_int,
                                 output_ext="norm",
                                 data_ext=config.ext_replacement,
                                 path_replacement=config.path_replacement,
                                 verbose=config.verbose,
                                 message="normalization values",
                                 comments=[file_comment],
                                 tag="Integral", units="counts")   
    else:
        norm_int = n_som2
        
    del n_som2

    # Step 18: Normalize sample data by integrated values
    if norm_int is not None:
        if config.verbose:
            print "Normalizing data by normalization data"

        if tim is not None:
            tim.getTime(False)

        d_som3 = common_lib.div_ncerr(d_som2, norm_int)            

        if tim is not None:
            tim.getTime(msg="After normalizing data ")
    else:
        d_som3 = d_som2

    del d_som2, norm_int

    # Step 19: Calculate the initial energy
    if config.initial_energy is not None:
        d_som3.attr_list["Initial_Energy"] = config.initial_energy

    # Steps 20-21: Calculate the energy transfer
    if config.verbose:
        print "Calculating energy transfer"

    if tim is not None:
        tim.getTime(False)

    #import profile
    #profiler = profile.Profile()
    #d_som4 = profiler.runcall(dr_lib.energy_transfer, d_som3, "DGS",
    #                          "Initial_Energy", lojac=True,
    #                          scale=config.lambda_ratio)
    #profiler.dump_stats("et_profile.dat")
    d_som4 = dr_lib.energy_transfer(d_som3, "DGS", "Initial_Energy",
                                    lojac=True, scale=config.lambda_ratio)
    

    if tim is not None:
        tim.getTime(msg="After calculating energy transfer ")

    del d_som3

    # Rebin energy transfer spectra
    if config.verbose:
        print "Rebinning to final energy transfer axis"

    if tim is not None:
        tim.getTime(False)
        
    d_som5 = common_lib.rebin_axis_1D(d_som4, config.E_bins.toNessiList())

    if tim is not None:
        tim.getTime(msg="After rebinning energy transfer ")

    del d_som4

    if config.dump_et_comb:
        d_som5_1 = dr_lib.sum_all_spectra(d_som5)
        hlr_utils.write_file(config.output, "text/Spec", d_som5_1,
                             output_ext="et",
                             data_ext=config.ext_replacement,    
                             path_replacement=config.path_replacement,
                             verbose=config.verbose,
                             message="combined energy transfer information")

        del d_som5_1

    # Get the corner geometry information
    if config.verbose:
        print "Reading in corner geometry information"
        
    if tim is not None:
        tim.getTime(False)
        
    corner_angles = hlr_utils.get_corner_geometry(corner_geom)

    if tim is not None:
        tim.getTime(msg="After reading in corner geometry information ")

    if config.verbose:
        print "Creating S(Q, E)"

    if tim is not None:
        tim.getTime(False)
        
    d_som5_2 = dr_lib.create_E_vs_Q_dgs(d_som5,
                                        config.initial_energy.toValErrTuple(),
                                        config.Q_bins.toNessiList(),
                                        corner_geom=corner_angles,
                                        split=config.split,
                                        configure=config,
                                        timer=tim)

    # Writing 2D DAVE file
    if not config.split:
        hlr_utils.write_file(config.output, "text/Dave2d", d_som5_2,
                             output_ext="sqe",
                             data_ext=config.ext_replacement,    
                             path_replacement=config.path_replacement,
                             verbose=config.verbose,
                             message="S(Q,E)")
                                               
    if tim is not None:
        tim.getTime(msg="After calculating S(Q,E) spectrum ")    

    del d_som5_2

    if config.qmesh:
        # Create Qvec vs E spectrum
        if config.verbose:
            print "Creating S(Qvec, E)"

        if tim is not None:
            tim.getTime(False)
        
        dr_lib.create_Qvec_vs_E_dgs(d_som5,
                                    config.initial_energy.toValErrTuple(),
                                    config, corner_geom=corner_angles,
                                    make_fixed=config.fixed,
                                    output=config.output,
                                    timer=tim)
        
        if tim is not None:
            tim.getTime(msg="After calculating final spectrum ")    

    # Write out RMD file
    d_som5.attr_list["config"] = config

    hlr_utils.write_file(config.output, "text/rmd", d_som5,
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
    description.append("This driver runs the data reduction for the Direct")
    description.append("Geometry Spectrometer class of instruments.")
    
    # Set up the options available
    parser = hlr_utils.DgsRedOptions("usage: %prog [options] <datafile>", None,
                                     None, hlr_utils.program_version(),
                                     'error',
                                     " ".join(description))

    # Set defaults for options
    parser.set_defaults(usmon_path="/entry/monitor1,1")
    parser.set_defaults(dsmon_path="/entry/monitor2,1")

    # Add dgs_reduction specific options
    parser.add_option("", "--timing", action="store_true", dest="timing",
                      help="Flag to turn on timing of code")
    parser.set_defaults(timing=False)

    (options, args) = parser.parse_args()

    # Set up the configuration
    configure = hlr_utils.Configure()

    # Call the configuration setter for DgsRedOptions
    hlr_utils.DgsRedConfiguration(parser, configure, options, args)

    # Set timer object if timing option is used
    if options.timing:
        import sns_timing
        timer = sns_timing.DiffTime()
    else:
        timer = None
    
    # Run the program
    run(configure, timer)
