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
This program covers the functionality outlined in B{Section 2.2.1 Powder or
amorphous material reduction} in
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

    # Perform early background subtraction if the hwfix flag is used
    if config.hwfix:
        if not config.mc:
            so_axis = "time_of_flight"
        else:
            so_axis = "Time_of_Flight"
        
        bkg_som = dr_lib.add_files(config.back,
                                   Data_Paths=config.data_paths.toPath(),
                                   SO_Axis=so_axis, Signal_ROI=config.roi_file,
                                   dataset_type="background",
                                   Verbose=config.verbose, Timer=tim)[0]
    else:
        bkg_som = None

    # Perform Steps 1-9 on sample data
    d_som1 = dr_lib.process_igs_data(config.data, config, timer=tim,
                                     inst_geom_dst=inst_geom_dst,
                                     tib_const=config.tib_data_const,
                                     bkg_som=bkg_som)

    # Perform Steps 1-9 on empty can data
    if config.ecan is not None:
        e_som1 = dr_lib.process_igs_data(config.ecan, config, timer=tim,
                                         inst_geom_dst=inst_geom_dst,
                                         dataset_type="empty_can",
                                         tib_const=config.tib_ecan_const,
                                         bkg_som=bkg_som)
    else:
        e_som1 = None

    # Perform Steps 1-9 on normalization data            
    if config.norm is not None:
        n_som1 = dr_lib.process_igs_data(config.norm, config, timer=tim,
                                         inst_geom_dst=inst_geom_dst,
                                         dataset_type="normalization",
                                         tib_const=config.tib_norm_const,
                                         bkg_som=bkg_som)
    else:
        n_som1 = None

    # Perform Steps 1-9 on background data
    if config.back is not None and not config.hwfix:
        b_som1 = dr_lib.process_igs_data(config.back, config, timer=tim,
                                         inst_geom_dst=inst_geom_dst,
                                         dataset_type="background",
                                         tib_const=config.tib_back_const)
    else:
        b_som1 = None

    if inst_geom_dst is not None:
        inst_geom_dst.release_resource()
        
    # Step 10: Subtract background spectrum from sample spectrum    
    d_som2 = dr_lib.subtract_bkg_from_data(d_som1, b_som1,
                                           verbose=config.verbose,
                                           timer=tim,
                                           dataset1="data",
                                           dataset2="background")

    # Step 11: Subtract background spectrum from empty can spectrum    
    e_som2 = dr_lib.subtract_bkg_from_data(e_som1, b_som1,
                                           verbose=config.verbose,
                                           timer=tim,
                                           dataset1="empty_can",
                                           dataset2="background")

    # Step 12: Subtract background spectrum from normalization spectrum
    n_som2 = dr_lib.subtract_bkg_from_data(n_som1, b_som1,
                                           verbose=config.verbose,
                                           timer=tim,
                                           dataset1="normalization",
                                           dataset2="background")
    del b_som1

    # Step 13: Subtract empty can spectrum from sample spectrum    
    d_som3 = dr_lib.subtract_bkg_from_data(d_som2, e_som2,
                                           verbose=config.verbose,
                                           timer=tim,
                                           dataset1="data",
                                           dataset2="empty_can")

    del d_som2
    
    # Step 14: Subtract empty can spectrum from normalization spectrum
    n_som3 = dr_lib.subtract_bkg_from_data(n_som2, e_som2,
                                           verbose=config.verbose,
                                           timer=tim,
                                           dataset1="normalization",
                                           dataset2="empty_can")    

    del n_som2, e_som2

    # Step 15: Integrate normalization spectra
    if config.verbose and n_som3 is not None:
        print "Integrating normalization spectra"

    norm_int = dr_lib.integrate_spectra(n_som3, start=config.norm_start,
                                        end=config.norm_end)

    del n_som3
        
    # Step 16: Normalize data by integrated values
    if config.verbose and norm_int is not None:
        print "Normalizing data by normalization data"

    if norm_int is not None:
        d_som4 = common_lib.div_ncerr(d_som3, norm_int)
    else:
        d_som4 = d_som3

    if norm_int is not None:
        if tim is not None:
            tim.getTime(msg="After normalizing data ")

    del d_som3, norm_int

    # Step 17: Convert initial wavelength to E_initial
    if config.verbose:
        print "Converting initial wavelength to E_initial"
        
    if tim is not None:
        tim.getTime(False)

    d_som6 = common_lib.wavelength_to_energy(d_som4)
        
    if tim is not None:
        tim.getTime(msg="After converting initial wavelength to E_initial ")

    if config.dump_initial_energy:
        hlr_utils.write_file(config.output, "text/Spec", d_som6,
                             output_ext="ixl",
                             data_ext=config.ext_replacement,
                             path_replacement=config.path_replacement,
                             verbose=config.verbose,
                             message="pixel initial energy information")
            
    del d_som4

    # Steps 19-20: Calculate energy transfer
    if config.verbose:
        print "Calculating energy transfer"

    if tim is not None:
        tim.getTime(False)

    d_som7 = dr_lib.igs_energy_transfer(d_som6)

    if tim is not None:
        tim.getTime(msg="After calculating energy transfer ")
        
    if config.dump_energy:
        hlr_utils.write_file(config.output, "text/Spec", d_som7,
                             output_ext="exl",
                             data_ext=config.ext_replacement,
                             path_replacement=config.path_replacement,
                             verbose=config.verbose,
                             message="pixel energy transfer information")

    # Write 3-column ASCII file for E_t
    d_som7_1 = dr_lib.sum_all_spectra(d_som7,
                                      rebin_axis=config.E_bins.toNessiList())
    hlr_utils.write_file(config.output, "text/Spec", d_som7_1,
                         output_ext="etr",
                         data_ext=config.ext_replacement,
                         path_replacement=config.path_replacement,
                         verbose=config.verbose,
                         message="combined energy transfer information") 
    
    del d_som7_1

    # Steps 18-20: Calculate scaled energy transfer
    if config.verbose:
        print "Calculating scaled energy transfer"
        
    d_som9 = dr_lib.igs_energy_transfer(d_som6, scale=True)
    
    if tim is not None:
        tim.getTime(msg="After calculating scaled energy transfer ")

    if config.dump_energy:
        hlr_utils.write_file(config.output, "text/Spec", d_som9,
                             output_ext="sexl",
                             data_ext=config.ext_replacement,    
                             path_replacement=config.path_replacement,
                             verbose=config.verbose,
                             message="pixel scaled energy transfer "\
                             +"information")

    # Write 3-column ASCII file for scaled E_t
    d_som9_1 = dr_lib.sum_all_spectra(d_som9,
                                      rebin_axis=config.E_bins.toNessiList())
    hlr_utils.write_file(config.output, "text/Spec", d_som9_1,
                         output_ext="setr",
                         data_ext=config.ext_replacement,            
                         path_replacement=config.path_replacement,
                         verbose=config.verbose,
                         message="combined scaled energy transfer "\
                         +"information") 
    
    del d_som9_1
    
    del d_som6, d_som7
        
    d_som9.attr_list["config"] = config
    
    hlr_utils.write_file(config.output, "text/rmd", d_som9,
                         output_ext="rmd",
                         data_ext=config.ext_replacement,         
                         path_replacement=config.path_replacement,
                         verbose=config.verbose,
                         message="metadata")
    
    if tim is not None:
        tim.setOldTime(old_time)
        tim.getTime(msg="Total Running Time: ")
    
