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
This program covers the functionality outlined in B{Section 2.4.6.1
Pixel-by-Pixel Reduction into 2D Maps} in
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
    import array_manip
    import common_lib
    import dr_lib
    import DST
    import SOM

    import math

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
    
    # Perform Steps 1-2 on sample data
    d_som1 = dr_lib.process_reflp_data(config.data, config, None,
                                       inst_geom_dst=data_inst_geom_dst,
                                       timer=tim)

    # Get the detector angle
    if config.omega is None:
        # Make a fake SO
        so = SOM.SO()
        try: 
            theta = hlr_utils.get_special(d_som1.attr_list["Theta"], so)
        except KeyError: 
            theta = (float('nan'), float('nan'))
    else:
        theta = config.omega.toFullTuple()
        
    if theta[0] is not None: 
        if theta[2] == "degrees" or theta[2] == "degree": 
            theta_rads = (theta[0] * (math.pi / 180.0), 0.0)
        else: 
            theta_rads = (theta[0], 0.0)
    else: 
        theta_rads = (float('nan'), float('nan'))

    d_som1.attr_list["data-theta"] = (theta_rads[0], theta_rads[1], "radians")

    # Perform Steps 1-3 on normalization data
    if config.norm is not None:
        n_som1 = dr_lib.process_reflp_data(config.norm, config,
                                           config.norm_roi_file,
                                           inst_geom_dst=norm_inst_geom_dst,
                                           timer=tim)
    else:
        n_som1 = None

    # Closing sample data instrument geometry file
    if data_inst_geom_dst is not None:
        data_inst_geom_dst.release_resource()

    # Closing normalization data instrument geometry file
    if norm_inst_geom_dst is not None:
        norm_inst_geom_dst.release_resource()        

    # Step 4: Divide data by normalization
    if config.verbose and config.norm is not None:
        print "Scale data by normalization"

    if tim is not None:
        tim.getTime(False)

    if config.norm is not None:
        # Need to rebin the normalization spectra to the data pixel spectra
        n_som2 = dr_lib.rebin_monitor(n_som1, d_som1, rtype="frac")
        # Now divide the spectra
        d_som2 = common_lib.div_ncerr(d_som1, n_som2)
        del n_som2
    else:
        d_som2 = d_som1

    if tim is not None and config.norm is not None:
        tim.getTime(msg="After normalizing signal spectra")

    del d_som1, n_som1

    sin_theta_rads = (math.sin(theta_rads[0]), math.sin(theta_rads[1]))

    # Step 6: Scale wavelength axis by sin(theta) to make lambda_T
    if config.verbose:
        print "Scaling wavelength axis by sin(theta)"
    
    if tim is not None:
        tim.getTime(False)
        
    d_som3 = common_lib.div_ncerr(d_som2, sin_theta_rads, axis="x")

    if tim is not None:
        tim.getTime(msg="After scaling wavelength axis ")

    del d_som2

    d_som3.setAxisLabel(0, "lambda_T")

    # Step 7: Rebin to lambda_T axis
    if config.verbose:
        print "Rebinning spectra"

    if config.lambdap_bins is None:
        # Create a binning scheme
        pathlength = d_som3.attr_list.instrument.get_total_path(
            det_secondary=True)

        delta_lambda = common_lib.tof_to_wavelength((config.delta_TOF, 0.0),
                                                    pathlength=pathlength)
 
        delta_lambdap = array_manip.div_ncerr(delta_lambda[0], delta_lambda[1],
                                              sin_theta_rads[0], 0.0)

        config.lambdap_bins = dr_lib.create_axis_from_data(d_som3,
                                                       width=delta_lambdap[0])

    else:
        # Do nothing, got the binning scheme
        pass

    if tim is not None:
        tim.getTime(False)

    d_som4 = common_lib.rebin_axis_1D_frac(d_som3,
                                           config.lambdap_bins.toNessiList())

    if tim is not None:
        tim.getTime(msg="After rebinning spectra ")

    del d_som3

    # Step 8: Write out all spectra to a file
    hlr_utils.write_file(config.output, "text/Spec", d_som4,
                         replace_ext=False,
                         replace_path=False,
                         verbose=config.verbose,
                         message="Reflectivity information")

    if config.dump_twod:
        d_som5 = dr_lib.create_X_vs_pixpos(d_som4,
                                           config.lambdap_bins.toNessiList(),
                                           rebin=False,
                                           y_label="R",
                                           y_units="",
                                           x_label="$\lambda_T$",
                                           x_units="$\AA$")

        hlr_utils.write_file(config.output, "text/Dave2d", d_som5,
                             output_ext="plp", verbose=config.verbose,
                             data_ext=config.ext_replacement,
                             path_replacement=config.path_replacement,
                             message="2D Reflectivity information")

    d_som4.attr_list["config"] = config

    hlr_utils.write_file(config.output, "text/rmd", d_som4,
                         output_ext="rmd", verbose=config.verbose,
                         data_ext=config.ext_replacement,
                         path_replacement=config.path_replacement,
                         message="metadata")

    if tim is not None:
        tim.setOldTime(old_time)
        tim.getTime(msg="Total Running Time")    

