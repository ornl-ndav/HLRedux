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
This programs plots data files handled or produced by data reduction. 
"""

def run(config):
    """
    This method is where the data reduction process gets done.

    @param config: Object containing the data reduction configuration
                   information.
    @type config: L{hlr_utils.Configure}
    """
    import dr_lib

    if config.data is None:
        raise RuntimeError("Need to pass a data filename(s) to the driver "\
                           +"script.")

    dst_type = hlr_utils.file_peeker(config.data[0])

    if config.verbose:
        print "Initial file type (data set):", dst_type

    d_som = dr_lib.add_files(config.data, dst_type=dst_type,
                             Signal_ROI=config.roi_file,
                             Verbose=config.verbose)

    if dst_type == "text/Spec":
        __plot_a3c(d_som, config)
    elif dst_type == "text/Dave2d":
        if config.projx:
            drplot.plot_1D_slice(d_som, "y", config.range, (None, None),
                                 logx=config.logx, logy=config.logy,
                                 line=config.line)
        elif config.projy:
            drplot.plot_1D_slice(d_som, "x", (None, None), config.range,
                                 logx=config.logx, logy=config.logy,
                                 line=config.line)
        elif config.slicex:
            drplot.plot_1D_slices(d_som, "y", config.range, clip=config.clip,
                                  logx=config.logx, logy=config.logy,
                                  line=config.line)
        elif config.slicey:
            drplot.plot_1D_slices(d_som, "x", config.range, clip=config.clip,
                                  logx=config.logx, logy=config.logy,
                                  line=config.line)
        else:
            drplot.plot_2D_so(d_som, logz=config.logz)
    elif dst_type == "text/num-info":
        drplot.plot_numinfo(d_som)
    else:
        raise RuntimeError("Do not know how to plot file type %s" % dst_type)

    pylab.show()

def __plot_a3c(som, conf):
    """
    This subroutine is responsible for plotting a 3-column ASCII file.
    """
    len_som = len(som)

    if len_som > 1:
        # Get the number of figures needed
        num_figs = len_som / 10 + 1
        # Get left over plots if length isn't evenly divisible
        left_over = len_som % 10
    else:
        num_figs = 1
        left_over = 1

    for i in xrange(num_figs):
        if len_som > 1:
            pylab.figure(i+1)
        if i+1 == num_figs:
            extent = left_over
        else:
            extent = 10

        for j in xrange(extent):
            if len_som > 1:
                pylab.subplot(2, 5, j+1)
            index = (i*10) + j

            pid = som[index].id

            try:
                drplot.plot_1D_so(som, pid, title=pid, logy=conf.logy,
                                  logx=conf.logx, line=conf.line)
            except ValueError:
                # All data got filtered
                pass

if __name__ == "__main__":
    import drplot
    import hlr_utils

    import pylab
   
    # Make description for driver
    description = []
    description.append("")

    # Set up the options available
    parser = hlr_utils.BasicOptions("usage: %prog [options]", None, None,
                                    hlr_utils.program_version(), 'error',
                                    " ".join(description))

    parser.add_option("", "--roi-file", dest="roi_file",
                      help="Specify a file that contains a list of pixel "\
                      +"ids to be read from the data")

    parser.add_option("", "--logy", dest="logy", action="store_true",
                      help="Set the y-axis to logarithmic scale.")
    parser.set_defaults(logy=False)

    parser.add_option("", "--logx", dest="logx", action="store_true",
                      help="Set the x-axis to logarithmic scale.")
    parser.set_defaults(logx=False)

    parser.add_option("", "--logz", dest="logz", action="store_true",
                      help="Set the z-axis to logarithmic scale.")
    parser.set_defaults(logz=False)        

    parser.add_option("", "--projx", dest="projx", action="store_true",
                      help="Project a 2D distribution along x.")
    parser.set_defaults(projx=False)

    parser.add_option("", "--projy", dest="projy", action="store_true",
                      help="Project a 2D distribution along y.")
    parser.set_defaults(projy=False)    

    parser.add_option("", "--range", dest="range", type="float", nargs=2,
                      help="Set the range to filter on the opposite "\
                      +"axis when projecting or slicing a 2D distribution.")

    parser.add_option("", "--clip", dest="clip", type="float", nargs=2,
                      help="Set the range to clip the axis for the "\
                      +"projection or slice. Please specify both minimum "\
                      +"and maximum values.")

    parser.add_option("", "--slicex", dest="slicex", action="store_true",
                      help="Show x distributions for each y from a 2D "\
                      +"distribution.")
    parser.set_defaults(slicex=False)

    parser.add_option("", "--slicey", dest="slicey", action="store_true",
                      help="Show y distributions for each x from a 2D "\
                      +"distribution.")
    parser.set_defaults(slicey=False)

    parser.add_option("-l", "--line", dest="line", action="store_true",
                      help="Draw a line connecting points for 1D plots.")

    # Do not need to use the following options
    parser.remove_option("--config")
    parser.remove_option("--data")
    parser.remove_option("--output")

    (options, args) = parser.parse_args()

    # set up the configuration
    configure = hlr_utils.Configure()

    # Need to set the inst parameter to None to spoof data file finder
    configure.inst = None

    # Need to set the facility parameter to None to spoof data file finder
    configure.facility = None

    # Temporarily silence verbosity
    old_verbosity = options.verbose
    options.verbose = False

    # Call the configuration setter for SNSOptions
    hlr_utils.BasicConfiguration(parser, configure, options, args)

    # Reset verbosity
    configure.verbose = old_verbosity

    # Set the ROI file
    configure.roi_file = hlr_utils.determine_files(options.roi_file,
                                                   one_file=True)

    # Set the logarithmic y-axis
    configure.logy = options.logy

    # Set the logarithmic x-axis
    configure.logx = options.logx

    # Set the logarithmic z-axis
    configure.logz = options.logz    

    # Set the flag to project to the x-axis
    configure.projx = options.projx

    # Set the flag to project to the y-axis
    configure.projy = options.projy

    # Set the range for filtering the opposite axis for the chosen projection
    # or slicing scheme
    if options.range is None:
        configure.range = (None, None)
    else:
        configure.range = options.range

    # Set the clipping range for the chosen projection or slicing scheme
    if options.clip is None:
        configure.clip = (None, None)
    else:
        configure.clip = options.clip            

    # Set the flag to make slices along the y-axis
    configure.slicex = options.slicex

    # Set the flag to make slices along the x-axis
    configure.slicey = options.slicey

    # Set the flag for a connecting line in 1D plots
    configure.line = options.line

    # Run the program
    run(configure)
