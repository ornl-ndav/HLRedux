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
    import DST

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
    
    # Perform Steps 1-2 on sample data
    d_som1 = dr_lib.process_reflp_data(config.data, config,
                                       None,
                                       timer=tim)

    # Perform Steps 1-3 on normalization data
    if config.norm is not None:
        n_som1 = dr_lib.process_reflp_data(config.norm, config,
                                           config.norm_roi_file,
                                           timer=tim)
    else:
        n_som1 = None

    # Step 4: Divide data by normalization
    if config.verbose and config.norm is not None:
        print "Scale data by normalization"

    if tim is not None:
        tim.getTime(False)

    if config.norm is not None:
        d_som2 = common_lib.div_ncerr(d_som1, n_som1, length_one_som=True)
    else:
        d_som2 = d_som1

    if tim is not None and config.norm is not None:
        tim.getTime(msg="After normalizing signal spectra")

    del d_som1, n_som1

    if config.dump_rtof_comb:
        d_som2_1 = dr_lib.sum_all_spectra(d_som2)
        d_som2_2 = dr_lib.data_filter(d_som2_1)
        del d_som2_1
        
        hlr_utils.write_file(config.output, "text/Spec", d_som2_2,
                             output_ext="crtof",
                             verbose=config.verbose,
                             data_ext=config.ext_replacement,
                             path_replacement=config.path_replacement,
                             message="combined R(TOF) information")

        del d_som2_2

    # Step 5: Convert TOF to Wavelength

    

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
    parser.remove_option("--norm-inst-geom")
    parser.remove_option("--no-bkg")
    parser.remove_option("--no-norm-bkg")
    parser.remove_option("--mom-trans-bins")
    parser.remove_option("--tof-cuts")
    parser.remove_option("--no-filter")
    parser.remove_option("--store-dtot")
    parser.remove_option("--dump-specular")
    parser.remove_option("--dump-bkg")
    parser.remove_option("--dump-sub")
    parser.remove_option("--dump-rtof-comb")
    parser.remove_option("--dump-rq")
    parser.remove_option("--dump-rqr")

    # Setup REF specific options
    parser.add_option("", "--timing", action="store_true", dest="timing",
                      help="Flag to turn on timing of code")
    parser.set_defaults(timing=False)

    (options, args) = parser.parse_args()

    # Set up the configuration
    configure = hlr_utils.Configure()

    # Call the configuration setter for RefOptions
    hlr_utils.RefConfiguration(parser, configure, options, args)

    # Setup the timing object
    if options.timing:
        import sns_timing
        timer = sns_timing.DiffTime()
    else:
        timer = None

    # Run the program
    run(configure, timer)
