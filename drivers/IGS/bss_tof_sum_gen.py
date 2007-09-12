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
This driver was a request from the B{BASIS} (aka B{BSS}) team and is not
formally documented.
"""

def run(config):
    """
    This method is where the data reduction process gets done.

    @param config: Object containing the data reduction configuration
                   information.
    @type config: L{hlr_utils.Configure}
    """
    import sys
    
    import dr_lib
    import DST
    import SOM

    banks = [("/entry/bank1", 1), ("/entry/bank2", 1)]

    max_ids = (64, 64)

    if config.vertical:
        tag = "v"
        size = max_ids[1]
        reps = max_ids[0] / config.pixel_group
        label = "Integrated pixel"
    else:
        tag = "h"
        size = max_ids[1] / config.pixel_group
        reps = max_ids[0] / config.sum_tubes
        label = "Tube Number"

    try:
        data_dst = DST.getInstance("application/x-NeXus",
                                   config.data)
    except SystemError:
        print "ERROR: Failed to data read file %s" % config.data
        sys.exit(-1)
        
    so_axis = "time_of_flight"

    for path in banks:
        bank = path[0].split('/')[-1]

        for i in range(size):

            tSOM = SOM.SOM()
            tSO = SOM.SO(construct=True)
            
            counter = 1
            for j in range(reps):

                if config.vertical:
                    starting_id = (i, config.pixel_group * j)
                    ending_id = (i + 1, config.pixel_group * (j + 1))
                else:
                    if config.sum_tubes == 1:
                        x1 = j
                        x2 = j + 1
                    else:
                        x1 = j * config.sum_tubes
                        x2 = (j + 1) * config.sum_tubes
                    
                    starting_id = (x1, config.pixel_group * i)
                    ending_id = (x2, config.pixel_group * (i + 1))

                d_som1 = data_dst.getSOM(path, so_axis,
                                         start_id=starting_id,
                                         end_id=ending_id)

                d_som2 = dr_lib.sum_all_spectra(d_som1)
                d_som2[0].id = d_som1[0].id

                d_som1 = None
                del d_som1

                value = dr_lib.integrate_axis(d_som2)

                if config.verbose:
                    print "Sum", d_som2[0].id, ":", value[0], value[1]

                tSO.axis[0].val.append(counter)
                tSO.y.append(value[0])
                tSO.var_y.append(value[1])
                if counter == 1:
                    tSO.id = d_som2[0].id

                counter += 1

            tSOM.attr_list["filename"] = config.data
            tSOM.setTitle("TOF Pixel Summation")
            tSOM.setDataSetType("density")
            tSOM.setYLabel("Intensity Sum")
            tSOM.setYUnits("counts")
            tSOM.setAxisLabel(0, label)
            tSOM.setAxisUnits(0, "")
            tSOM.append(tSO)

            tag1 = str(i + 1)
                    
            outfile = bank + "_" + tag + "_" + tag1 + ".tof"

            hlr_utils.write_file(outfile, "text/Spec", tSOM,
                                 verbose=config.verbose,
                                 message="intensity sum file",
                                 replace_ext=False)
                    
    data_dst.release_resource()


if __name__ == "__main__":
    import hlr_utils

    # set up the options available
    parser = hlr_utils.BasicOptions("usage: %prog [options] <datafile>", None,
                                    None, hlr_utils.program_version())

    parser.add_option("-u", "--vertical", action="store_true", dest="vertical",
                      help="Flag to slice and sum pixels in the vertical "\
                      +"direction")
    parser.set_defaults(vertical=False)
    
    parser.add_option("-a", "--horizontal", action="store_false",
                      dest="vertical",
                      help="Flag to slice and sum pixels in the horizontal "\
                      +"direction. (Default behavior)")
    
    parser.add_option("", "--pixel-group", dest="pixel_group", type="int",
                      metavar="INT",
                      help="Number of pixels in a grouping. The default "\
                      +"value is 4.")
    parser.set_defaults(pixel_group=4)

    parser.add_option("", "--sum-tubes", dest="sum_tubes", type="int",
                      metavar="INT",
                      help="Number of tubes to sum over. The default "\
                      +"value is 1.")
    parser.set_defaults(sum_tubes=1)

    (options, args) = parser.parse_args()

    # set up the configuration
    configure = hlr_utils.Configure()
    
    # get the datafile name and check it
    if len(args) == 1:
        configure.data = args[0]
        if not hlr_utils.file_exists(configure.data):
            parser.error("Data file [%s] does not exist" % configure.data)
    else:
        if options.data is not None:
            configure.data = hlr_utils.fix_filename(options.data)
            if not hlr_utils.file_exists(configure.data):
                parser.error("Data file [%s] does not exist" % configure.data)
        else:
            parser.error("Did not specify a datafile")

    # set the verbosity
    configure.verbose = options.verbose

    # set vertical
    configure.vertical = options.vertical

    # set pixel grouping
    configure.pixel_group = options.pixel_group

    # set sum tubes
    configure.sum_tubes = options.sum_tubes    
    if configure.sum_tubes <= 0:
        parser.error("sum-tubes must be greater than zero (default is 1)")
    else:
        pass
    
    run(configure)
