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
    runner = "tof_slicer"
    mfilter = "mask_generator"
    banks = [("/entry/bank1", 1), ("/entry/bank2", 1)]

    max_ids = (64, 64)

    if config.vertical:
        tag = "v"
        size = max_ids[1]
        reps = max_ids[0] / config.pixel_group
    else:
        tag = "h"
        size = max_ids[0]
        reps = max_ids[1] / config.pixel_group

    for path in banks:
        bank = path[0].split('/')[-1]

        if bank.endswith("1") and config.sum_tubes_bank1 is not None:
            tubes = config.sum_tubes_bank1
        elif bank.endswith("2") and config.sum_tubes_bank2 is not None:
            tubes = config.sum_tubes_bank2
        else:
            tubes = None

        if tubes is None:
            for i in range(size):
                for j in range(reps):
                    
                    start_id = (i, config.pixel_group * j)
                    end_id = (i + 1, config.pixel_group * (j + 1))
                    
                    if config.vertical:
                        tag1 = str(i + 1)
                        tag2 = str(j + 1)
                    else:
                        tag1 = str(j + 1)
                        tag2 = str(i + 1)
                        
                    oufile = bank + "_" + tag + "_" + tag1 + "_" \
                                 + tag2 + ".tof"
                        
                    if config.verbose:
                        print "Creating %s" % oufile
                        
                    command = runner + " --data-paths=\"" + path[0] \
                              + "\",1 --starting-ids=" \
                              + str(start_id[0]) + "," \
                              + str(start_id[1]) \
                              + " --ending-ids=" + str(end_id[0]) \
                              + "," \
                              + str(end_id[1]) + " --output=" \
                              + oufile \
                              + " " + config.data
                    if config.ts_verbose:
                        command += " -v"
                                
                    os.system(command)
        else:
            for j in range(reps):
                start_id = config.pixel_group * j
                end_id = config.pixel_group * (j + 1)

                counter = 0
                for tube in tubes:
                    run_gen = []
                    run_gen.append(mfilter)
                    run_gen.append("--bank-ids=%s,%s" % (bank[-1], bank[-1]))
                    run_gen.append("--h-ranges=%d,%d" % (tube-1, tube-1))
                    run_gen.append("--v-ranges=%d,%d" % (start_id, end_id-1))
                    if counter != 0:
                        run_gen.append("--append")

                    os.system(" ".join(run_gen))
                    counter += 1
                    
                roifile = "pixel_mask.dat"

                tag1 = str(j + 1)
                
                oufile = bank + "_" + tag + "_" + tag1 + ".tof"

                if config.verbose:
                    print "Creating %s" % oufile
                        
                command = []

                command.append(runner)
                command.append("--data-paths=%s,1" % path[0])
                command.append("--roi-file=%s" % roifile)
                command.append("--output=%s" % oufile)
                command.append(config.data)
                if config.ts_verbose:
                    command.append("-v")

                os.system(" ".join(command))

                os.remove(roifile)
                

if __name__ == "__main__":
    import os

    import hlr_utils
    import sns_inst_util

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

    parser.add_option("-t", "--ts-verbose", action="store_true",
                      dest="ts_verbose", help="Flag to set verbose on "\
                      +"tof_slicer")
    parser.set_defaults(ts_verbose=False)

    parser.add_option("", "--sum-tubes-bank1", dest="sum_tubes_bank1",
                      help="Provide a listing of tubes to sum over for "\
                      +"bank1. Example: 1,3,5,10-37,45,57-64")

    parser.add_option("", "--sum-tubes-bank2", dest="sum_tubes_bank2",
                      help="Provide a listing of tubes to sum over for "\
                      +"bank2. Example: 1,3,5,10-37,45,57-64")    

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

    # set the verbosity on tof_slicer
    configure.ts_verbose = options.ts_verbose

    # set vertical
    configure.vertical = options.vertical

    # set pixel grouping
    configure.pixel_group = options.pixel_group

    # set bank1 tubes for summing 
    if options.sum_tubes_bank1 is not None:
        configure.sum_tubes_bank1 = sns_inst_util.generateList(\
            options.sum_tubes_bank1.split(','))
    else:
        configure.sum_tubes_bank1 = options.sum_tubes_bank1

    # set bank2 tubes for summing 
    if options.sum_tubes_bank2 is not None:
        configure.sum_tubes_bank2 = sns_inst_util.generateList(\
            options.sum_tubes_bank2.split(','))
    else:
        configure.sum_tubes_bank2 = options.sum_tubes_bank2

    run(configure)
