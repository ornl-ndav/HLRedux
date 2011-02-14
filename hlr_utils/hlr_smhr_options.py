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
import hlr_ref_options
import hlr_utils

class SmhrOptions(hlr_ref_options.RefOptions):
    """
    This class provides options for the REF specmh_reduction driver.
    """

    def __init__(self, usage=None, option_list=None, version=None,
                 conflict_handler='error', description=None, **kwargs):
        """
        Constructor for C{SmhrOptions}

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
        hlr_ref_options.RefOptions.__init__(self, usage, option_list,
                                            Option, version, conflict_handler,
                                            description)
        
        self.add_option("", "--ecell", dest="ecell",
                        help="Specify the empty sample cell file")
        
        self.add_option("", "--subtrans-coeff", dest="subtrans_coeff",
                        nargs=2, type="float", help="Provide the substrate "\
                        +"transmission coefficients.")
        
        self.add_option("", "--substrate-diam", dest="substrate_diam",
                        type="float",
                        help="Provide the substrate diameter in cm.")
        
        self.add_option("", "--scale-ecell", dest="scale_ecell", type="float",
                        help="Provide the scaling factor for the empty cell "\
                        +"subtraction.")
        self.set_defaults(scale_ecell=1.0)
        
        self.add_option("", "--dump-ecell-rtof", action="store_true",
                        dest="dump_ecell_rtof",
                        help="Dump the empty cell spectra after all scaling. "\
                        +"Creates a *.ertof file.")
        self.set_defaults(dump_ecell_rtof=False)
        

def SmhrConfiguration(parser, configure, options, args):
    """
    This function sets the incoming C{Configure} object with all the options
    that have been specified via the C{SmhrOptions} object.

    @param parser: The parser object
    @type parser: L{hlr_utils.SmhrOptions}
    
    @param configure: The configuration object
    @type configure: L{hlr_utils.Configure}
    
    @param options: The parsed options from C{SmhrOptions}
    @type options: C{Option}

    @param args: The parsed arguments from C{SmhrOptions}
    @type args: C{list}
    """

    # Call the configuration setter for RefOptions
    hlr_ref_options.RefConfiguration(parser, configure, options, args)

    # Setup the empty cell file list
    if hlr_utils.cli_provide_override(configure, "ecell", "--ecell"):
        configure.ecell = hlr_utils.determine_files(options.ecell,
                                                    configure.inst,
                                                    configure.facility)

    # If empty cell subtraction is desired, turn off standard background
    # subtraction
    if configure.ecell is not None:
        configure.no_bkg = True
        
    # Setup the substrate transmission coefficients
    if hlr_utils.cli_provide_override(configure, "subtrans_coeff",
                                      "--subtrans-coeff"):
        configure.subtrans_coeff = options.subtrans_coeff

    # Setup the substrate diameter parameter
    if hlr_utils.cli_provide_override(configure, "substrate_diam",
                                      "--substrate-diam"):
        configure.substrate_diam = options.substrate_diam

    # Setup the empty cell scaling parameter
    if hlr_utils.cli_provide_override(configure, "scale_ecell",
                                      "--scale_ecell"):
        configure.scale_ecell = options.scale_ecell        

    # Set the ability to dump the empty cell R(TOF) information
    if hlr_utils.cli_provide_override(configure, "dump_ecell_rtof",
                                      "--dump-ecell-rtof"): 
        configure.dump_ecell_rtof = options.dump_ecell_rtof

    if options.dump_all:
        configure.dump_ecell_rtof = True
