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
This program reads a TOF U{NeXus<www.nexusformat.org>} file and creates a TOF
spectrum from the data. The data maybe pixel filtered by providing the
appropriate information on the command-line.
""" 

def run(config):
    """
    This method is where the data reduction process gets done.

    @param config: Object containing the data reduction configuration
                   information.
    @type config: L{hlr_utils.Configure}
    """
    import sys
    
    import DST

    try:
        data_dst = DST.getInstance("application/x-NeXus", config.data[0])
    except SystemError:
        print "ERROR: Failed to data read file %s" % config.data[0]
        sys.exit(-1)

    so_axis = "time_of_flight"

    if config.verbose:
        print "Reading data file"

    if config.roi_file is None:
        d_som1 = data_dst.getSOM(config.data_paths.toPath(), so_axis,
                                 start_id=config.starting_ids,
                                 end_id=config.ending_ids)
    else:
        d_som1 = data_dst.getSOM(config.data_paths.toPath(), so_axis,
                                 roi_file=config.roi_file)

    if config.dump_pxl:
        hlr_utils.write_file(config.data[0], "text/Spec", d_som1,
                             output_ext="tfp", verbose=config.verbose,
                             path_replacement=config.path_replacement,
                             message="pixel TOF information")
    else:
        pass

    if config.tib_const is not None:
        import common_lib
        d_som2 = common_lib.sub_ncerr(d_som1, config.tib_const.toValErrTuple())

        if config.dump_sxl:
            hlr_utils.write_file(config.data[0], "text/Spec", d_som2,
                                 output_ext="tsp", verbose=config.verbose,
                                 path_replacement=config.path_replacement,
                                 message="TIB const sub pixel TOF information")
        
    else:
        d_som2 = d_som1

    del d_som1

    if len(d_som2) == 1:
        if config.verbose:
            print "Summing 1 spectrum."        
        d_som3 = d_som2
    else:
        if config.verbose:
            print "Summing %d spectra." % len(d_som2)
        d_som3 = dr_lib.sum_all_spectra(d_som2)
        d_som3[0].id = d_som2[0].id

    del d_som2

    hlr_utils.write_file(config.output, "text/Spec", d_som3, replace_ext=False,
                         verbose=config.verbose,
                         path_replacement=config.path_replacement,
                         message="combined TOF information")

if __name__ == "__main__":
    import dr_lib
    import hlr_utils

    # Make description for driver
    result = []
    result.append("This driver reads a TOF NeXus file and creates a *.tof")
    result.append("(3-column ASCII) of I(TOF). Other intermediate files")
    result.append("can be produced by using the appropriate dump-X flag")
    result.append("described in this help. The file extensions are described")
    result.append("in the option documentation.")
    
    # set up the options available
    parser = hlr_utils.InstOptions("usage: %prog [options] <datafile>", None,
                                    None, hlr_utils.program_version(), 'error',
                                    " ".join(result))

    # Defaults
    parser.set_defaults(data_paths="/entry/bank1,1")

    # Remove unneeded options
    parser.remove_option("--norm")
    parser.remove_option("--inst-geom")
    
    parser.add_option("", "--starting-ids", dest="starting_ids",
                      help="Specify the comma separated list of i and j pixel"\
                      +" locations on the detector. This is inclusive: "\
                      +"0,0,4,3 (for two banks)")
    
    parser.add_option("", "--ending-ids", dest="ending_ids",
                      help="Specify the comma separated list of i and j pixel"\
                      +" locations on the detector. This is exclusive: "\
                      +"0,0,4,3 (for two banks)")

    parser.add_option("", "--dump-pxl", action="store_true", dest="dump_pxl",
                      help="Flag to dump the TOF for all pixels. Creates a  "\
                      +"*.tfp file.")
    parser.set_defaults(dump_pxl=False)

    parser.add_option("", "--roi-file", dest="roi_file",
                      help="Specify a file that contains a list of pixel ids "\
                      +"from a region-of-interest to be read from the data")

    parser.add_option("", "--tib-const", dest="tib_const",
                      help="Specify constant to subtract from data "\
                        +"spectra: value, err^2")

    parser.add_option("", "--dump-sxl", action="store_true", dest="dump_sxl",
                      help="Flag to dump the TOF for all pixels after TIB"\
                      +"subtraction. Creates a *.tsp file.")
    parser.set_defaults(dump_sxl=False)    

    (options, args) = parser.parse_args()

    # set up the configuration
    configure = hlr_utils.Configure()

    # Call the configuration setter for InstOptions
    hlr_utils.InstConfiguration(parser, configure, options, args)

    # Set the ROI file
    if hlr_utils.cli_provide_override(configure, "roi_file", "--roi-file"):
        configure.roi_file = hlr_utils.determine_files(options.roi_file,
                                                       one_file=True)

    # set the starting ids
    if hlr_utils.cli_provide_override(configure, "starting_ids",
                                      "--starting-ids"):
        if options.starting_ids is not None:
            configure.starting_ids = hlr_utils.create_id_pairs(\
            options.starting_ids,\
            options.data_paths)
        else:
            configure.starting_ids = options.starting_ids

    # set the ending ids
    if hlr_utils.cli_provide_override(configure, "ending_ids", "--ending-ids"):
        if options.ending_ids is not None:
            configure.ending_ids = hlr_utils.create_id_pairs(\
                options.ending_ids,
                options.data_paths,
                inc=True)
        else:
            configure.ending_ids = options.ending_ids

    # set the dump all TOF pixel information
    if hlr_utils.cli_provide_override(configure, "dump_pxl", "--dump-pxl"):
        configure.dump_pxl = options.dump_pxl

    # set the dump all TOF pixel information after TIB subtraction
    if hlr_utils.cli_provide_override(configure, "dump_sxl", "--dump-sxl"):
        configure.dump_sxl = options.dump_sxl

    # Set the time-independent background constant
    if hlr_utils.cli_provide_override(configure, "tib_const", "--tib-const"): 
        configure.tib_const = hlr_utils.DrParameterFromString(\
                    options.tib_const, True)

    # run the program
    run(configure)
