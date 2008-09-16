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
This program reads in two sets of one or more files and performs a specified
simple math execution between the two file sets. The program will also allow
the final spectrum to be rescaled before being written out to file.
"""

def run(config, tim):
    """
    This method is where the data reduction process gets done.

    @param config: Object containing the data reduction configuration
                   information.
    @type config: L{hlr_utils.Configure}

    @param tim: Object that will allow the method to perform timing
                evaluations.
    @type tim: C{sns_time.DiffTime}    
    """
    import common_lib
    import dr_lib
    
    if tim is not None:
        tim.getTime(False)
        old_time = tim.getOldTime()

    if config.data1 is None or config.data2 is None:
        raise RuntimeError("Need to pass a data filename(s) to the driver "\
                           +"script.")

    dst_type1 = hlr_utils.file_peeker(config.data1[0])

    if config.verbose:
        print "Initial file type (data set 1):", dst_type1

    d_som1 = dr_lib.add_files(config.data1, dst_type=dst_type1,
                              Verbose=config.verbose,
                              Timer=tim)

    dst_type2 = hlr_utils.file_peeker(config.data2[0])

    if config.verbose:
        print "Initial file type (data set 2):", dst_type2

    d_som2 = dr_lib.add_files(config.data2, dst_type=dst_type2,
                              Verbose=config.verbose,
                              Timer=tim)

    # Get requested simple math operation
    func = common_lib.__getattribute__(config.operation)

    d_som3 = func(d_som1, d_som2)

    del d_som1, d_som2

    # Rescale data if necessary
    if config.rescale is not None:
        d_som4 = common_lib.mult_ncerr(d_som3, (config.rescale, 0.0))
    else:
        d_som4 = d_som3

    del d_som3

    # Write out file after simple math operation
    hlr_utils.write_file(config.output, dst_type1, d_som4,
                         verbose=config.verbose,
                         replace_ext=False,
                         path_replacement=config.path_replacement,
                         axis_ok=True,
                         message="operated file")

    if tim is not None:
        tim.setOldTime(old_time)
        tim.getTime(msg="Total Running Time")

if __name__ == "__main__":
    import hlr_utils

    # Make description for driver
    description = []
    description.append("")
    description.append("This driver reads in data reduction produced 3-column")
    description.append("ASCII or DAVE 2D ASCII files. The expected filenames")
    description.append("should be of the form <inst_name>_<run_number>_")
    description.append("<segment_number>[_dataset_type].<ext>. If they are")
    description.append("not, the driver will still work, but it is possible")
    description.append("that the first data file will be overwritten. In")
    description.append("this case, it is best to provide an output filename")
    description.append("via the command-line. Once the files are read in,")
    description.append("the reqested simple math operation is performed on")
    description.append("the two sets of data: data1 op data2. The default")
    description.append("operation is add. The final result can also be")
    description.append("rescaled by providing the scaling constant.")

    # Set up the options available
    parser = hlr_utils.BasicOptions("usage: %prog [options]", None, None,
                                    hlr_utils.program_version(), 'error',
                                    " ".join(description))

    # Specify the first data set
    parser.add_option("", "--data1", dest="data1", help="Specify the files "\
                      +"of the first dataset")

    # Specify the second data set
    parser.add_option("", "--data2", dest="data2", help="Specify the files "\
                      +"of the second dataset")    

    # Specify the operation as addition
    parser.add_option("-a", "--add", dest="operation", action="store_const",
                      const="add_ncerr", help="Perform data1 + data2")
    parser.set_defaults(operation="add_ncerr")
    
    # Specify the operation as subtraction
    parser.add_option("-s", "--sub", dest="operation", action="store_const",
                      const="sub_ncerr", help="Perform data1 - data2")
    
    # Specify the operation as multiplication
    parser.add_option("-m", "--mult", dest="operation", action="store_const",
                      const="mult_ncerr", help="Perform data1 * data2")
    
    # Specify the operation as division
    parser.add_option("-d", "--div", dest="operation", action="store_const",
                      const="div_ncerr", help="Perform data1 / data2")
    
    # Specify the rescaling constant
    parser.add_option("-r", "--rescale", dest="rescale", help="Specify a "\
                      +"constant with which to rescale the final data.")
    
    parser.add_option("", "--timing", action="store_true", dest="timing",
                      help="Flag to turn on timing of code")
    parser.set_defaults(timing=False)

    # Change help message for output option
    parser.get_option("-o").help = "Specify a new output file name, a new "\
                                   +"data directory or a new directory plus "\
                                   +"output file name. The new directory "\
                                   +"must exist. The default is to use the "\
                                   +"current working directory and the first "\
                                   +"data file as the basis for the output "\
                                   +"file name."

    # Do not need to use the following options
    parser.remove_option("--config")
    parser.remove_option("--data")

    (options, args) = parser.parse_args()

    # set up the configuration
    configure = hlr_utils.Configure()

    # Need to set the inst parameter to None to spoof data file finder
    configure.inst = None

    # Need to set the facility parameter to None to spoof data file finder
    configure.facility = None    

    # Need to spoof the data check
    configure.data = [""]
    options.data = None

    # Quick test on output
    if options.output is not None:
        filename = hlr_utils.fix_filename(options.output)
        import os
        # If this is a directory only, then we want to have the default
        # created filename
        if os.path.isdir(filename) and not os.path.isfile(filename):
            have_output = False
            is_dir = True
        else:
            have_output = True
            is_dir = False
    else:
        have_output = False
        is_dir = False

    # Temporarily silence verbosity
    old_verbosity = options.verbose
    options.verbose = False

    # Call the configuration setter for SNSOptions
    hlr_utils.BasicConfiguration(parser, configure, options, args)

    # Reset verbosity
    configure.verbose = old_verbosity

    # This is a standard file, but we need to remove the segment number
    if not have_output:
        if is_dir:
            dired = os.path.dirname(configure.output)
            dired += "/"
            infile = os.path.basename(configure.output)
        else:
            dired = ""
            infile = configure.output

        # Check and remove extra extensions. This happens when original
        # extension is not .txt
        if infile.rfind('.') != infile.find('.'):
            infile = infile[:infile.rfind('.')]

        configure.path_replacement = dired
        parts = infile.split('_')
        outfile = dired + "_".join(parts[:2])
        # Have dataset tag
        if len(parts) == 4:
            configure.output = outfile + "_" + parts[-1]
        else:
            ext_parts = parts[-1].split('.')
            configure.output = outfile + "." + ext_parts[-1]
    # An output file has been provided so do nothing
    else:
        pass

    if configure.verbose:
        print "Using %s as output file" % configure.output

    # Set the files from the first data set
    configure.data1 = hlr_utils.determine_files(options.data1,
                                                configure.inst,
                                                configure.facility,
                                                stop_on_none=True)

    # Set the files from the second data set
    configure.data2 = hlr_utils.determine_files(options.data2,
                                                configure.inst,
                                                configure.facility,
                                                stop_on_none=True)    

    # Set the math operation
    configure.operation = options.operation

    # Set the rescaling constant
    try:
        configure.rescale = float(options.rescale)
    except TypeError:
        configure.rescale = options.rescale
    
    # Setup the timing object
    if options.timing:
        import sns_timing
        timer = sns_timing.DiffTime()
    else:
        timer = None

    # Run the program
    run(configure, timer)
