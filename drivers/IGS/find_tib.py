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
This program covers the functionality outlined in B{Section 2.2.2 Determination
of Time-Indepdent Background} in
U{http://neutrons.ornl.gov/asg/projects/SCL/reqspec/DR_Lib_RS.doc}.
"""

def __bisect_range(range):
    """
    This function provides a convenient range bisection call

    @param range: Object containing a minimum and maximum value to bisect
    @type range: C{tuple}


    @return: The value of the bisection
    @rtype: C{float}
    """
    return (range[1] + range[0]) / 2.0

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

def __calculate_ratio(conf, ctib, t=None):
    """
    This function runs amorphous_reduction_sqe and calculates the ratio for the
    given time-independent background constant.

    @param conf: Object containing the data reduction configuration
                 information.
    @type conf: L{hlr_utils.Configure}

    @param ctib: Value of the time-independent background to run reduction with
    @type ctib: C{float}

    @param t: (OPTIONAL) Object that will allow the method to perform
                         timing evaluations.
    @type t: C{sns_time.DiffTime}

    @return: The values of the integration in the positive and negative
    sections respectively.
    @rtype: C{tuple}
    """
    import copy
    import amorphous_reduction_sqe
    import dr_lib

    amr_config = copy.deepcopy(conf)
    amr_config.verbose = conf.amr_verbose
    amr_config.tib_data_const = hlr_utils.DrParameter(ctib, 0.0)
    
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
        print "Ratio: %e / %e, %f" % (pos_int[0].y, neg_int[0].y,
                                      __make_ratio((pos_int[0].y,
                                                    neg_int[0].y)))

    return (pos_int[0].y, neg_int[0].y)

def __make_ratio(ratio):
    """
    This function takes two values and returns the division of them.

    @param ratio: The numerator and denominator of the ratio
    @type ratio: C{tuple}


    @return: The ratio
    @rtype: C{float}
    """
    return ratio[0] / ratio[1]

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
    # Steps 1-3
    ratio_min_parts = __calculate_ratio(config, config.ctib_min)
    ratio_min = __make_ratio(ratio_min_parts)

    # Step 4
    ratio_max_parts = __calculate_ratio(config, config.ctib_max)
    ratio_max = __make_ratio(ratio_max_parts)

    # Step 5
    if __check_parts(ratio_min_parts) and __check_parts(ratio_max_parts):
        if (config.ratio[0] < ratio_min or config.ratio[0] > ratio_max):
            raise RuntimeError("Ratios from minimum and maximum ctibs do not "\
                               +"bracket ratio. Increase the maximum ctib "
                               +"parameter. Min: %f, Max: %f, Given Ratio: %f"\
                               % (ratio_min, ratio_max, config.ratio[0]))
    elif __check_parts(ratio_min_parts) and not __check_parts(ratio_max_parts):
        if ratio_min > config.ratio[0]:
            raise RuntimeError("Ratio from minimum ctib is greater than "\
                               +"requested ratio. Decrease the minimum ctib "\
                               +"parameter. Min: %f, Given Ratio: %f" \
                               %(ratio_min, config.ratio[0]))
    elif not __check_parts(ratio_min_parts) and \
             not __check_parts(ratio_max_parts):
        raise RuntimeError("The components of both ratios are negative. "\
                           +"Decrease the value of the minimum ctib "\
                           +"parameter.")
    else:
        pass

    # Step 6
    tib_try = 0.0
    ratio_try = 0.0
    
    tib_range = [config.ctib_min, config.ctib_max]

    run_ok = False
        
    for i in range(config.niter):
        tib_try = __bisect_range(tib_range)
        if config.verbose:
            print "TIB Try: ", tib_try

        ratio_try_parts = __calculate_ratio(config, tib_try)
        ratio_try = __make_ratio(ratio_try_parts)

        # First, check to see if ratio is within tolerance
        if __check_range(ratio_try, config.ratio[0]-config.ratio[1],
                         config.ratio[0]+config.ratio[1]):
            if config.verbose:
                print "Final TIB: %f" % tib_try
            run_ok = True
            break

        # If not, check if the ratio parts
        if not __check_parts(ratio_try_parts):
            # It's not +/+, move range down
            tib_range[1] = tib_try
        else:
            # It's +/+, so look at ratio
            if ratio_try > config.ratio[0]:
                # Move range down
                tib_range[1] = tib_try
            else:
                # Move range up
                tib_range[0] = tib_try

    if not run_ok:
        # If you hit here, you've exhausted the number of iterations
        print "Maximum number of iterations exceeded! No suitable TIB found!"
        print "Best Value: %f, Ratio: %f" % (tib_try, ratio_try)
    
if __name__ == "__main__":
    import hlr_utils

    # Make description for driver
    result = []
    result.append("This driver searches for a time-independent background")
    result.append("that corresponds to a user requested ratio of energy")
    result.append("transfer ranges. The --energy-bins option should be used")
    result.append("to set the positive energy transfer region of integration.")
    result.append("The negative region will be constructed from this")
    result.append("information.")

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

    # Add find_tib related options
    parser.add_option("", "--ratio", dest="ratio",
                      help="Specify the value and tolerance (error) of the "\
                      +"target energy transfer integration ratio as comma "\
                      +"separated values")
    
    parser.add_option("", "--niter", dest="niter", type="int",
                      help="Specify the number of iterations to try. The "\
                      +"default is 20.")
    parser.set_defaults(niter=20)

    parser.add_option("", "--ctib-min", dest="ctib_min", type="float",
                      help="Specify the minimum value of the "\
                      +"time-independent background")
    
    parser.add_option("", "--ctib-max", dest="ctib_max", type="float",
                      help="Specify the maximum value of the "\
                      +"time-independent background")

    parser.add_option("", "--amr-verbose", action="store_true",
                      dest="amr_verbose", help="Flag to turn on the "\
                      +"verbosity of the amorphous_reduction_sqe code.")
    parser.set_defaults(amr_verbose=False)
    
    parser.add_option("", "--timing", action="store_true", dest="timing",
                      help="Flag to turn on timing of code")
    parser.set_defaults(timing=False)

    # Removing output flag
    parser.remove_option("-o")

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

    (options, args) = parser.parse_args()

    # Set up the configuration
    configure = hlr_utils.Configure()

    # Call the configuration setter for AmrOptions
    hlr_utils.AmrConfiguration(parser, configure, options, args)

    # Set the positive and negative energy transfer axis integration ranges
    efacts = options.E_bins.split(',')
    configure.et_pos_range = (float(efacts[0]), float(efacts[1]))
    configure.et_neg_range = (-1.0*float(efacts[1]), -1.0*float(efacts[0]))

    # Reset energy transfer axis to [-E_t_max, E_t_max]
    configure.E_bins = hlr_utils.Axis(-1.0*float(efacts[1]),
                                      float(efacts[1]),
                                      float(efacts[2]))

    # Reset Q axis to one big bin
    qfacts = options.Q_bins.split(',')
    configure.Q_bins = hlr_utils.Axis(float(qfacts[0]),
                                      float(qfacts[1]),
                                      float(qfacts[1])-float(qfacts[0]))

    # Set the integration ratio and its tolerance
    if options.ratio:
        configure.ratio = hlr_utils.split_values(options.ratio)
    else:
       parser.error("An integration ratio must be supplied") 

    # Set the number of iterations
    configure.niter = options.niter

    # Set the minimum time-independent background constant
    configure.ctib_min = options.ctib_min

    # Set the maximum time-independent background constant
    configure.ctib_max = options.ctib_max

    # Set the verbosity for the amorphous_reduction_sqe code
    configure.amr_verbose = options.amr_verbose

    # Set timer object if timing option is used
    if options.timing:
        import sns_timing
        timer = sns_timing.DiffTime()
    else:
        timer = None

    run(configure, timer)
