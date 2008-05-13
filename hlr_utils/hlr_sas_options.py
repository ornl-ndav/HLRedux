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

class SansOptions(hlr_utils.InstOptions):
    """
    This class provides options for the SAS class of instruments for use in
    reducing neutron scattering data with the data reduction drivers.
    """
    
    def __init__(self, usage=None, option_list=None, options_class=None,
                 version=None, conflict_handler='error', description=None,
                 **kwargs):
        """
        Constructor for C{SansOptions}

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
        hlr_utils.InstOptions.__init__(self, usage, option_list,
                                       Option, version,
                                       conflict_handler, description,
                                       inst="SAS")
        
        # Remove norm option since it is not necessary
        self.remove_option("--norm")

        self.add_option("", "--bmon-path", dest="bmon_path",
                        help="Specify the comma separated list of the beam "\
                        +"monitor path and signal.")

        self.add_option("", "--tmon-path", dest="tmon_path",
                        help="Specify the comma separated list of the "\
                        +"transmission monitor path and signal.")        

        self.add_option("", "--trans", dest="trans", help="Specify the "\
                        +"filename for a transmission spectrum. Use this "\
                        +"option in the absence of transmission monitors.")

        self.add_option("", "--mon-effc", action="store_true",
                        dest="mon_effc",
                        help="Flag for turning on monitor efficiency "\
                        +"correction")
        self.set_defaults(mon_eff=False)

        self.add_option("", "--roi-file", dest="roi_file",
                        help="Specify a file that contains a list of pixel "\
                        +"ids to be read from the data")

        self.add_option("", "--mom-trans-bins", dest="Q_bins",
                        help="Specify the minimum and maximum momentum "\
                        +"transfer values, the momentum transfer bin "\
                        +"width in Angstroms^-1 and the type (lin or log)")

        self.add_option("", "--time-zero-offset-det",
                        dest="time_zero_offset_det",
                        help="Specify the time zero offset, err^2 in "\
                        +"microseconds for the detector")

        self.add_option("", "--time-zero-offset-mon",
                        dest="time_zero_offset_mon",
                        help="Specify the time zero offset, err^2 in "\
                        +"microseconds for the monitor")        

        self.add_option("", "--lambda-bins", dest="lambda_bins",
                        help="Specify the minimum and maximum wavelength "\
                        +"values and the wavelength bin width in Angstroms")
        self.set_defaults(lambda_bins="0,10,0.1")

        self.add_option("", "--lambda-cut", dest="lambda_cut",
                        help="Specify the wavelength at which to cut the "\
                        +"spectra (Angstroms).")

        self.add_option("", "--bkg-coeff", dest="bkg_coeff",
                        help="Specify the polynomial coefficients for a "\
                        +"wavelength dependent background subtraction. The "\
                        +"should be lowest to highest: c0 + c1 * x + "\
                        +"c2 * x**2 + ...")
        
        self.add_option("", "--dump-wave", action="store_true",
                        dest="dump_wave",
                        help="Flag to dump the wavelength information for all"\
                        +" pixels. Creates a *.pxl file for each dataset.")
        self.set_defaults(dump_wave=False)
        
        self.add_option("", "--dump-bmon-wave", action="store_true",
                        dest="dump_bmon_wave",
                        help="Flag to dump the wavelength information for the"\
                        +" beam monitor. Creates a *.bmxl file for each "\
                        +"dataset.")
        self.set_defaults(dump_bmon_wave=False)    

        self.add_option("", "--dump-bmon-effc", action="store_true",
                        dest="dump_bmon_effc",
                        help="Flag to dump the wavelength information for the"\
                        +" efficiency corrected beam monitor. Creates a "\
                        +"*.bmel file for each dataset.")
        self.set_defaults(dump_bmon_effc=False)

        self.add_option("", "--dump-bmon-rebin", action="store_true",
                        dest="dump_bmon_rebin",
                        help="Flag to dump the wavelength information for the"\
                        +" rebinned beam monitor. Creates a *.bmrl file for "\
                        +"each dataset")
        self.set_defaults(dump_bmon_rebin=False)

        self.add_option("", "--dump-wave-bmnorm", action="store_true",
                        dest="dump_wave_bmnorm",
                        help="Flag to dump the combined wavelength "\
                        +"information for all pixels after beam monitor "\
                        +"normalization. Creates a *.pbml file for each "\
                        +"dataset.")
        self.set_defaults(dump_wave_bmnorm=False)

        self.add_option("", "--dump-all", action="store_true", dest="dump_all",
                        help="Flag to dump combined information")
        self.set_defaults(dump_all=False)
        
        
def SansConfiguration(parser, configure, options, args):
    """
    This function sets the incoming C{Configure} object with all the options
    that have been specified via the C{SansOptions} object.

    @param parser: The parser object
    @type parser: L{hlr_utils.SansOptions}

    @param configure: The configuration object
    @type configure: L{hlr_utils.Configure}

    @param options: The parsed options from C{SansOptions}
    @type options: C{Option}

    @param args: The parsed arguments from C{SansOptions}
    @type args: C{list}
    """

    # Call the configuration setter for InstOptions
    hlr_utils.InstConfiguration(parser, configure, options, args, inst="SAS")

    # Set the beam monitor path
    if hlr_utils.cli_provide_override(configure, "bmon_path", "--bmon-path"):
        configure.bmon_path = hlr_utils.NxPath(options.bmon_path)

    # Set the transmission monitor path
    if hlr_utils.cli_provide_override(configure, "tmon_path", "--tmon-path"):
        configure.tmon_path = hlr_utils.NxPath(options.tmon_path)        

    # Set the Transmission spectrum file
    if hlr_utils.cli_provide_override(configure, "trans", "--trans"):
        configure.trans = hlr_utils.determine_files(options.trans,
                                                    one_file=True)
    # Set mon_effc flag
    if hlr_utils.cli_provide_override(configure, "mon_effc", "--mon-effc"):
        configure.mon_effc = options.mon_effc

    # Set the ROI file
    if hlr_utils.cli_provide_override(configure, "roi_file", "--roi-file"):
        configure.roi_file = hlr_utils.determine_files(options.roi_file,
                                                       one_file=True)

    # Set the momentum transfer bins
    if hlr_utils.cli_provide_override(configure, "Q_bins", "--mom-trans-bins"):
        configure.Q_bins = hlr_utils.AxisFromString(options.Q_bins)

    # Set the time-zero offset for the detector
    if hlr_utils.cli_provide_override(configure, "time_zero_offset_det",
                                      "--time-zero-offset-det"):    
        configure.time_zero_offset_det = hlr_utils.DrParameterFromString(\
            options.time_zero_offset_det, True)

    # Set the time-zero offset for the monitor
    if hlr_utils.cli_provide_override(configure, "time_zero_offset_mon",
                                      "--time-zero-offset-mon"):    
        configure.time_zero_offset_mon = hlr_utils.DrParameterFromString(\
            options.time_zero_offset_mon, True)        

    # Set the lambda bins for use with dump-bmnorm-wave
    if hlr_utils.cli_provide_override(configure, "lambda_bins",
                                      "--lambda-bins"):    
        configure.lambda_bins = hlr_utils.AxisFromString(options.lambda_bins)

    # Set the lambda cut for cutting wavelength spectra
    if hlr_utils.cli_provide_override(configure, "lambda_cut",
                                      "--lambda-cut"):
        try:
            configure.lambda_cut = float(options.lambda_cut)
        except TypeError:
            configure.lambda_cut = options.lambda_cut

    # Set the coefficients for the wavelength dependent background correction
    if hlr_utils.cli_provide_override(configure, "bkg_coeff", "--bkg-coeff"):
        try:
            configure.bkg_coeff = options.bkg_coeff.split(',')
        except TypeError:
            configure.bkg_coeff = options.bkg_coeff
        
    # Set the ability to dump the detector pixel wavelength information
    if hlr_utils.cli_provide_override(configure, "dump_wave", "--dump-wave"):
        configure.dump_wave = options.dump_wave

    # Set the ability to dump the beam monitor wavelength information
    if hlr_utils.cli_provide_override(configure, "dump_bmon_wave",
                                      "--dump-bmon-wave"):
        configure.dump_bmon_wave = options.dump_bmon_wave    

    # Set the ability to dump the efficiency corrected beam monitor wavelength
    # information
    if hlr_utils.cli_provide_override(configure, "dump_bmon_effc",
                                      "--dump-bmon-effc"):
        configure.dump_bmon_effc = options.dump_bmon_effc

    # Set the ability to dump the rebinned beam monitor wavelength information
    if hlr_utils.cli_provide_override(configure, "dump_bmon_rebin",
                                      "--dump-bmon-rebin"):
        configure.dump_bmon_rebin = options.dump_bmon_rebin

    # Set the ability to dump the wavelength information after beam monitor
    # normalization
    if hlr_utils.cli_provide_override(configure, "dump_wave_bmnorm",
                                      "--dump-wave-bmnorm"):
        configure.dump_wave_bmnorm = options.dump_wave_bmnorm

    if hlr_utils.cli_provide_override(configure, "dump_all", "--dump-all"):
        if options.dump_all:
            configure.dump_wave = True
            configure.dump_bmon_wave = True
            configure.dump_bmon_effc = True
            configure.dump_bmon_rebin = True
            configure.dump_wave_bmnorm = True
