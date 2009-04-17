#!/usr/bin/env python

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

    import nessi_list
    import SOM
    
    import bisect

    is_init = False
    Q_axis = None
    E_axis = None
    len_Q = 0
    len_E = 0
    so_id = None
    lo_val = -999
    hi_val = -999
    scan = nessi_list.NessiList()
    scan_err2 = nessi_list.NessiList()
    
    # Object to hold integrated data for each temperature scan
    result = SOM.SOM()
    result.attr_list["filename"] = config.data
    result.setAllAxisLabels(["Q", "T"])
    result.setAllAxisUnits(["1/Angstroms", "Kelvin"])
    result.setYLabel("Integral")
    result.setYUnits("")
    result.setDataSetType("density")
    
    int_so = SOM.SO()

    # Read in all data files
    counter = 0
    for datafile in config.data:
        som = dr_lib.add_files([datafile], dst_type=dst_type,
                               Verbose=config.verbose)

        if not is_init:
            Q_axis = som[0].axis[0].val
            len_Q = len(Q_axis)
            E_axis = som[0].axis[1].val
            len_E = len(E_axis)
            so_id = som[0].id
            int_so.id = so_id
            int_so.axis[0].val = E_axis
            lo_val = bisect.bisect_left(E_axis, config.int_range[0])
            hi_val = bisect.bisect_left(E_axis, config.int_range[1])

        for i in xrange(len_Q):
            int_so.y = som[0].y[i*len_E:(i+1)*len_E]
            int_so.var_y = som[0].var_y[i*len_E:(i+1)*len_E]
            value = dr_lib.integrate_axis_py(int_so, start=lo_val, end=hi_val)
            scan.append(value[0])
            scan_err2.append(value[1])

        is_init = True
        counter += 1

    # Reorient data to make groups of temps for a single Q bin
    final_data = nessi_list.NessiList()
    final_data_err2 = nessi_list.NessiList()

    scann = scan.toNumPy()
    scann_err2 = scan_err2.toNumPy()

    import itertools
    for i in xrange(len_Q):
        sslice = scann[i::len_Q]
        sslice_err2 = scann_err2[i::len_Q]
        for val, err in itertools.izip(sslice, sslice_err2):
            final_data.append(val)
            final_data_err2.append(err)
    
    # Create placeholder for combined spectrum
    so = SOM.SO(2)
    so.id = so_id
    so.y = final_data
    so.var_y = final_data_err2
    so.axis[0].val = Q_axis
    temp = nessi_list.NessiList()
    temp.extend(config.temps)
    so.axis[1].val = temp

    result.append(so)

    hlr_utils.write_file(config.output, "text/Dave2d", result,
                         verbose=config.verbose,
                         replace_ext=False,
                         axis_ok=True,
                         path_replacement=config.path_replacement,
                         message="combined file")

    result.attr_list["config"] = config

    hlr_utils.write_file(config.output, "text/rmd", result,
                         output_ext="rmd",
                         data_ext=config.ext_replacement,
                         path_replacement=config.path_replacement,
                         verbose=config.verbose,
                         message="metadata")


if __name__ == "__main__":
    import dr_lib
    import hlr_utils

    # Make description for driver
    description = []
    description.append("This driver reads in DAVE 2D ASCII files each")
    description.append("containing a single temperature scan, performs")
    description.append("an integration for each Q bin, and outputs that")
    description.append("information to a file.")

    # set up the options available
    parser = hlr_utils.BasicOptions("usage: %prog [options] <datafile>", None,
                                    None, hlr_utils.program_version(), 'error',
                                    " ".join(description))

    parser.add_option("", "--int-range", dest="int_range", type="float",
                      nargs=2, help="Specify the energy integration range in "\
                      +"ueV.")

    parser.add_option("", "--temps=", dest="temps",
                      help="Specify the temperatures (in K) for the "\
                      +"corresponding list of data files in a "\
                      +"comma-delimited list. NOTE: No checks "\
                      +"can be made, so you must make sure the order is "\
                      +"correct.")

    # Change help slightly for data option
    parser.get_option("--data").help = "Specify the DAVE 2D ASCII files."

    # Remove unneeded options
    parser.remove_option("--inst")
    parser.remove_option("--facility")
    parser.remove_option("--config")

    (options, args) = parser.parse_args()

    # set up the configuration
    configure = hlr_utils.Configure()

    # Call the configuration setter for BasicOptions
    hlr_utils.BasicConfiguration(parser, configure, options, args)

    # MUST OVERRIDE THE DEFAULT OUTPUT FILE NAME
    if options.output is None:
        parser.error("Must specify an output file via the -o or --output "\
                     +"flag.")

    # Set the integration range option
    configure.int_range = options.int_range

    # Set the temperature list
    configure.temps = [float(T) for T in options.temps.split(',')]

    # run the program
    run(configure)