if __name__ == "__main__":
    import hlr_utils

    # Make description for driver
    result = []
    result.append("This driver runs the data reduction for the inelastic")
    result.append("banks for the BSS instrument. The standard output is a")
    result.append("a *.setr file (3-column ASCII) for S(E) and a *.etr file")
    result.append("(3-column ASCII) for sigma(E). Other intermediate files")
    result.append("can be produced by using the appropriate dump-X flag")
    result.append("described in this help. The file extensions are described")
    result.append("in the option documentation.")
 
    # Set up the options available
    parser = hlr_utils.AmrOptions("usage: %prog [options] <datafile>", None,
                                  hlr_utils.program_version(), 'error',
                                  " ".join(result))

    # Set defaults for imported options
    parser.set_defaults(inst="BSS")
    parser.set_defaults(data_paths="/entry/bank1,1,/entry/bank2,1")
    parser.set_defaults(mon_path="/entry/monitor,1")
    parser.set_defaults(norm_start="6.24")
    parser.set_defaults(norm_end="6.30")

    # Remove unneeded options
    parser.remove_option("--mom-trans-bins")
    
    # Add amorphous_reduction specific options
    parser.add_option("", "--timing", action="store_true", dest="timing",
                      help="Flag to turn on timing of code")
    parser.set_defaults(timing=False)
    
    (options, args) = parser.parse_args()

    # Set up the configuration
    configure = hlr_utils.Configure()

    # Set Q_bins to be dummy to avoid Q axis trap
    configure.Q_bins = ""

    # Call the configuration setter for AmrOptions
    hlr_utils.AmrConfiguration(parser, configure, options, args)

    # Set timer object if timing option is used
    if options.timing:
        import sns_timing
        timer = sns_timing.DiffTime()
    else:
        timer = None
    
    # Run the program
    run(configure, timer)
