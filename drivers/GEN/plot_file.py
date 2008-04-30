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
    import numpy
    import pylab
    
    import dr_lib

    if config.data is None:
        raise RuntimeError("Need to pass a data filename(s) to the driver "\
                           +"script.")

    dst_type = hlr_utils.file_peeker(config.data[0])

    if config.verbose:
        print "Initial file type (data set):", dst_type

    d_som = dr_lib.add_files(config.data, dst_type=dst_type,
                             Verbose=config.verbose)[0]

    if dst_type == "text/Spec":
        __plot_a3c(d_som, config)
    elif dst_type == "text/Dave2d":
        __plot_dave(d_som, config)
    elif dst_type == "text/num-info":
        __plot_numinfo(d_som, config)
    else:
        raise RuntimeError("Do not know how to plot file type %s" % dst_type)

    pylab.show()

def __plot_a3c(som, conf):
    """
    This subroutine is responsible for plotting a 3-column ASCII file.
    """
    pass

def __plot_dave(som, conf):
    """
    This subroutine is responsible for plotting a Dave 2D file.
    """
    info = som.toXY()

    Nx = len(info[0])
    Ny = len(info[1])
    
    #yn = numpy.nan_to_num(info[2])
    z = numpy.reshape(info[2], (Nx, Ny))

    import matplotlib.cm as cm

    pylab.contourf(info[1], info[0], z, cmap=cm.hot)
    pylab.xlabel(som.getAxisLabel(1))
    pylab.ylabel(som.getAxisLabel(0))

    pylab.colorbar()

def __plot_numinfo(som, conf):
    """
    This subroutine is responsible for plotting a NumInfo file.
    """
    pass

if __name__ == "__main__":
    import hlr_utils

    # Make description for driver
    description = []
    description.append("")

    # Set up the options available
    parser = hlr_utils.BasicOptions("usage: %prog [options]", None, None,
                                    hlr_utils.program_version(), 'error',
                                    " ".join(description))
    
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

    # Run the program
    run(configure)
