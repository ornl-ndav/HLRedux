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


    @return: A mapping of the banks to offsets for the 2D grid and an offset
             for the lowset bank.
    @rtype: C{tuple} of (C{dict}, C{int})
    """
    bmap = {}

    # Files are of the format: <inst>_bankXXX-YYY.norm
    for dfile in dfilelist:
        parts = dfile.split('_')[-1].split('-')
        min_bank = int(parts[0].split('bank')[-1])
        max_bank = int(parts[-1].split('.')[0])

        for i in range(min_bank, max_bank+1):
            bmap["bank%d" % i] = i - 1

    # If lowest bank is not zero, we need to adjust the indicies
    minval = min(bmap.values())
    if minval > 0:
        for key in bmap:
            bmap[key] -= minval

    return (bmap, minval)

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

    (bank_map, offset) = make_bank_map(config.data)
    num_banks = len(bank_map)
    len_x = config.num_tubes * num_banks
    len_data = config.num_pixels * len_x

    grid = nessi_list.NessiList(len_data)
    run_number = -1
    instrument = ""
    
    for datafile in config.data:
        instrument = datafile.split('_')[0]
        
        d_som = dr_lib.add_files([datafile], dst_type=dst_type,
                                 Verbose=config.verbose)

        run_number = d_som.attr_list["normalization-run_number"]

        for so in d_som:
            bank_offset = bank_map[so.id[0]]
            # index = y + Ny * (x + b * Nx)
            index = so.id[1][1] + config.num_pixels * (so.id[1][0] +
                                                       bank_offset *
                                                       config.num_tubes)
            grid[index] = so.y
            
        del d_som

    # if run number is a list, it's separated by /
    run_number = run_number.split('/')[0]
        
    z = numpy.reshape(grid.toNumPy(), (len_x, config.num_pixels))
    x = numpy.arange(len_x)
    y = numpy.arange(config.num_pixels)

    title = "%s %s" % (instrument, run_number)

    import matplotlib.cm as mcm
    if config.cmb:
        colormap = mcm.Blues
    else:
        colormap = mcm.hot

    figure = pylab.figure()
    figure.subplots_adjust(left=0.085, right=0.95)
    
    drplot.plot_2D_arr(x, y, numpy.transpose(z), ylabel="Pixel Number",
                       xlabel="Bank Number", title=title,
                       logz=config.logz, colormap=colormap, nocb=True)

    # Set grid lines to dilineate the banks
    tl = [str(i+1) for i in range(offset, offset+num_banks+1)]
    drplot.grid_setter(locator=num_banks, ticklabels=tl, rotation='vertical')

    if config.pixel_grid:
        # Set some grid lines for the pixels
        drplot.grid_setter(axis="y", linestyle="-.")

    pylab.colorbar(orientation="horizontal", fraction=0.05,
                   format=config.format)
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

    parser.add_option("", "--cmb", dest="cmb", action="store_true",
                      help="Use the Blues colormap")
    parser.set_defaults(cmb=False)

    parser.add_option("", "--pixel-grid", dest="pixel_grid",
                      action="store_true", help="Add some grid lines for "\
                      +"the pixels.")
    parser.set_defaults(pixel_grid=False)

    parser.add_option("", "--format", dest="format", help="Specify a text "\
                      +"format for the colorbar values. The default is %.2f")
    parser.set_defaults(format="%.2f")

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

    # Set the colormap to Blues
    configure.cmb = options.cmb

    # Set the flag for pixel grid lines
    configure.pixel_grid = options.pixel_grid    

    # Set the colorbar value formatting string
    configure.format = options.format

    # Run the program
    run(configure)
