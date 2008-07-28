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
This program performs steps 1-4,6-8 outlined in B{Section 2.5.1:
Pixel-by-Pixel Reduction in One Dimension}
U{http://neutrons.ornl.gov/asg/projects/SCL/reqspec/DR_Lib_RS.doc} on two
datasets and divides those processed datasets to produce a transmisson file.
This is done in the absence of transmission monitors.
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

    if config.back is None:
        only_background = True
        data_type = "data"
    else:
        only_background = False
        data_type = "transmission"
        
    # Perform Steps 1-4,6-8 on sample data
    d_som1 = dr_lib.process_sas_data(config.data, config, timer=tim,
                                     inst_geom_dst=inst_geom_dst,
                                     dataset_type=data_type,
                                     transmission=True,
                                     get_background=only_background)

    # Perform Steps 1-4,6-8 on background data
    if config.back is not None:
        b_som1 = dr_lib.process_sas_data(config.back, config, timer=tim,
                                         inst_geom_dst=inst_geom_dst,
                                         dataset_type="trans_bkg",
                                         transmission=True)
    else:
        b_som1 = None

    # Put the datasets on the same axis
    d_som2 = dr_lib.sum_by_rebin_frac(d_som1, config.lambda_bins.toNessiList())
    del d_som1

    if b_som1 is not None:
        b_som2 = dr_lib.sum_by_rebin_frac(b_som1,
                                          config.lambda_bins.toNessiList())
    else:
        b_som2 = None
        
    del b_som1    
    
    # Divide the data spectrum by the background spectrum
    if b_som2 is not None:
        d_som3 = common_lib.div_ncerr(d_som2, b_som2)
    else:
        d_som3 = d_som2

    del d_som2, b_som2

    # Reset y units to dimensionless for the tranmission due to ratio
    if config.back is not None:
        d_som3.setYLabel("Ratio")
        d_som3.setYUnits("")
        write_message = "transmission spectrum"
    else:
        write_message = "spectrum for background estimation"

    # Write out the transmission spectrum
    hlr_utils.write_file(config.output, "text/Spec", d_som3,
                         verbose=config.verbose,
                         replace_path=False,
                         replace_ext=False,
                         message=write_message)

    d_som3.attr_list["config"] = config

    hlr_utils.write_file(config.output, "text/rmd", d_som3,
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
    result.append("This driver creates a transmission spectrum for")
    result.append("Small-Angle Scattering detectors in the absence of")
    result.append("a transmission monitor.")

    # Set up the options available
    parser = hlr_utils.SansOptions("usage: %prog [options] <datafile>", None,
                                  None, hlr_utils.program_version(), 'error',
                                  " ".join(result))

    # Set defaults for imported options
    parser.set_defaults(data_paths="/entry/bank1,1")
    parser.set_defaults(bmon_path="/entry/monitor1,1")
    parser.set_defaults(tmon_path="/entry/monitor2,1")

    # Remove unnecessary options
    parser.remove_option("--data-trans")
    parser.remove_option("--tmon-path")
    parser.remove_option("--ecan")
    parser.remove_option("--ecan-trans")
    parser.remove_option("--solv")
    parser.remove_option("--solv-trans")
    parser.remove_option("--open")
    parser.remove_option("--dkcur")
    parser.remove_option("--rescale-final")
    parser.remove_option("--mom-trans-bins")
    parser.remove_option("--dump-wave-bmnorm")
    parser.remove_option("--dump-frac-rebin")
    
    # Add sas_transmission specific options
    parser.add_option("", "--back",
                      help="Specify the background file that will divide the "\
                      +"data.")
    
    parser.add_option("", "--timing", action="store_true", dest="timing",
                      help="Flag to turn on timing of code")
    parser.set_defaults(timing=False)
    
    (options, args) = parser.parse_args()

    # Set up the configuration
    configure = hlr_utils.Configure()

    # Call the configuration setter for SansOptions
    hlr_utils.SansConfiguration(parser, configure, options, args)

    # Set the background file list
    if hlr_utils.cli_provide_override(configure, "back", "--back"):
        configure.back = hlr_utils.determine_files(options.back,
                                                   configure.inst,
                                                   configure.facility)

    if configure.lambda_bins is None:
        parser.error("Please specify the final wavelength axis!")

    # Set timer object if timing option is used
    if options.timing:
        import sns_timing
        timer = sns_timing.DiffTime()
    else:
        timer = None
    
    # Run the program
    run(configure, timer)
