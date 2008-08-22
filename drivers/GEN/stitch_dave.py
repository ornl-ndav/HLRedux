#!/usr/bin/env python

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
This driver stitches DAVE 2D ASCII files that contain one bin on the slowest
running axis.
"""

def run(config):
    """
    This method is where the processing is done.

    @param config: Object containing the driver configuration information.
    @type config: L{hlr_utils.Configure}
    """
    if config.data is None:
        raise RuntimeError("Need to pass a data filename to the driver "\
                           +"script.")

    dst_type = hlr_utils.file_peeker(config.data[0])
    if dst_type != "text/Dave2D":
        raise TypeError("Only Dave2D ASCII files can be handled. Do not "\
                        +"know how to handle %s." % dst_type)

    
if __name__ == "__main__":
    import dr_lib
    import hlr_utils

    # Make description for driver
    result = []
    result.append("This driver reads in DAVE 2D ASCII files containing one")
    result.append("bin in the slowest running axis, combines them into a")
    result.append("new inclusive spectrum and writes that out to file.")

    # set up the options available
    parser = hlr_utils.BasicOptions("usage: %prog [options] <datafile>", None,
                                    None, hlr_utils.program_version(), 'error',
                                    " ".join(result))

    # Specify the rescaling constant
    parser.add_option("-r", "--rescale", dest="rescale", help="Specify a "\
                      +"constant with which to rescale the final data.")

    # Remove unneeded options
    parser.remove_option("--inst")
    parser.remove_option("--facility")

    (options, args) = parser.parse_args()

    # set up the configuration
    configure = hlr_utils.Configure()

    # Call the configuration setter for BasicOptions
    hlr_utils.BasicConfiguration(parser, configure, options, args)

    # Set the rescaling constant
    try:
        configure.rescale = float(options.rescale)
    except TypeError:
        configure.rescale = options.rescale

    # run the program
    run(configure)
