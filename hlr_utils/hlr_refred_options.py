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

from optparse import Option
import hlr_utils

class RefRedOptions(hlr_utils.RefOptions):
    """
    This class provides options for the REF instruments for use in
    reducing neutron scattering data with the data reduction drivers.
    """

    def __init__(self, usage=None, option_list=None, version=None,
                 conflict_handler='error', description=None, **kwargs):
        """
        Constructor for C{RefRedOptions}

        @param usage: (OPTIONAL) The correct usage of program in which the
                                 option class is used
        @type usage: C{string}
        
        @param option_list: (OPTIONAL) A list containing the alternative method
                                       of providing options
        @type option_list: C{list}

        @param version: (OPTIONAL) The program version
        @type version: C{string}

        @param conflict_handler: (OPTIONAL) How the parser handles conflicts
                                            between options.
        @type conflict_handler: C{string}

        @param description: (OPTIONAL) The program description
        @type description: C{string}
        
        @param kwargs: A list of keyword arguments that the function accepts:
        """
        # parent constructor
        hlr_utils.RefOptions.__init__(self, usage, option_list, Option,
                                      version, conflict_handler, description)
        
        self.add_option("", "--mom-trans-bins", dest="Q_bins",
                        help="Specify the minimum and maximum momentum "\
                        +"transfer values and the momentum transfer bin "\
                        +"width in Angstroms^-1")

        self.add_option("", "--no-filter", action="store_true",
                        dest="no_filter",
                        help="Flag to turn off bad data filtering.")
        self.set_defaults(no_filter=False)

        self.add_option("", "--store-dtot", action="store_true",
                        dest="store_dtot",
                        help="Flag to turn on storage of delta t over t in "\
                        +"TOF output file.")
        self.set_defaults(store_dtot=False)

        self.add_option("", "--data-peak-excl", dest="data_peak_excl",
                        type="int", nargs=2,
                        help="Peak exclusion range pixel IDs for sample data.")

        self.add_option("", "--norm-peak-excl", dest="norm_peak_excl",
                        type="int", nargs=2,
                        help="Peak exclusion range pixel IDs for "\
                        +"normalization data.")    
        
def RefRedConfiguration(parser, configure, options, args):
    """
    This function sets the incoming C{Configure} object with all the options
    that have been specified via the C{RefRedOptions} object.

    @param parser: The parser object
    @type parser: L{hlr_utils.RefRedOptions}
    
    @param configure: The configuration object
    @type configure: L{hlr_utils.Configure}
    
    @param options: The parsed options from C{RefRedOptions}
    @type options: C{Option}

    @param args: The parsed arguments from C{RefRedOptions}
    @type args: C{list}
     """

    # Call the configuration setter for RefOptions
    hlr_utils.RefConfiguration(parser, configure, options, args)

    # Set the momentum transfer bins
    if hlr_utils.cli_provide_override(configure, "Q_bins", "--mom-trans-bins"):
        configure.Q_bins = hlr_utils.AxisFromString(options.Q_bins)

    # Set the no bad data filter flag
    if hlr_utils.cli_provide_override(configure, "no_filter", "--no-filter"):
        configure.no_filter = options.no_filter

    # Set the store delta t over t flag
    if hlr_utils.cli_provide_override(configure, "store_dtot", "--store-dtot"):
        configure.store_dtot = options.store_dtot        

    # Set the pixel ID range values for peak exclusion from sample data
    if hlr_utils.cli_provide_override(configure, "data_peak_excl",
                                      "--data-peak-excl"):
        configure.data_peak_excl = options.data_peak_excl

    # Set the pixel ID range values for peak exclusion from normalization data
    if hlr_utils.cli_provide_override(configure, "norm_peak_excl",
                                      "--norm-peak-excl"):
        configure.norm_peak_excl = options.norm_peak_excl        
