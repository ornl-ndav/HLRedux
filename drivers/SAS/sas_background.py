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
This program covers the functionality outlined in B{Section 2.5.2:
Background Spectrum Creation}
U{http://neutrons.ornl.gov/asg/projects/SCL/reqspec/DR_Lib_RS.doc} as
developed for the I{LENS} facility.
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

    # Add so_axis to Configure object
    config.so_axis = "time_of_flight"

    dataset_type = "background"

    # Step 0: Open appropriate data files

    # Data
    if config.verbose:
        print "Reading %s file" % dataset_type

    # The [0] is to get the data SOM and ignore the None background SOM
    dp_som = dr_lib.add_files(config.data,
                              Data_Paths=config.data_paths.toPath(),
                              SO_Axis=config.so_axis,
                              Signal_ROI=config.roi_file,
                              dataset_type=dataset_type,
                              Verbose=config.verbose, Timer=tim)
    
    if tim is not None:
        tim.getTime(msg="After reading %s " % dataset_type)

    dp_som0 = dr_lib.fix_bin_contents(dp_som)

    del dp_som

    if inst_geom_dst is not None:
        inst_geom_dst.setGeometry(config.data_paths.toPath(), dp_som0)

    # Note: time_zero_offset_det MUST be a tuple
    if config.time_zero_offset_det is not None:
        dp_som0.attr_list["Time_zero_offset_det"] = \
                                   config.time_zero_offset_det.toValErrTuple()

    # Step 2: Convert TOF to wavelength for data
    if config.verbose:
        print "Converting TOF to wavelength"

    if tim is not None:
        tim.getTime(False)

    # Convert detector pixels
    dp_som1 = common_lib.tof_to_wavelength_lin_time_zero(
        dp_som0,
        units="microsecond",
        time_zero_offset=config.time_zero_offset_det.toValErrTuple(),
        inst_param="total")

    if tim is not None:
        tim.getTime(msg="After converting TOF to wavelength ")

    del dp_som0

    if config.verbose:
        print "Cutting spectra"

    if tim is not None:
        tim.getTime(False)

    dp_som2 = dr_lib.cut_spectra(dp_som1, config.lambda_low_cut,
                                 config.lambda_high_cut)

    if tim is not None:
        tim.getTime(msg="After cutting spectra ")

    del dp_som1

    rebin_axis = config.lambda_bins.toNessiList()

    # Put the data on the same axis
    if config.verbose:
        print "Rebinning data onto specified wavelength axis"

    if tim is not None:
        tim.getTime(False)
        
    dp_som3 = dr_lib.sum_by_rebin_frac(dp_som2, rebin_axis)

    if tim is not None:
        tim.getTime(msg="After rebinning data onto specified wavelength axis ")
        
    del dp_som2

    data_run_time = dp_som3.attr_list["background-duration"]

    # Divide the data by the duration
    if config.verbose:
        print "Scaling data by the counting duration"
        
    if tim is not None:
        tim.getTime(False)
        
    dp_som4 = common_lib.div_ncerr(dp_som3, (data_run_time.getValue(), 0.0))

    if tim is not None:
        tim.getTime(msg="After scaling data by the counting duration ")
        
    del dp_som3

    # Calculate the accelerator on time
    if config.verbose:
        print "Calculating accelerator on time"
        
    acc_on_time = hlr_utils.DrParameter(data_run_time.getValue() -
                                        config.acc_down_time.getValue(), 0.0,
                                        "seconds")

    # Get the number of data bins
    num_wave_bins = len(rebin_axis) - 1

    # Calculate the scaled accelerator uptime
    if config.verbose:
        print "Calculating the scaled accelerator uptime"

    if tim is not None:
        tim.getTime(False)
        
    final_scale = acc_on_time.toValErrTuple()[0] / num_wave_bins
    
    print "A:", acc_on_time, num_wave_bins, final_scale
    if tim is not None:
        tim.getTime(msg="After calculating the scaled accelerator uptime ")
        
    # Create the final background spectrum
    if config.verbose:
        print "Creating the background spectrum"

    if tim is not None:
        tim.getTime(False)
        
    dp_som5 = common_lib.div_ncerr(dp_som4, (final_scale, 0))
    dp_som5.attr_list["%s-Scaling" % dataset_type] = final_scale

    if tim is not None:
        tim.getTime(msg="After creating background spectrum ")
        
    del dp_som4

    # Write out the background spectrum
    hlr_utils.write_file(config.output, "text/Spec", dp_som5,
                         verbose=config.verbose,
                         output_ext="bkg",
                         data_ext=config.ext_replacement,
                         replace_path=False,
                         replace_ext=True,
                         message="background spectrum")

    dp_som5.attr_list["config"] = config

    hlr_utils.write_file(config.output, "text/rmd", dp_som5,
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
    result.append("This driver creates a background spectrum for")
    result.append("Small-Angle Scattering detectors that will be fit and")
    result.append("subtracted during data reduction. The result of running")
    result.append("this driver is a 3-column ASCII file with an extension")
    result.append("of *.bkg")

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
    parser.remove_option("--bmon-path")
    parser.remove_option("--tmon-path")
    parser.remove_option("--r-bins")
    parser.remove_option("--theta-bins")
    parser.remove_option("--time-zero-offset-mon")
    parser.remove_option("--ecan")
    parser.remove_option("--ecan-trans")
    parser.remove_option("--solv")
    parser.remove_option("--solv-trans")
    parser.remove_option("--open")
    parser.remove_option("--dkcur")
    parser.remove_option("--mon-effc")
    parser.remove_option("--mon-eff-const")
    parser.remove_option("--rescale-final")
    parser.remove_option("--bkg-coeff")
    parser.remove_option("--mom-trans-bins")
    parser.remove_option("--dump-wave")
    parser.remove_option("--dump-bmon-wave")
    parser.remove_option("--dump-bmon-effc")
    parser.remove_option("--dump-bmon-rebin")
    parser.remove_option("--dump-wave-bmnorm")
    parser.remove_option("--dump-frac-rebin")
    parser.remove_option("--dump-tof-r")
    parser.remove_option("--dump-wave-r")
    parser.remove_option("--dump-Q-r")
    parser.remove_option("--dump-tof-theta")
    parser.remove_option("--dump-wave-theta")
    parser.remove_option("--dump-Q-theta")
    parser.remove_option("--dump-2d")
    parser.remove_option("--dump-all")

    # Add sas_background specific options
    parser.add_option("", "--acc-down-time", dest="acc_down_time",
                      help="Please provide the duration (seconds) that the "\
                      +"accelerator is down.")
    parser.set_defaults(acc_down_time="0.0,0.0,seconds")
    
    parser.add_option("", "--timing", action="store_true", dest="timing",
                      help="Flag to turn on timing of code")
    parser.set_defaults(timing=False)
    
    (options, args) = parser.parse_args()

    # Set up the configuration
    configure = hlr_utils.Configure()

    # Call the configuration setter for SansOptions
    hlr_utils.SansConfiguration(parser, configure, options, args)

    # Set the accelerator down time
    if hlr_utils.cli_provide_override(configure, "acc_down_time",
                                      "--acc-down-time"):
        configure.acc_down_time = hlr_utils.DrParameterFromString(\
            options.acc_down_time, True)

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
