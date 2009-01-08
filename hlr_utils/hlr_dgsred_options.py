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
import hlr_dgs_options
import hlr_utils

class DgsRedOptions(hlr_dgs_options.DgsOptions):
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
        hlr_options.DgsOptions.__init__(self, usage, option_list,
                                        Option, version, conflict_handler,
                                        description)

        self.add_option("", "--corner-geom", dest="corner_geom",
                        help="Specify the file containing the corner "\
                        +"geometry information.")
        
        self.add_option("", "--energy-bins", dest="E_bins",
                        help="Specify the minimum and maximum energy values "\
                        +"and the energy bin width in meV")

        self.add_option("", "--qx-bins", dest="Qx_bins",
                        help="Specify the minimum, maximum and bin width of "\
                        +"the x-component of the momentum transfer in "\
                        +"1/Angstroms.")

        self.add_option("", "--qy-bins", dest="Qy_bins",
                        help="Specify the minimum, maximum and bin width of "\
                        +"the y-component of the momentum transfer in "\
                        +"1/Angstroms.")

        self.add_option("", "--qz-bins", dest="Qz_bins",
                        help="Specify the minimum, maximum and bin width of "\
                        +"the z-component of the momentum transfer in "\
                        +"1/Angstroms.")                

def DgsRedConfiguration(parser, configure, options, args):
    """
    This function sets the incoming C{Configure} object with all the options
    that have been specified via the C{DgsRedOptions} object.

    @param parser: The parser object
    @type parser: L{hlr_utils.DgsRedOptions}
    
    @param configure: The configuration object
    @type configure: L{hlr_utils.Configure}
    
    @param options: The parsed options from C{DgsRedOptions}
    @type options: C{Option}

    @param args: The parsed arguments from C{DgsRedOptions}
    @type args: C{list}
    """

    # Call the configuration setter for DgsOptions
    hlr_dgs_options.DgsConfiguration(parser, configure, options, args)

    # Set the corner geometry information file
    if hlr_utils.cli_provide_override(configure, "corner_geom",
                                      "--corner-geom"):
        configure.corner_geom = options.corner_geom

    if configure.corner_geom is None:
        parser.error("You must provide a corner geometry file via the "\
                     +"corner-geom option!")

    # Set the energy transfer bins
    if hlr_utils.cli_provide_override(configure, "E_bins", "--energy-bins"):
        configure.E_bins = hlr_utils.AxisFromString(options.E_bins)

    if configure.E_bins is None:
        parser.error("You must provide energy transfer binning via the "\
                     +"energy-bins option")        

    # Set the x-component of the momentum transfer bins
    if hlr_utils.cli_provide_override(configure, "Qx_bins", "--qx-bins"):
        configure.Qx_bins = hlr_utils.AxisFromString(options.Qx_bins)

    # Set the y-component of the momentum transfer bins
    if hlr_utils.cli_provide_override(configure, "Qy_bins", "--qy-bins"):
        configure.Qy_bins = hlr_utils.AxisFromString(options.Qy_bins)

    # Set the z-component of the momentum transfer bins
    if hlr_utils.cli_provide_override(configure, "Qz_bins", "--qz-bins"):
        configure.Qz_bins = hlr_utils.AxisFromString(options.Qz_bins)        
