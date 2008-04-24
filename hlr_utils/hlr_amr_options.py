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
import hlr_igs_options
import hlr_utils

class AmrOptions(hlr_igs_options.IgsOptions):
    """
    This class provides options for the IGS amorphous_reduction driver.
    """

    def __init__(self, usage=None, option_list=None, version=None,
                 conflict_handler='error', description=None, **kwargs):
        """
        Constructor for C{AmrOptions}

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
        hlr_igs_options.IgsOptions.__init__(self, usage, option_list,
                                            Option, version, conflict_handler,
                                            description)

        # Add amorphous_reduction specific options
        self.add_option("", "--mon-eff", dest="mon_eff", metavar="TUPLE",
                        help="Specify the monitor efficiency file or an "\
                        +"efficiency tuple (efficiency,error2)")
        
        self.add_option("", "--det-eff", dest="det_eff",
                        help="Specify the detector efficiency file or an "\
                        +"efficiency tuple (efficiency,error2)")
        
        self.add_option("", "--energy-bins", dest="E_bins",
                        help="Specify the minimum and maximum energy values "\
                        +"and the energy bin width in ueV")
        
        self.add_option("", "--mom-trans-bins", dest="Q_bins",
                        help="Specify the minimum and maximum momentum "\
                        +"transfer values and the momentum transfer bin "\
                        +"width in Angstroms^-1")

        self.add_option("", "--rescale-final", dest="rescale_final",
                        help="Specify the constant with which to scale the "\
                        +"final data.")

        self.add_option("", "--dump-dslin", action="store_true",
                        dest="dump_dslin",
                        help="Flag to dump the linearly interpolated direct "\
                        +"scattering background information summed over "\
                        +"all pixels. Creates a *.lin file.")
        self.set_defaults(dump_dslin=False)
        
        self.add_option("", "--dump-energy", action="store_true",
                        dest="dump_energy",
                        help="Flag to dump the energy transfer information "\
                        +"for all pixels. Creates a *.exl file.")
        self.set_defaults(dump_energy=False)
        
        self.add_option("", "--dump-ei", action="store_true",
                        dest="dump_initial_energy",
                        help="Flag to dump the initial energy information for"\
                        +" all pixels. Creates a *.ixl file.")
        self.set_defaults(dump_ei=False)

        self.add_option("", "--split", action="store_true", dest="split",
                        help="Special flag for running driver in split mode. "\
                        +"Only necessary for parallel computing environment.")
        self.set_defaults(split=False)
        
def AmrConfiguration(parser, configure, options, args):
    """
    This function sets the incoming C{Configure} object with all the options
    that have been specified via the C{AmrOptions} object.

    @param parser: The parser object
    @type parser: L{hlr_utils.AmrOptions}
    
    @param configure: The configuration object
    @type configure: L{hlr_utils.Configure}
    
    @param options: The parsed options from C{AmrOptions}
    @type options: C{Option}

    @param args: The parsed arguments from C{AmrOptions}
    @type args: C{list}
    """

    # Call the configuration setter for IgsOptions
    hlr_igs_options.IgsConfiguration(parser, configure, options, args)
 
    # Set the monitor efficiency (tuple)
    if hlr_utils.cli_provide_override(configure, "mon_eff", "--mon-eff"): 
        configure.mon_eff = hlr_utils.DrParameterFromString(options.mon_eff,
                                                            True)

    # Set the detector efficiency. This can be a tuple (one number for all
    # pixels) or a file containing numbers for all pixels.
    if hlr_utils.cli_provide_override(configure, "det_eff", "--det-eff"):
        try:
            configure.det_eff = hlr_utils.DrParameterFromString(\
                options.det_eff, True)
        except ValueError:
            configure.det_eff = hlr_utils.determine_files(options.det_eff,
                                                          one_file=True)
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
        parser.error("You must provide Q binning via the mom-trans-bins "\
                     +"option")

    # Set the final data rescaling constant
    if hlr_utils.cli_provide_override(configure, "rescale_final",
                                      "--rescale-final"):
        try:
            configure.rescale_final = float(options.rescale_final)
        except TypeError:
            configure.rescale_final = options.rescale_final

    # Set the ability to dump the energy transfer information
    if hlr_utils.cli_provide_override(configure, "dump_dslin",
                                      "--dump-dslin"):
        configure.dump_dslin = options.dump_dslin
        
    # Set the ability to dump the energy transfer information
    if hlr_utils.cli_provide_override(configure, "dump_energy",
                                      "--dump-energy"):
        configure.dump_energy = options.dump_energy
    
    # Set the ability to dump the initial energy information
    if hlr_utils.cli_provide_override(configure, "dump_initial_energy",
                                      "--dump-initial-energy"):    
        configure.dump_initial_energy = options.dump_initial_energy

    if hlr_utils.cli_provide_override(configure, "dump_all", "--dump-all"):
        if options.dump_all:
            configure.dump_dslin = True
            configure.dump_energy = True
            configure.dump_initial_energy = True

    if hlr_utils.cli_provide_override(configure, "split", "--split"):
        configure.split = options.split