if __name__ == "__main__":
    import hlr_utils

    # Make description for driver
    result = []
    result.append("This driver runs the data reduction for REF_M and REF_L")
    result.append("instruments in helping\nto produce 2D maps of pixel ID")
    result.append("versus perpendicular wavelength (lambda_T). The standard")
    result.append("output is a *.txt file (3-column ASCII) for R(lambda_T).")
    result.append("Other intermediate files can be produced")
    result.append("by using the appropriate dump-X flag described in this")
    result.append("help. The file extensions are described in the option")
    result.append("documentation.")

    # Set up the options available
    parser = hlr_utils.RefOptions("usage: %prog [options] <datafile>", None,
                                  None, hlr_utils.program_version(), 'error',
                                  " ".join(result))

    # Defaults for REF
    parser.set_defaults(data_paths="/entry/bank1,1")

    # Remove unneeded options
    parser.remove_option("--angle-offset")
    parser.remove_option("--data-roi-file")
    parser.remove_option("--dbkg-roi-file")
    parser.remove_option("--nbkg-roi-file")
    parser.remove_option("--data-peak-excl")
    parser.remove_option("--norm-peak-excl")
    parser.remove_option("--no-bkg")
    parser.remove_option("--no-norm-bkg")
    parser.remove_option("--mom-trans-bins")
    parser.remove_option("--tof-cuts")
    parser.remove_option("--no-filter")
    parser.remove_option("--store-dtot")
    parser.remove_option("--dump-specular")
    parser.remove_option("--dump-bkg")
    parser.remove_option("--dump-sub")
    parser.remove_option("--dump-rtof")
    parser.remove_option("--dump-rtof-comb")
    parser.remove_option("--dump-rq")
    parser.remove_option("--dump-rqr")

    # Setup REF specific options
    parser.add_option("", "--lambdap-bins", dest="lambdap_bins",
                      help="Specify the minimum and maximum lambda "\
                      +"perpendicular values and the lambda perpedicular "\
                      +"bin width in Angstroms.")

    parser.add_option("", "--mon-norm", action="store_true", dest="mon_norm",
                      help="Flag for using monitor normalization instead of "\
                      +"proton charge.")
    parser.set_defaults(mon_norm=False)

    parser.add_option("", "--mon-path", dest="mon_path",
                      help="Specify the comma separated list of monitor "\
                      +"path and signal.")
    parser.set_defaults(mon_path="/entry/monitor1,1")    

    parser.add_option("", "--omega", dest="omega", help="Override the value "\
                      +"of the angle for lambda perpendicular. The units on "\
                      +"the angle must be in radians.")

    parser.add_option("", "--dump-twod", action="store_true",
                      dest="dump_twod",
                      help="Flag to dump the R(pid,lambda_T) information. "\
                      +"Creates a *.plp file.")
    parser.set_defaults(dump_twod=False)

    parser.add_option("", "--timing", action="store_true", dest="timing",
                      help="Flag to turn on timing of code")
    parser.set_defaults(timing=False)

    (options, args) = parser.parse_args()

    # Set up the configuration
    configure = hlr_utils.Configure()

    # Call the configuration setter for RefOptions
    hlr_utils.RefConfiguration(parser, configure, options, args)

    # Set the lambda perpendicular (lambda_T)
    if hlr_utils.cli_provide_override(configure, "lambdap_bins",
                                      "--lambdap-bins"):
        configure.lambdap_bins = hlr_utils.AxisFromString(options.lambdap_bins)

    # Set mon_norm flag
    if hlr_utils.cli_provide_override(configure, "mon_norm", "--mon-norm"):
        configure.mon_norm = options.mon_norm

    # Set the monitor path
    if hlr_utils.cli_provide_override(configure, "mon_path", "--mon-path"):
        configure.mon_path = hlr_utils.NxPath(options.mon_path)

    # Set the override angle for calculating lambda_T
    if hlr_utils.cli_provide_override(configure, "omega", "--omega"):
        configure.omega = hlr_utils.DrParameterFromString(options.omega, True)

    # Set the ability to dump the R(pid, lambda_T) information
    if hlr_utils.cli_provide_override(configure, "dump_twod", "--dump-twod"):
        configure.dump_twod = options.dump_twod
        
    if hlr_utils.cli_provide_override(configure, "dump_all", "--dump-all"):
        if options.dump_all:
            configure.dump_twod = True

    # Setup the timing object
    if options.timing:
        import sns_timing
        timer = sns_timing.DiffTime()
    else:
        timer = None

    # Run the program
    run(configure, timer)
