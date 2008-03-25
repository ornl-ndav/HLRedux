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
This program reads in data reduction produced 3-column ASCII or DAVE 2D ASCII
files.
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
    import sys

    import common_lib
    import dr_lib
    
    if tim is not None:
        tim.getTime(False)
        old_time = tim.getOldTime()

    if config.data is None:
        raise RuntimeError("Need to pass a data filename to the driver "\
                           +"script.")

    dst_type = hlr_utils.file_peeker(config.data[0])

    if config.verbose:
        print "Initial file type:", dst_type

    d_som1 = dr_lib.add_files(config.data, dst_type=dst_type,
                              Verbose=config.verbose,
                              Timer=tim)[0]

    hlr_utils.write_file(config.output, dst_type, d_som1,
                         verbose=config.verbose,
                         replace_ext=False,
                         path_replacement=config.path_replacement,
                         axis_ok=True,
                         message="combined file")

    if tim is not None:
        tim.setOldTime(old_time)
        tim.getTime(msg="Total Running Time")
    
if __name__ == "__main__":
    import hlr_utils

    # Make description for driver
    description = []
    description.append("This driver reads in data reduction produced 3-column")
    description.append("ASCII or DAVE 2D ASCII files. The expected filenames")
    description.append("should be of the form <inst_name>_<run_number>_")
    description.append("<segment_number>[_dataset_type].<ext>. If they are")
    description.append("not, the driver will still work, but it is possible")
    description.append("that the first data file will be overwritten. In")
    description.append("this case, it is best to provide an output filename")
    description.append("via the command-line.")

    # Set up the options available
    parser = hlr_utils.BasicOptions("usage: %prog [options] <datafiles>", None,
                                    None, hlr_utils.program_version(), 'error',
                                    " ".join(description))

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

    # Do not need to use config option
    parser.remove_option("--config")

    (options, args) = parser.parse_args()

    # set up the configuration
    configure = hlr_utils.Configure()

    # Need to set the inst parameter to None to spoof data file finder
    configure.inst = None

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
        
    # Setup the timing object
    if options.timing:
        import sns_timing
        timer = sns_timing.DiffTime()
    else:
        timer = None

    # Run the program
    run(configure, timer)
