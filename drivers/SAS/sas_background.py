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
    

    if tim is not None:
        tim.setOldTime(old_time)
        tim.getTime(msg="Total Running Time")    

if __name__ == "__main__":
    import hlr_utils

    # Make description for driver
    result = []
    result.append("This driver creates a background spectrum for")
    result.append("Small-Angle Scattering detectors that will be fit and")
    result.append("subtracted during data reduction.")

    # Set up the options available
    parser = hlr_utils.SansOptions("usage: %prog [options] <datafile>", None,
                                  None, hlr_utils.program_version(), 'error',
                                  " ".join(result))

    # Set defaults for imported options
    parser.set_defaults(data_paths="/entry/bank1,1")
    parser.set_defaults(bmon_path="/entry/monitor1,1")

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
    parser.remove_option("--bkg-coeff")
    parser.remove_option("--mom-trans-bins")
    parser.remove_option("--dump-wave-bmnorm")
    parser.remove_option("--dump-frac-rebin")

    # Add sas_background specific options
    parser.add_option("", "--timing", action="store_true", dest="timing",
                      help="Flag to turn on timing of code")
    parser.set_defaults(timing=False)
    
    (options, args) = parser.parse_args()

    # Set up the configuration
    configure = hlr_utils.Configure()

    # Call the configuration setter for SansOptions
    hlr_utils.SansConfiguration(parser, configure, options, args)

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
