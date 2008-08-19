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
                             Verbose=config.verbose)[0]

    if dst_type == "text/Spec":
        __plot_a3c(d_som, config)
    elif dst_type == "text/Dave2d":
        __plot_dave(d_som, config)
    elif dst_type == "text/num-info":
        __plot_numinfo(d_som)
    else:
        raise RuntimeError("Do not know how to plot file type %s" % dst_type)

    pylab.show()

def __plot_a3c(som, conf):
    """
    This subroutine is responsible for plotting a 3-column ASCII file.
    """
    len_som = len(som)

    info = som.toXY(withYvar=True)

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
                pylab.subplot(2,5,j+1)
            index = (i*10) + j

            if conf.logy:
                indicies = info[index][1].nonzero()
                y = info[index][1][indicies]
                var_y = info[index][2][indicies]
                x = info[index][0][indicies]
            else:
                y = info[index][1]
                var_y = info[index][2]
                x = info[index][0]

            if len_som > 1:
                pid = som[index].id
            else:
                pid = None
                
            __plot_one_a3c(x, y, numpy.sqrt(var_y),
                           som.getAllAxisLabels(), som.getAllAxisUnits(),
                           som.getYLabel(), som.getYUnits(),
                           pid, logy=conf.logy, logx=conf.logx)

def __plot_one_a3c(x, y, var_y, *args, **kwargs):
    """
    This subroutine is responsible for making a single 3-column ASCII dataset
    """
    try:
        logy = kwargs["logy"]
    except KeyError:
        logy = False

    try:
        logx = kwargs["logx"]
    except KeyError:
        logx = False        

    y = numpy.nan_to_num(y)
    var_y = numpy.nan_to_num(var_y)
    
    try:
        pylab.errorbar(x, y, var_y, fmt='o', mec='b', ls='None')
    except ValueError:
        # All data got filtered
        pass
    
    pylab.xlabel(args[0][0] + " [" + args[1][0] + "]")
    pylab.ylabel(args[2] + " [" + args[3] + "]")
    if args[4] is not None:
        pylab.title(args[4])
    else:
        pass

    if logy:
        ax = pylab.gca()
        ax.set_yscale("log")
    if logx:
        ax = pylab.gca()
        ax.set_xscale("log")

def __plot_dave(som, conf):
    """
    This subroutine is responsible for plotting a Dave 2D file.
    """
    info = som.toXY()

    Nx = len(info[0][0])
    Ny = len(info[0][1])
    
    # Y values are filtered since plotting has trouble with NaNs
    z = numpy.reshape(numpy.nan_to_num(info[0][2]), (Nx, Ny))

    import matplotlib.cm as cm
    import matplotlib

    if conf.logz:
        mylocator = matplotlib.ticker.LogLocator()
    else:
        mylocator = None

    pylab.contourf(info[0][1], info[0][0], z, cmap=cm.hot,
                   locator=mylocator)

    energy_units = som.getAxisUnits(1)
    if energy_units == "ueV":
        energy_units = "$\mu$eV"

    q_units = som.getAxisUnits(0)
    if q_units == "1/Angstroms":
        q_units = "1/$\AA$"
    
    pylab.xlabel(som.getAxisLabel(1) + " [" + energy_units + "]")
    pylab.ylabel(som.getAxisLabel(0) + " [" + q_units + "]")

    pylab.colorbar()

def __plot_numinfo(som):
    """
    This subroutine is responsible for plotting a NumInfo file.
    """
    info = som.toXY(withYvar=True)

    # Data is stored as floats and pixel IDs, so everything needs conversion
    x = numpy.arange(len(info))
    y = numpy.array([s[1] for s in info])
    ey = numpy.sqrt([s[2] for s in info])
    pid = numpy.array([str(s[0]) for s in info])

    pylab.errorbar(x, y, ey, fmt='o', mec='b', ls='None')
    pylab.xticks(x, pid, rotation='vertical')
    pylab.ylabel(som.getYLabel() + " [" + som.getYUnits() + "]")

if __name__ == "__main__":
    import hlr_utils

    import numpy
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

    # Run the program
    run(configure)
