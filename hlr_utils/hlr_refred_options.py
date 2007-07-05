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
        
        # Add REF_M specific options
        self.add_option("", "--lambda-bins", dest="lambda_bins",
                        help="Specify the minimum and maximum wavelength "\
                        +"values and the wavelength bin width in Angstroms")

        self.add_option("", "--mom-trans-bins", dest="Q_bins",
                        help="Specify the minimum and maximum momentum "\
                        +"transfer values and the momentum transfer bin "\
                        +"width in Angstroms^-1")

        self.add_option("", "--tof-only", action="store_const", const=0,
                        dest="step_stop",
                        help="Flag to have driver stop processing data at TOF")
        
        self.add_option("", "--wave-only", action="store_const", const=1,
                        dest="step_stop",
                        help="Flag to have driver stop processing data at "\
                        +"wavelength")
        self.set_defaults(step_stop=2)

        self.add_option("", "--split", action="store_true", dest="split",
                        help="Flag to split data up in N spectra along the "\
                        +"short axis of the signal ROI.")
        self.set_defaults(split=False)

        self.add_option("", "--no-filter", action="store_true",
                        dest="no_filter",
                        help="Flag to turn off bad data filtering.")
        self.set_defaults(no_filter=False)

        self.add_option("", "--no-dtot", action="store_true", dest="no_dtot",
                        help="Flag to turn off calculation of delta t over t")
        self.set_defaults(no_dtot=False)

        # Remove unneeded options
        self.remove_option("--combine")
        self.remove_option("--dump-norm")
        self.remove_option("--dump-norm-bkg")

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

    # Set the lambda bins
    if hlr_utils.cli_provide_override(configure, "lambda_bins",
                                      "--lambda-bins"):
        configure.lambda_bins = hlr_utils.AxisFromString(options.lambda_bins)

    # Set the momentum transfer bins
    if hlr_utils.cli_provide_override(configure, "Q_bins", "--mom-trans-bins"):
        configure.Q_bins = hlr_utils.AxisFromString(options.Q_bins)

    # Set the step stop flag
    if hlr_utils.cli_provide_override(configure, "step_stop", "--step-stop"):
        configure.step_stop = options.step_stop

    # Set the split spectra flag
    if hlr_utils.cli_provide_override(configure, "split", "--split"):
        configure.split = options.split        

    # Set the no bad data filter flag
    if hlr_utils.cli_provide_override(configure, "no_filter", "--no-filter"):
        configure.no_filter = options.no_filter

    # Set the no delta t over t flag
    if hlr_utils.cli_provide_override(configure, "no_dtot", "--no-dtot"):
        configure.no_dtot = options.no_dtot        
