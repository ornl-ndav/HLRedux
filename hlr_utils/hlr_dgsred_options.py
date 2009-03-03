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
        hlr_dgs_options.DgsOptions.__init__(self, usage, option_list,
                                            Option, version, conflict_handler,
                                            description)

        self.add_option("", "--mask-file", dest="mask_file",
                        help="Specify a file that contains a list of pixel "\
                        +"ids to be excluded from the data")

        self.add_option("", "--corner-geom", dest="corner_geom",
                        help="Specify the file containing the corner "\
                        +"geometry information.")

        self.add_option("", "--lambda-ratio", action="store_true",
                        dest="lambda_ratio", help="Flag that turns on the "\
                        +"lambda ratio scaling (lambda_i/lambda_f) during "\
                        +"energy transfer conversion.")
        self.set_defaults(lambda_ratio=False)
        
        self.add_option("", "--energy-bins", dest="E_bins",
                        help="Specify the minimum and maximum energy values "\
                        +"and the energy bin width in meV")

        self.add_option("", "--mom-trans-bins", dest="Q_bins",
                        help="Specify the minimum and maximum momentum "\
                        +"transfer values and the momentum transfer bin "\
                        +"width in Angstroms^-1")

        self.add_option("-m", "--qmesh", dest="qmesh", action="store_true",
                        help="Create the Q vector meshes for each energy "\
                        +"slice.")
        self.set_defaults(qmesh=False)

        self.add_option("-x", "--fixed", action="store_true",
                        dest="fixed", help="Dump the Q vector information to "\
                        +"a fixed grid.")
        self.set_defaults(fixed=False)

        self.add_option("", "--dump-et-comb", action="store_true",
                        dest="dump_et_comb",
                        help="Flag to dump the energy transfer information "\
                        +"for all pixels combined. Creates a *.et file.")
        self.set_defaults(dump_et_comb=False)

        self.add_option("", "--split", action="store_true", dest="split",
                        help="Special flag for running driver in split mode. "\
                        +"Only necessary for parallel computing environment.")
        self.set_defaults(split=False)        

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

    # Set the mask file
    if hlr_utils.cli_provide_override(configure, "mask_file", "--mask-file"):
        configure.mask_file = hlr_utils.determine_files(options.mask_file,
                                                        one_file=True)

    # Set the corner geometry information file
    if hlr_utils.cli_provide_override(configure, "corner_geom",
                                      "--corner-geom"):
        configure.corner_geom = options.corner_geom

    if configure.corner_geom is None:
        parser.error("You must provide a corner geometry file via the "\
                     +"corner-geom option!")

    # Set the lambda ratio flag
    if hlr_utils.cli_provide_override(configure, "lambda_ratio",
                                      "--lambda-ratio"):
        configure.lambda_ratio = options.lambda_ratio

    # Set the energy transfer bins
    if hlr_utils.cli_provide_override(configure, "E_bins", "--energy-bins"):
        configure.E_bins = hlr_utils.AxisFromString(options.E_bins)

    if configure.E_bins is None:
        parser.error("You must provide energy transfer binning via the "\
                     +"energy-bins option")        

    # Set the momentum transfer bins
    if hlr_utils.cli_provide_override(configure, "Q_bins", "--mom-trans-bins"):
        configure.Q_bins = hlr_utils.AxisFromString(options.Q_bins)

    if configure.Q_bins is None:
        parser.error("You must provide momentum transfer binning via the "\
                     +"mom-trans-bins option")

    # Set the ability to create the Q vector meshes for each energy slice
    if hlr_utils.cli_provide_override(configure, "qmesh", "--qmesh", "m"):
        configure.qmesh = options.qmesh
        
    # Set the ability to write out fixed grid mesh files
    if hlr_utils.cli_provide_override(configure, "fixed", "--fixed", "x"):
        configure.fixed = options.fixed        

    # Set the ability to dump the combined energy transfer information
    if hlr_utils.cli_provide_override(configure, "dump_et_comb",
                                      "--dump-et-comb"):
        configure.dump_et_comb = options.dump_et_comb        

    if hlr_utils.cli_provide_override(configure, "split", "--split"):
        configure.split = options.split
