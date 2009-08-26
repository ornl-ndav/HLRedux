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
This program plots text/num-info files that are produced from normalization
reduction processes. 
"""
def make_bank_map(dfilelist):
    """
    This method inspects the names of the normalization files looking for the
    bank numbers. A map is then created from the bank ranges. This will allow
    for gaps in the coverage.

    @param dfilelist: The list of data files to be processed.
    @type dfilelist: C{list}


    @return: A mapping of the banks to offsets for the 2D grid.
    @rtype: C{dict}
    """
    bmap = {}

    # Files are of the format: <inst>_bankXXX-YYY.norm
    for dfile in dfilelist:
        parts = dfile.split('_')[-1].split('-')
        min_bank = int(parts[0].split('bank')[-1])
        max_bank = int(parts[-1].split('.')[0])

        for i in range(min_bank, max_bank+1):
            bmap["bank%d" % i] = i - 1

    return bmap

def run(config):
    """
    This method is where the plot processing gets done.

    @param config: Object containing the configuration information.
    @type config: L{hlr_utils.Configure}
    """
    import dr_lib
    import nessi_list
    import numpy

    if config.data is None:
        raise RuntimeError("Need to pass a data filename(s) to the driver "\
                           +"script.")

    dst_type = hlr_utils.file_peeker(config.data[0])

    if dst_type != "text/num-info":
        raise RuntimeError("Cannot handle DST type: %s" % dst_type)

    bank_map = make_bank_map(config.data)
    num_banks = len(bank_map)
    len_x = config.num_tubes * num_banks
    len_data = config.num_pixels * len_x

    grid = nessi_list.NessiList(len_data)
    
    for datafile in config.data:
        d_som = dr_lib.add_files([datafile], dst_type=dst_type,
                                 Verbose=config.verbose)

        for so in d_som:
            bank_offset = bank_map[so.id[0]]
            # index = y + Ny * (x + b * Nx)
            index = so.id[1][1] + config.num_pixels * (so.id[1][0] +
                                                       bank_offset *
                                                       config.num_tubes)
            grid[index] = so.y
            
        del d_som
        
    z = numpy.reshape(grid.toNumPy(), (config.num_pixels, len_x))
    y = numpy.arange(len_x)
    x = numpy.arange(config.num_pixels)
    
    drplot.plot_2D_arr(y, x, z)
    pylab.show()

if __name__ == "__main__":
    import drplot
    import hlr_utils

    import pylab

    # Make description for driver
    description = []
    description.append("This driver takes *.norm files from dgs_norm and")
    description.append("plots them as a two dimensional grid. If there are")
    description.append("gaps in the banks, they will be ignored.")

    # Set up the options available
    parser = hlr_utils.BasicOptions("usage: %prog [options]", None, None,
                                    hlr_utils.program_version(), 'error',
                                    " ".join(description))

    parser.add_option("-x", "--num-tubes", dest="num_tubes", type=int,
                      help="Specify the number of tubes in a detector bank." \
                      +"The default is 8.")
    parser.set_defaults(num_tubes=8)

    parser.add_option("-y", "--num-pixels", dest="num_pixels", type=int,
                      help="Specify the number of pixels in a detector tube." \
                      +"The default is 128.")
    parser.set_defaults(num_pixels=128)

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

    # Set the number of tubes in a detector bank
    configure.num_tubes = options.num_tubes

    # Set the number of pixels in a detector tube
    configure.num_pixels = options.num_pixels    

    # Set the logarithmic z-axis
    configure.logz = options.logz    

    # Run the program
    run(configure)
