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
This driver repeats the procedures found in B{Section 2.2.1 Powder or
amorphous material reduction} of 
U{http://neutrons.ornl.gov/asg/projects/SCL/reqspec/DR_Lib_RS.doc} to find the 
normalization efficiency on a per-pixel basis from a vanadium run file. It 
will repeat steps 1-8,15,22-25,28-31
"""

def run(config, tim):
    """
    This method is where the data reduction process gets done.

    @param config: Object containing the data reduction configuration
                   information.
    @type config: L{hlr_utils.Configure}

    @param tim: Object that will allow the method to perform
    timing evaluations.
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

    # Perform early background subtraction if the hwfix flag is used
    if config.hwfix:
        if not config.mc:
            so_axis = "time_of_flight"
        else:
            so_axis = "Time_of_Flight"
            
        bkg_som0 = dr_lib.add_files(config.back,
                                    Data_Paths=config.data_paths.toPath(),
                                    SO_Axis=so_axis,
                                    Signal_ROI=config.roi_file,
                                    dataset_type="background",
                                    Verbose=config.verbose, Timer=tim)[0]

        bkg_som = dr_lib.fix_bin_contents(bkg_som0)
        del bkg_som0
    else:
        bkg_som = None

    # Perform Steps 1-8,15 on normalization data            
    n_som1 = dr_lib.process_igs_data(config.data, config, timer=tim,
                                     inst_geom_dst=inst_geom_dst,
                                     dataset_type="normalization",
                                     tib_const=config.tib_norm_const,
                                     bkg_som=bkg_som)
    
    # Perform Steps 1-8,15 on empty can data
    if config.ecan is not None:
        e_som1 = dr_lib.process_igs_data(config.ecan, config, timer=tim,
                                         inst_geom_dst=inst_geom_dst,
                                         dataset_type="empty_can",
                                         tib_const=config.tib_ecan_const,
                                         bkg_som=bkg_som)
    else:
        e_som1 = None

    # Perform Steps 1-8,15 on background data
    if config.back is not None and not config.hwfix:
        b_som1 = dr_lib.process_igs_data(config.back, config, timer=tim,
                                         inst_geom_dst=inst_geom_dst,
                                         dataset_type="background",
                                         tib_const=config.tib_back_const)
    else:
        b_som1 = None

    if inst_geom_dst is not None:
        inst_geom_dst.release_resource()

    # Steps 22-23: Subtract background spectrum from empty can spectrum for
    #              normalization
    e_som2 = dr_lib.subtract_bkg_from_data(e_som1, b_som1,
                                           verbose=config.verbose,
                                           timer=tim,
                                           dataset1="empty_can",
                                           dataset2="background",
                                           scale=config.scale_bcn)

    # Step 24-25: Subtract background spectrum from normalization spectrum
    n_som2 = dr_lib.subtract_bkg_from_data(n_som1, b_som1,
                                           verbose=config.verbose,
                                           timer=tim,
                                           dataset1="normalization",
                                           dataset2="background",
                                           scale=config.scale_bn)
    del b_som1

    # Step 28-29: Subtract empty can spectrum from normalization spectrum
    n_som3 = dr_lib.subtract_bkg_from_data(n_som2, e_som2,
                                           verbose=config.verbose,
                                           timer=tim,
                                           dataset1="normalization",
                                           dataset2="empty_can",
                                           scale=config.scale_cn)

    del n_som2, e_som2

    # Step 30-31: Integrate normalization spectra
    if config.verbose:
        print "Integrating normalization spectra"

    norm_int = dr_lib.integrate_spectra(n_som3, start=config.norm_start,
                                        end=config.norm_end, norm=True)

    n_som3.attr_list["config"] = config
    
    hlr_utils.write_file(config.output, "text/rmd", n_som3,
                         output_ext="rmd",
                         data_ext=config.ext_replacement,         
                         path_replacement=config.path_replacement,
                         verbose=config.verbose,
                         message="metadata")
    
    del n_som3

    file_comment = "Normalization Integration range: %0.3fA, %0.3fA" % \
                   (config.norm_start, config.norm_end)

    hlr_utils.write_file(config.output, "text/num-info", norm_int,
                         output_ext="norm",
                         data_ext=config.ext_replacement,
                         path_replacement=config.path_replacement,
                         verbose=config.verbose,
                         message="normalization values",
                         comments=[file_comment],
                         tag="Integral", units="counts")

    if tim is not None:
        tim.setOldTime(old_time)
        tim.getTime(msg="Total Running Time")

if __name__ == "__main__":
    import dr_lib
    import hlr_utils

    # Make description for driver
    result = []
    result.append("This driver finds the normalization efficiency for the")
    result.append("inelastic banks for the BSS instrument. The standard")
    result.append("output is a *.norm file (3-column ASCII) of the pixel")
    result.append("normalization efficiencies. Other intermediate files can")
    result.append("be produced by using the appropriate dump-X flag described")
    result.append("in this help. The file extensions are described in the")
    result.append("option documentation.")

    # Set up the options available
    parser = hlr_utils.IgsOptions("usage: %prog [options] <datafile>", None,
                                  None, hlr_utils.program_version(), 'error',
                                  " ".join(result))

    # Set defaults for imported options
    parser.set_defaults(inst="BSS")
    parser.set_defaults(data_paths="/entry/bank1,1,/entry/bank2,1")
    parser.set_defaults(mon_path="/entry/monitor,1")
    parser.set_defaults(norm_start="6.24")
    parser.set_defaults(norm_end="6.30")

    # Remove unnecessary options
    parser.remove_option("--dsback")
    parser.remove_option("--tib-dsback-const")
    parser.remove_option("--scale-bs")
    parser.remove_option("--scale-bcs")
    parser.remove_option("--scale-cs")
    parser.remove_option("--tof-elastic")    
    
    parser.add_option("", "--timing", action="store_true", dest="timing",
                      help="Flag to turn on timing of code")
    parser.set_defaults(timing=False)
    
    (options, args) = parser.parse_args()

    # Set up the configuration
    configure = hlr_utils.Configure()

    # Assume the data is in norm option and set into data option. Clear out
    # the norm option
    if len(args) == 0:
        if options.data is None:
            options.data = options.norm
            options.norm = None

    # Call the configuration setter for IgsOptions
    hlr_utils.IgsConfiguration(parser, configure, options, args)

    # Set timer object if timing option is used
    if options.timing:
        import sns_timing
        timer = sns_timing.DiffTime()
    else:
        timer = None
    
    # Run the program
    run(configure, timer)
