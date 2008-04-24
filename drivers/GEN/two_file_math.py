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

def run(config):
    pass

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
    description.append("the two sets of data: data1 op data2. The final ")
    description.append("result can also be rescaled by providing the scaling")
    description.append("constant.")

    # Set up the options available
    parser = hlr_utils.BasicOptions("usage: %prog [options] <datafiles>", None,
                                    None, hlr_utils.program_version(), 'error',
                                    " ".join(description))

    parser.add_option("", "--timing", action="store_true", dest="timing",
                      help="Flag to turn on timing of code")
    parser.set_defaults(timing=False)

    # Do not need to use config option
    parser.remove_option("--config")

    (options, args) = parser.parse_args()

    # set up the configuration
    configure = hlr_utils.Configure()

    # Need to set the inst parameter to None to spoof data file finder
    configure.inst = None

    # Temporarily silence verbosity
    old_verbosity = options.verbose
    options.verbose = False

    # Call the configuration setter for SNSOptions
    hlr_utils.BasicConfiguration(parser, configure, options, args)

    # Reset verbosity
    configure.verbose = old_verbosity

    # Setup the timing object
    if options.timing:
        import sns_timing
        timer = sns_timing.DiffTime()
    else:
        timer = None

    # Run the program
    run(configure, timer)
