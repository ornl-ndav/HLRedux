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

        self.add_option("", "--roi-file", dest="roi_file",
                        help="Specify a file that contains a list of pixel "\
                        +"ids to be read from the data")

        self.add_option("", "--initial-energy", dest="initial_energy",
                        help="Specify the initial energy, err^2 for the "\
                        +"reduction in units of meV")

        self.add_option("", "--time-zero-offset", dest="time_zero_offset",
                        help="Specify the time-zero offset, err^2 in units "\
                        +"of microseconds")

        self.add_option("", "--no-mon-norm", action="store_true",
                        dest="no_mon_norm",
                        help="Flag for turning off monitor normalization")

        self.add_option("", "--pc-norm", action="store_true", dest="pc_norm",
                        help="Flag for performing proton charge "\
                        +"normalization. This will only be done if monitor "\
                        +"normalization is turned off.")

        self.add_option("", "--mon-int-range", dest="mon_int_range",
                        type="float", nargs=2, help="Set the minimum and "\
                        +"maximum values in TOF [microseconds] for the "\
                        +"integration of the monitor.")

        self.add_option("", "--det-eff", dest="det_eff",
                        help="Specify the detector efficiency file or an "\
                        +"efficiency tuple (efficiency,error2)")
                        
        self.add_option("", "--data-trans-coeff", dest="data_trans_coeff",
                        help="Specify the transmission coefficient value and "\
                        +"err^2 for the sample data background.")
        
        self.add_option("", "--norm-trans-coeff", dest="norm_trans_coeff",
                        help="Specify the transmission coefficient value and "\
                        +"err^2 for the normalization data background.")

        self.add_option("", "--corner-geom", dest="corner_geom",
                        help="Specify the file containing the corner "\
                        +"geometry information.")

        self.add_option("", "--lambda-ratio", action="store_true",
                        dest="lambda_ratio", help="Flag that turns on the "\
                        +"lambda ratio scaling (lambda_i/lambda_f) during "\
                        +"energy transfer conversion.")

        self.add_option("", "--lambda-bins", dest="lambda_bins",
                        help="Specify the minimum and maximum wavelength "\
                        +"values and the wavelength bin width in Angstroms")
        self.set_defaults(lambda_bins="0.0,10.0,0.1")

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

        self.add_option("", "--dump-wave-comb", action="store_true",
                        dest="dump_wave_comb",
                        help="Flag to dump the wavelength information for all"\
                        +" pixels combined. Creates a *.fwv file.")
        self.set_defaults(dump_wave_comb=False)

        self.add_option("", "--dump-et-comb", action="store_true",
                        dest="dump_et_comb",
                        help="Flag to dump the energy transfer information "\
                        +"for all pixels combined. Creates a *.et file.")
        self.set_defaults(dump_et_comb=False)        

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

    # Set the ROI file
    if hlr_utils.cli_provide_override(configure, "roi_file", "--roi-file"):
        configure.roi_file = hlr_utils.determine_files(options.roi_file,
                                                       one_file=True)

    # Set the initial energy
    if hlr_utils.cli_provide_override(configure, "initial_energy",
                                      "--initial-energy"):
        configure.initial_energy = hlr_utils.DrParameterFromString(\
            options.initial_energy, True)

    # Set the time-zero offset
    if hlr_utils.cli_provide_override(configure, "time_zero_offset",
                                      "--time-zero-offset"):    
        configure.time_zero_offset = hlr_utils.DrParameterFromString(\
            options.time_zero_offset, True)

    # Set no_mon_norm flag
    if hlr_utils.cli_provide_override(configure, "no_mon_norm",
                                      "--no-mon-norm"):
        configure.no_mon_norm = options.no_mon_norm

    # Set proton charge normalization flag
    if hlr_utils.cli_provide_override(configure, "pc_norm",
                                      "--pc-norm"):
        configure.pc_norm = options.pc_norm        

    # Set the TOF range for the monitor integration
    if hlr_utils.cli_provide_override(configure, "mon_int_range",
                                      "--mon-int-range"):
        configure.mon_int_range = options.mon_int_range

    # Set the detector efficiency. This can be a tuple (one number for all
    # pixels) or a file containing numbers for all pixels.
    if hlr_utils.cli_provide_override(configure, "det_eff", "--det-eff"):
        try:
            configure.det_eff = hlr_utils.DrParameterFromString(\
                options.det_eff, True)
        except RuntimeError:
            configure.det_eff = hlr_utils.determine_files(options.det_eff,
                                                          one_file=True)
            
    # Set the transmission coefficient for the sample data background
    if hlr_utils.cli_provide_override(configure, "data_trans_coeff",
                                      "--data-trans-coeff"):
        configure.data_trans_coeff = hlr_utils.DrParameterFromString(\
            options.data_trans_coeff, True)

    # Set the transmission coefficient for the normalization background
    if hlr_utils.cli_provide_override(configure, "norm_trans_coeff",
                                      "--norm-trans-coeff"):
        configure.norm_trans_coeff = hlr_utils.DrParameterFromString(\
            options.norm_trans_coeff, True)        

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

    # Set the x-component of the momentum transfer bins
    if hlr_utils.cli_provide_override(configure, "Qx_bins", "--qx-bins"):
        configure.Qx_bins = hlr_utils.AxisFromString(options.Qx_bins)

    # Set the y-component of the momentum transfer bins
    if hlr_utils.cli_provide_override(configure, "Qy_bins", "--qy-bins"):
        configure.Qy_bins = hlr_utils.AxisFromString(options.Qy_bins)

    # Set the z-component of the momentum transfer bins
    if hlr_utils.cli_provide_override(configure, "Qz_bins", "--qz-bins"):
        configure.Qz_bins = hlr_utils.AxisFromString(options.Qz_bins)        
        
    # Set the wavelength bins
    if hlr_utils.cli_provide_override(configure, "lambda_bins",
                                      "--lambda-bins"):
        configure.lambda_bins = hlr_utils.AxisFromString(options.lambda_bins)

    # Set the ability to dump the combined final wavelength information
    if hlr_utils.cli_provide_override(configure, "dump_wave_comb",
                                      "--dump-wave-comb"):
        configure.dump_wave_comb = options.dump_wave_comb

    # Set the ability to dump the combined energy transfer information
    if hlr_utils.cli_provide_override(configure, "dump_et_comb",
                                      "--dump-et-comb"):
        configure.dump_et_comb = options.dump_et_comb        
