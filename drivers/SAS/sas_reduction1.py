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
This program covers the functionality outlined in B{Section 2.5.1:
Pixel-by-Pixel Reduction in One Dimension}
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

    # Perform Steps 1-9 on sample data
    d_som1 = dr_lib.process_sas_data(config.data, config, timer=tim,
                                     inst_geom_dst=inst_geom_dst,
                                     bkg_subtract=config.bkg_coeff,
                                     trans_data=config.data_trans)

    # Perform Steps 1-9 on buffer/solvent only data
    if config.solv is not None:
        s_som1 = dr_lib.process_sas_data(config.solv, config, timer=tim,
                                         inst_geom_dst=inst_geom_dst,
                                         dataset_type="solvent")
    else:
        s_som1 = None

    # Step 10: Subtract buffer/solvent only spectrum from sample spectrum
    d_som2 = dr_lib.subtract_bkg_from_data(d_som1, s_som1,
                                           verbose=config.verbose,
                                           timer=tim,
                                           dataset1="data",
                                           dataset2="solvent")
    
    del s_som1, d_som1

    # Perform Steps 1-9 on empty-can data
    if config.ecan is not None:
        e_som1 = dr_lib.process_sas_data(config.ecan, config, timer=tim,
                                         inst_geom_dst=inst_geom_dst,
                                         dataset_type="empty_can",
                                         trans_data=config.ecan_trans)
    else:
        e_som1 = None

    # Step 11: Subtract empty-can spectrum from sample spectrum
    d_som3 = dr_lib.subtract_bkg_from_data(d_som2, e_som1,
                                           verbose=config.verbose,
                                           timer=tim,
                                           dataset1="data",
                                           dataset2="empty_can")
    
    del e_som1, d_som2

    # Perform Steps 1-9 on open beam data
    if config.open is not None:
        o_som1 = dr_lib.process_sas_data(config.open, config, timer=tim,
                                         inst_geom_dst=inst_geom_dst,
                                         dataset_type="open_beam")
    else:
        o_som1 = None
        
    # Step 12: Subtract open beam spectrum from sample spectrum
    d_som4 = dr_lib.subtract_bkg_from_data(d_som3, o_som1,
                                           verbose=config.verbose,
                                           timer=tim,
                                           dataset1="data",
                                           dataset2="open_beam")
    
    del o_som1, d_som3

    # Perform Steps 1-9 on dark current data
    if config.dkcur is not None:
        dc_som1 = dr_lib.process_sas_data(config.open, config, timer=tim,
                                          inst_geom_dst=inst_geom_dst,
                                          dataset_type="dark_current")
    else:
        dc_som1 = None
        
    # Step 13: Subtract dark current spectrum from sample spectrum
    d_som5 = dr_lib.subtract_bkg_from_data(d_som4, dc_som1,
                                           verbose=config.verbose,
                                           timer=tim,
                                           dataset1="data",
                                           dataset2="dark_current")
    
    del dc_som1, d_som4    

    # Steps 14 and 15: Rebin and sum all spectra
    if config.verbose:
        print "Rebinning and summing for final spectrum"

    if tim is not None:
        tim.getTime(False)

    if config.dump_frac_rebin:
        set_conf = config
    else:
        set_conf = None

    d_som6 = dr_lib.sum_by_rebin_frac(d_som5, config.Q_bins.toNessiList(),
                                      configure=set_conf)

    if tim is not None:
        tim.getTime(msg="After rebinning and summing for spectrum")    

    del d_som5

    if config.verbose:
        print "Scaling final spectrum by Q centers"
        
    if tim is not None:
        tim.getTime(False)

    d_som7 = dr_lib.fix_bin_contents(d_som6, scale=True, width=True,
                                     units="1/Angstroms")

    if tim is not None:
        tim.getTime(msg="After scaling final spectrum")    

    del d_som6
    
    hlr_utils.write_file(config.output, "text/Spec", d_som7,
                         verbose=config.verbose,
                         replace_path=False,
                         replace_ext=False,
                         message="combined S(Q) information")

    d_som7.attr_list["config"] = config

    hlr_utils.write_file(config.output, "text/rmd", d_som7,
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
    result = []
    result.append("This driver runs the data reduction for Small-Angle")
    result.append("Scattering instruments. The standard output is a *.txt")
    result.append("file for S(Q). Other")
    result.append("intermediate files can be produced by using the ")
    result.append("appropriate dump-X flag described in this help. The file")
    result.append("extensions are described in the option documentation.")

    # Set up the options available
    parser = hlr_utils.SansOptions("usage: %prog [options] <datafile>", None,
                                  None, hlr_utils.program_version(), 'error',
                                  " ".join(result))

    # Set defaults for imported options
    parser.set_defaults(data_paths="/entry/bank1,1")
    parser.set_defaults(bmon_path="/entry/monitor1,1")
    # FIXME
    parser.set_defaults(tmon_path="/entry/monitor2,1")
    
    # Add sas_reduction specific options
    parser.add_option("", "--timing", action="store_true", dest="timing",
                      help="Flag to turn on timing of code")
    parser.set_defaults(timing=False)
    
    (options, args) = parser.parse_args()

    # Set up the configuration
    configure = hlr_utils.Configure()

    # Call the configuration setter for SansOptions
    hlr_utils.SansConfiguration(parser, configure, options, args)

    # Set timer object if timing option is used
    if options.timing:
        import sns_timing
        timer = sns_timing.DiffTime()
    else:
        timer = None
    
    # Run the program
    run(configure, timer)
    
