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
This program plots multiple 1D data files on the same graph.
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

    for datafile in config.data:
        d_som = dr_lib.add_files([datafile], dst_type=dst_type,
                                 Verbose=config.verbose)

        if dst_type == "text/Spec":
            drplot.plot_1D_so(d_som, d_som[0].id, logx=config.logx,
                              logy=config.logy, llabel=datafile)

            pylab.legend(numpoints=1, loc=config.legpos)
        elif dst_type == "text/Dave2d":
            drplot.plot_2D_so(d_som, logz=config.logz, nocb=True)
        else:
            raise RuntimeError("Cannot plot multiple files of this type %s" \
                               % dst_type)
        
    pylab.show()

if __name__ == "__main__":
    import drplot
    import hlr_utils

    import pylab

    # Make description for driver
    description = []
    description.append("This driver takes multiple 1D data files (3-column")
    description.append("ASCII) and plots them on the same graph. The file")
    description.append("names are used as the legend labels.")

    # Set up the options available
    parser = hlr_utils.BasicOptions("usage: %prog [options]", None, None,
                                    hlr_utils.program_version(), 'error',
                                    " ".join(description))

    parser.add_option("", "--logy", dest="logy", action="store_true",
                      help="Set the y-axis to logarithmic scale.")
    parser.set_defaults(logy=False)

    parser.add_option("", "--logx", dest="logx", action="store_true",
                      help="Set the x-axis to logarithmic scale.")
    parser.set_defaults(logx=False)

    parser.add_option("", "--logz", dest="logz", action="store_true",
                      help="Set the z-axis to logarithmic scale.")
    parser.set_defaults(logz=False)    

    parser.add_option("", "--legpos", dest="legpos", help="Set the location "\
                      +"of the legend on the graph. Default is 0 (best)")
    parser.set_defaults(legpos=0)

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

    # Set the logarithmic y-axis
    configure.logy = options.logy

    # Set the logarithmic x-axis
    configure.logx = options.logx

    # Set the logarithmic z-axis
    configure.logz = options.logz    

    # Set the legend position
    configure.legpos = options.legpos

    # Run the program
    run(configure)
