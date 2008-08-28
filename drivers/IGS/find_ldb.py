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
This program covers the functionality outlined in B{Section 2.2.3 Determination
of Wavelength-Dependent Background} in
U{http://neutrons.ornl.gov/asg/projects/SCL/reqspec/DR_Lib_RS.doc}.
"""

def __bisect_range(trange):
    """
    This function provides a convenient range bisection call

    @param trange: Object containing a minimum and maximum value to bisect
    @type trange: C{tuple}


    @return: The value of the bisection
    @rtype: C{float}
    """
    return (trange[1] + trange[0]) / 2.0

def __check_parts(parts):
    """
    This function takes two values that are part of a ratio and checks the
    sign of both parts. 

    @param parts: Two parts of a ratio that will be checked for sign
    @type parts: C{tuple}


    @return: Returns I{True} for (+,+) and I{False} for (+,-), (-,+) and (-,-).
    @rtype: C{boolean}
    """
    if parts[0] > 0 and parts[1] > 0:
        return True
    else:
        return False

def __check_range(value, low_end, high_end):
    """
    This function checks to see if a value is within a requested range given
    by C{[low_end, high_end]}.

    @param value: Value to check within a requested range
    @type value: C{float}

    @param low_end: The minimum value of the requested range
    @type low_end: C{float}

    @param high_end: The maximum value of the requested range
    @type high_end: C{float}


    @return: I{True} if the value is within the requested range and I{False}
             if the value is not.
    @rtype: C{boolean}
    """
    return value >= low_end and value <= high_end

def __calculate_ratio(conf, cwdb, t=None):
    """
    This function runs amorphous_reduction_sqe and calculates the ratio for the
    given time-independent background constant.

    @param conf: Object containing the data reduction configuration
                 information.
    @type conf: L{hlr_utils.Configure}

    @param cwdb: Value of the wavelength-dependent background to run reduction
                 with.
    @type cwdb: C{float}

    @param t: (OPTIONAL) Object that will allow the method to perform
                         timing evaluations.
    @type t: C{sns_time.DiffTime}


    @return: The values of the integration in the positive and negative
             sections respectively.
    @rtype: C{tuple}
    """
    import copy

    import dr_lib

    amr_config = copy.deepcopy(conf)
    amr_config.verbose = conf.amr_verbose
    amr_config.ldb_const = hlr_utils.DrParameter(cwdb, 0.0)
    
    if t is not None:
        t.getTime(False)

    if conf.verbose:
        print "Running amorphous_reduction_sqe"

    som = amorphous_reduction_sqe.run(amr_config)

    if t is not None:
        t.getTime(msg="After running amorphous_reduction_sqe ")

    pos_int = dr_lib.integrate_spectra(som, start=conf.et_pos_range[0],
                                       end=conf.et_pos_range[1], axis_pos=1)

    neg_int = dr_lib.integrate_spectra(som, start=conf.et_neg_range[0],
                                       end=conf.et_neg_range[1], axis_pos=1) 

    if conf.verbose:
        try:
            print "Ratio: %e / %e, %f" % (pos_int[0].y, neg_int[0].y,
                                          __make_ratio((pos_int[0].y,
                                                        neg_int[0].y)))
        except ZeroDivisionError:
            print "Ratio: %e / %e, inf" % (pos_int[0].y, neg_int[0].y)

    return (pos_int[0].y, neg_int[0].y)

def __make_ratio(ratio):
    """
    This function takes two values and returns the division of them.

    @param ratio: The numerator and denominator of the ratio
    @type ratio: C{tuple}


    @return: The ratio
    @rtype: C{float}
    """
    try: 
        return ratio[0] / ratio[1]
    except ZeroDivisionError:
        return float("inf")

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

    if config.verbose:
        print "Ratio:", config.ratio
    
    # Steps 1-3
    ratio_min_parts = __calculate_ratio(config, config.cwdb_min)
    ratio_min = __make_ratio(ratio_min_parts)

    if tim is not None:
        tim.getTime(msg="After minimum ratio calculation ")

    # Step 4
    ratio_max_parts = __calculate_ratio(config, config.cwdb_max)
    ratio_max = __make_ratio(ratio_max_parts)

    if tim is not None:
        tim.getTime(msg="After maximum ratio calculation ")

    old_niter = -1

    # Step 5
    if __check_parts(ratio_min_parts) and __check_parts(ratio_max_parts):
        if (config.ratio < ratio_min or config.ratio > ratio_max):
            print "Ratios from minimum and maximum cwdbs do not "\
                  +"bracket ratio. Increase the maximum cwdb "\
                  +"parameter. Min: %f, Max: %f, Given Ratio: %f"\
                  % (ratio_min, ratio_max, config.ratio)
            old_niter = config.niter
            config.niter = 0
    elif __check_parts(ratio_min_parts) and not __check_parts(ratio_max_parts):
        if ratio_min > config.ratio:
            print "Ratio from minimum cwdb is greater than "\
                      +"requested ratio. Decrease the minimum cwdb "\
                      +"parameter. Min: %f, Given Ratio: %f" \
                      %(ratio_min, config.ratio)
            old_niter = config.niter
            config.niter = 0
    elif not __check_parts(ratio_min_parts) and \
             not __check_parts(ratio_max_parts):
        print "The components of both ratios are negative. "\
              +"Decrease the value of the minimum cwdb parameter."
        old_niter = config.niter
        config.niter = 0
    else:
        pass

    # Steps 6-7
    wdb_try = 0.0
    ratio_try = 0.0
    
    wdb_range = [config.cwdb_min, config.cwdb_max]

    run_ok = False

    counter = 0
    while counter < config.niter:
        if config.verbose:
            print "Range:", wdb_range
        wdb_try = __bisect_range(wdb_range)
        if config.verbose:
            print "WDB Try: ", wdb_try

        ratio_try_parts = __calculate_ratio(config, wdb_try)
        ratio_try = __make_ratio(ratio_try_parts)

        if tim is not None:
            tim.getTime(msg="After ratio calculation ")

        # First, check to see if ratio is within tolerance
        if __check_range(ratio_try, config.ratio-config.tol,
                         config.ratio+config.tol):
            run_ok = True
            break

        # If not, check if the ratio parts
        if not __check_parts(ratio_try_parts):
            # It's not +/+, move range down
            wdb_range[1] = wdb_try
        else:
            # It's +/+, so look at ratio
            if ratio_try > config.ratio:
                # Move range down
                wdb_range[1] = wdb_try
            else:
                # Move range up
                wdb_range[0] = wdb_try

        counter += 1

    if not run_ok and counter != 0:
        # If you hit here, you've exhausted the number of iterations, so
        # subtract nothing
        print "Maximum number of iterations (%d) reached! No suitable WDB "\
              +"found!" % counter
        wdb_try = 0.0

    if run_ok:
        print "Best Value: %e, Ratio: %f, NIter: %d" % (wdb_try, ratio_try,
                                                        counter)

    # Step 8
    # Set the create_output flag to True to get the output file from this run
    config.create_output = True
    config.verbose = config.amr_verbose
    config.E_bins = config.final_E_bins
    config.ldb_const = hlr_utils.DrParameter(wdb_try, 0.0)

    # Remove unneeded options so they don't get into RMD file
    del config.final_E_bins
    del config.et_neg_range
    del config.et_pos_range
    del config.ratio

    # Reset the iteration option to make sure info goes into RMD file
    if old_niter != -1:
        config.niter = old_niter
    
    amorphous_reduction_sqe.run(config)

    if tim is not None:
        tim.setOldTime(old_time)
        tim.getTime(msg="Total Running Time")
    
if __name__ == "__main__":
    import amorphous_reduction_sqe
    import hlr_utils

    # Make description for driver
    result = []
    result.append("This driver searches for a wavelength-dependent background")
    result.append("that corresponds to a desired ratio based on temperature")
    result.append("an the energy transfer range. The --et-int-range option")
    result.append("should be used to set the positive energy transfer region")
    result.append("of integration. The negative region will be constructed")
    result.append("from this information.")

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

    # Add find_ldb related options
    parser.add_option("", "--et-int-range", dest="et_int_range", help="Set "\
                      +"the minimum and maximum values of the energy tranfer "\
                      +"integration range. Also, set the bin width for "\
                      +"energy transfer that will be used during the "\
                      +"calculation.")
    
    parser.add_option("", "--detbal-temp", dest="detbal_temp", help="Specify "\
                      +"the experiment temperature that will help calculate "\
                      +"the desired ratio.")
    
    parser.add_option("", "--tol", dest="tol",
                      help="Specify the tolerance of the target energy "\
                      +"transfer integration ratio")
    
    parser.add_option("", "--niter", dest="niter", type="int",
                      help="Specify the number of iterations to try. The "\
                      +"default is 20.")
    parser.set_defaults(niter=20)

    parser.add_option("", "--cwdb-min", dest="cwdb_min", type="float",
                      help="Specify the minimum value of the "\
                      +"wavelength-dependent background")
    parser.set_defaults(cwdb_min=0.0)
    
    parser.add_option("", "--cwdb-max", dest="cwdb_max", type="float",
                      help="Specify the maximum value of the "\
                      +"wavelength-dependent background")

    parser.add_option("", "--amr-verbose", action="store_true",
                      dest="amr_verbose", help="Flag to turn on the "\
                      +"verbosity of the amorphous_reduction_sqe code.")
    parser.set_defaults(amr_verbose=False)
    
    parser.add_option("", "--timing", action="store_true", dest="timing",
                      help="Flag to turn on timing of code")
    parser.set_defaults(timing=False)

    # Removing all file writing flags
    parser.remove_option("--dump-all")
    parser.remove_option("--dump-tib")
    parser.remove_option("--dump-wave")
    parser.remove_option("--dump-mon-wave")
    parser.remove_option("--dump-mon-rebin")
    parser.remove_option("--dump-mon-effc")
    parser.remove_option("--dump-wave-mnorm")
    parser.remove_option("--dump-energy")
    parser.remove_option("--dump-ei")
    parser.remove_option("--dump-dslin")

    # Remove some other unneeded options
    parser.remove_option("--split")
    parser.remove_option("--lambda-bins")
    # This one is handled by the loop
    parser.remove_option("--ldb-const")
    # Block the rescaling as this causes havoc with the looping
    parser.remove_option("--rescale-final")

    (options, args) = parser.parse_args()

    # Set up the configuration
    configure = hlr_utils.Configure()

    # Call the configuration setter for AmrOptions
    hlr_utils.AmrConfiguration(parser, configure, options, args)

    # Set the positive and negative energy transfer axis integration ranges
    efacts = options.et_int_range.split(',')
    configure.et_pos_range = (float(efacts[0]), float(efacts[1]))
    configure.et_neg_range = (-1.0*float(efacts[1]), -1.0*float(efacts[0]))

    # Capture final energy binning
    configure.final_E_bins = configure.E_bins

    # Reset energy transfer axis to [-E_t_max, E_t_max]
    configure.E_bins = hlr_utils.Axis(-1.0*float(efacts[1]),
                                      float(efacts[1]),
                                      float(efacts[2]))

    # Reset Q axis to one big bin
    qfacts = options.Q_bins.split(',')
    configure.Q_bins = hlr_utils.Axis(float(qfacts[0]),
                                      float(qfacts[1]),
                                      float(qfacts[1])-float(qfacts[0]))

    # Set the tolerance for the desired ratio
    if options.tol:
        configure.tol = float(options.tol)
    else:
        parser.error("A tolerance must be supplied") 

    # Set the experiment (detailed balance) temperature
    if options.detbal_temp:
        configure.detbal_temp = float(options.detbal_temp)
    else:
        parser.error("An experiment temperature must be supplied")         

    # Set the number of iterations
    configure.niter = options.niter

    # Set the minimum wavelength-dependent background constant
    configure.cwdb_min = options.cwdb_min

    # Set the maximum wavelength-dependent background constant
    configure.cwdb_max = options.cwdb_max

    # Set the verbosity for the amorphous_reduction_sqe code
    configure.amr_verbose = options.amr_verbose

    # Set a flag for creating output, but the default is currently False
    configure.create_output = False

    # Set timer object if timing option is used
    if options.timing:
        import sns_timing
        timer = sns_timing.DiffTime()
    else:
        timer = None

    # Take out options that have defaults but aren't necessary
    del configure.lambda_bins

    # Step 0: Calculate desired ratio
    import math
    configure.ratio = math.exp(0.5 * (float(efacts[0]) + float(efacts[1])) /
                               (configure.detbal_temp * 86.17343))
    

    run(configure, timer)
