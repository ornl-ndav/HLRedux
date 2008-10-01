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
import hlr_options
import hlr_utils

class DgsOptions(hlr_options.InstOptions):
    """
    This class provides options for the DGS class of instruments for use in
    reducing neutron scattering data with the data reduction drivers.
    """
    
    def __init__(self, usage=None, option_list=None, options_class=None,
                 version=None, conflict_handler='error', description=None,
                 **kwargs):
        """
        Constructor for C{DgsOptions}

        @param usage: (OPTIONAL) The correct usage of program in which the
                                 option class is used
        @type usage: C{string}
        
        @param option_list: (OPTIONAL) A list containing the alternative method
                                       of providing options
        @type option_list: C{list}

        @param options_class: (OPTIONAL) The options class type
        @type options_class: C{optparse.Option}

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
        hlr_options.InstOptions.__init__(self, usage, option_list,
                                         Option, version, conflict_handler,
                                         description, inst="DGS")

        self.add_option("", "--usmon-path", dest="usmon_path",
                        help="Specify the comma separated list of upstream "\
                        +"monitor path and signal.")

        self.add_option("", "--dsmon-path", dest="dsmon_path",
                        help="Specify the comma separated list of downstream "\
                        +"monitor path and signal.")

        self.add_option("", "--initial-energy", dest="initial_energy",
                        help="Specify the initial energy for the reduction in"\
                        +"in units of meV")

        self.add_option("", "--energy-bins", dest="E_bins",
                        help="Specify the minimum and maximum energy values "\
                        +"and the energy bin width in meV")

def DgsConfiguration(parser, configure, options, args):
    """
    This function sets the incoming C{Configure} object with all the options
    that have been specified via the C{DgsOptions} object.

    @param parser: The parser object
    @type parser: L{hlr_utils.DgsOptions}
    
    @param configure: The configuration object
    @type configure: L{hlr_utils.Configure}
    
    @param options: The parsed options from C{DgsOptions}
    @type options: C{Option}

    @param args: The parsed arguments from C{DgsOptions}
    @type args: C{list}
    """

    # Call the configuration setter for InstOptions
    hlr_options.InstConfiguration(parser, configure, options, args, inst="DGS")

    # Set the upstream monitor path
    if hlr_utils.cli_provide_override(configure, "usmon_path", "--usmon-path"):
        configure.usmon_path = hlr_utils.NxPath(options.usmon_path)

    # Set the downstream monitor path
    if hlr_utils.cli_provide_override(configure, "dsmon_path", "--dsmon-path"):
        configure.dsmon_path = hlr_utils.NxPath(options.dsmon_path)        

    # Set the initial energy
    if hlr_utils.cli_provide_override(configure, "initial_energy",
                                      "--initial-energy"):
        configure.initial_energy = hlr_utils.DrParameterFromString(\
            options.initial_energy)

    # Set the energy transfer bins
    if hlr_utils.cli_provide_override(configure, "E_bins", "--energy-bins"):
        configure.E_bins = hlr_utils.AxisFromString(options.E_bins)

    if configure.E_bins is None:
        parser.error("You must provide energy transfer binning via the "\
                     +"energy-bins option")        
