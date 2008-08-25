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
    if dst_type != "text/Dave2d":
        raise TypeError("Only Dave2D ASCII files can be handled. Do not "\
                        +"know how to handle %s." % dst_type)

    spectra = []

    # Read in all data files
    for datafile in config.data:
        spectra.append(dr_lib.add_files([datafile], dst_type=dst_type,
                                        Verbose=config.verbose)[0])

    # Sort spectra on slowest axis (Q for BSS files)
    spectra.sort(lambda x, y: cmp(x[0].axis[0].val[0], y[0].axis[0].val[0]))

    # Create placeholder for combined spectrum
    Ny = len(spectra)
    Nx = len(spectra[0][0].axis[1].val)

    import nessi_list
    import SOM

    result = SOM.SOM()
    result = hlr_utils.copy_som_attr(result, "SOM", spectra[0], "SOM")
    
    so = SOM.SO(2)
    so.id = 0
    so.y = nessi_list.NessiList(Nx * Ny)
    so.var_y = nessi_list.NessiList(Nx * Ny)
    so.axis[1].val = spectra[0][0].axis[1].val

    # Make the slowest axis
    slow_axis = [x[0].axis[0].val[0] for x in spectra]
    so.axis[0].val = nessi_list.NessiList()
    so.axis[0].val.extend(slow_axis)

    # Create combined spectrum
    import array_manip
    
    for i in xrange(Ny):
        value = hlr_utils.get_value(spectra[i], 0, "SOM", "y")
        err2 = hlr_utils.get_err2(spectra[i], 0, "SOM", "y")
        
        start = i * Nx

        (so.y, so.var_y) = array_manip.add_ncerr(so.y, so.var_y, value, err2,
                                                a_start=start)

    result.append(so)
    
    hlr_utils.write_file(config.output, dst_type, result,
                         verbose=config.verbose,
                         replace_ext=False,
                         path_replacement=config.path_replacement,
                         axis_ok=True,
                         message="combined file")

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
