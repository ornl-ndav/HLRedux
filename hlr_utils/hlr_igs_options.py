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

class IgsOptions(hlr_options.SNSOptions):
    """
    This class provides options for the IGS class of instruments for use in
    reducing neutron scattering data with the data reduction drivers.
    """

    def __init__(self, usage=None, option_list=None, options_class=None,
                 version=None, conflict_handler='error', description=None,
                 **kwargs):
        """
        Constructor for C{IgsOptions}

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
        hlr_options.SNSOptions.__init__(self, usage, option_list,
                                        Option, version, conflict_handler,
                                        description, inst="IGS")

        self.add_option("", "--dead-time", dest="dead_time",
                        help="Dead time with units (no spaces)")
        
        self.add_option("", "--tib-tofs", dest="tib_tofs",
                        help="Specify four TOF values bin for "\
                        +"time-independent background estimation")

        self.add_option("", "--tib-data-const", dest="tib_data_const",
                        help="Specify constant to subtract from sample data "\
                        +"spectra: value, err^2")
        
        self.add_option("", "--tib-ecan-const", dest="tib_ecan_const",
                        help="Specify constant to subtract from empty can "\
                        +"spectra: value, err^2")

        self.add_option("", "--tib-back-const", dest="tib_back_const",
                        help="Specify constant to subtract from background "\
                        +"spectra: value, err^2")

        self.add_option("", "--tib-norm-const", dest="tib_norm_const",
                        help="Specify constant to subtract from "\
                        +"normalization spectra: value, err^2")        

        self.add_option("", "--tib-dsback-const", dest="tib_dsback_const",
                        help="Specify constant to subtract from direct "\
                        +"scattering background spectra: value, err^2")
        
        self.add_option("", "--no-mon-norm", action="store_true",
                        dest="no_mon_norm",
                        help="Flag for turning off monitor normalization")

        self.add_option("", "--no-mon-effc", action="store_true",
                        dest="no_mon_effc",
                        help="Flag for turning off monitor efficiency "\
                        +"correction")

        self.add_option("", "--norm-start", dest="norm_start",
                        help="Specify the starting wavelength for "\
                        +"normalization integration")
        
        self.add_option("", "--norm-end", dest="norm_end",
                        help="Specify the ending wavelength for "\
                        +"normalization integration")
        
        self.add_option("", "--final-wavelength", dest="wavelength_final",
                        help="Specify the final wavelength lambda, err^2 in "\
                        +"Angstroms")

        self.add_option("", "--dump-tib", action="store_true",
                        dest="dump_tib",
                        help="Flag to dump the time-independent background "\
                        +"information for all pixels. Creates a *.tib file "\
                        +"for each dataset.")
        self.set_defaults(dump_tib=False)
        
        self.add_option("", "--dump-wave", action="store_true",
                        dest="dump_wave",
                        help="Flag to dump the wavelength information for all"\
                        +" pixels. Creates a *.pxl file for each dataset.")
        self.set_defaults(dump_wave=False)
        
        self.add_option("", "--dump-mon-wave", action="store_true",
                        dest="dump_mon_wave",
                        help="Flag to dump the wavelength information for the"\
                        +" monitor. Creates a *.mxl file for each dataset.")
        self.set_defaults(dump_mon_wave=False)    

        self.add_option("", "--dump-mon-rebin", action="store_true",
                        dest="dump_mon_rebin",
                        help="Flag to dump the wavelength information for the"\
                        +" rebinned monitor. Creates a *.mrl file for each "\
                        +"dataset")
        self.set_defaults(dump_mon_rebin=False)

        self.add_option("", "--dump-mon-effc", action="store_true",
                        dest="dump_mon_effc",
                        help="Flag to dump the wavelength information for the"\
                        +" efficiency corrected monitor. Creates a *.mel "\
                        +"file for each dataset.")
        self.set_defaults(dump_mon_effc=False)

        self.add_option("", "--dump-wave-mnorm", action="store_true",
                        dest="dump_wave_mnorm",
                        help="Flag to dump the combined wavelength "\
                        +"information for all pixels after monitor "\
                        +"normalization. Creates a *.pml file for each "\
                        +"dataset.")
        self.set_defaults(dump_wave_mnorm=False)
 
        self.add_option("", "--mon-path", dest="mon_path",
                        help="Specify the comma separated list of monitor "\
                        +"path and signal.")
        
        self.add_option("", "--dump-all", action="store_true", dest="dump_all",
                        help="Flag to dump various intermediate files")
        self.set_defaults(dump_all=False)
        
        self.add_option("", "--no-filter", action="store_false", dest="filter",
                        help="Flag to turn off negative wavelength filtering.")
        
        self.add_option("", "--filter", action="store_true", dest="filter",
                        help="Flag to turn on negative wavelength filtering. "\
                        +"This is the default operation.")   
        self.set_defaults(filter=True)
        
        self.add_option("", "--roi-file", dest="roi_file",
                        help="Specify a file that contains a list of pixel "\
                        +"ids to be read from the data")
        
        self.add_option("", "--time-zero-offset", dest="time_zero_offset",
                        help="Specify the time zero offset, err^2 in "\
                        +"microseconds")
        
        self.add_option("", "--time-zero-slope", dest="time_zero_slope",
                        help="Specify the time zero slope, err^2 in "\
                        +"microseconds")
        
        self.add_option("", "--mc", action="store_true", dest="mc",
                        help="Flag to turn on MC reading")
        self.set_defaults(mc=False)

        self.add_option("", "--lambda-bins", dest="lambda_bins",
                        help="Specify the minimum and maximum wavelength "\
                        +"values and the wavelength bin width in Angstroms")
        self.set_defaults(lambda_bins="0,10,0.1")

        self.add_option("", "--hwfix", action="store_true", dest="hwfix",
                        help="Flag to turn on early background subtraction "\
                        +"using background datasets scaled by proton charge "\
                        +"ratio.")
        self.set_defaults(hwfix=False)
                        
        self.add_option("", "--scale-bs", dest="scale_bs",
                        help="Specify constant to scale the background "
                        +"spectra for subtraction from the sample data "\
                        +"spectra: value, err^2")

        self.add_option("", "--scale-bn", dest="scale_bn",
                        help="Specify constant to scale the background "\
                        +"spectra for subtraction from the normalization "\
                        +"data spectra: value, err^2")

        self.add_option("", "--scale-bcs", dest="scale_bcs",
                        help="Specify constant to scale the background "\
                        +"spectra for subtraction from the sample data "\
                        +"associated empty container spectra: value, err^2")

        self.add_option("", "--scale-bcn", dest="scale_bcn",
                        help="Specify constant to scale the background "\
                        +"spectra for subtraction from the normalization "\
                        +"data associated empty container spectra: value, "\
                        +"err^2")

        self.add_option("", "--scale-cs", dest="scale_cs",
                        help="Specify constant to scale the empty container "\
                        +"spectra for subtraction from the sample data "\
                        +"spectra: value, err^2")

        self.add_option("", "--scale-cn", dest="scale_cn",
                        help="Specify constant to scale the empty container "\
                        +"spectra for subtraction from the normalization "\
                        +"data spectra: value, err^2")

        self.add_option("", "--tof-elastic", dest="tof_elastic",
                        help="Specify the low and high TOF values that "\
                        +"bracket the elastic peak")

def IgsConfiguration(parser, configure, options, args):
    """
    This function sets the incoming C{Configure} object with all the options
    that have been specified via the C{IgsOptions} object.

    @param parser: The parser object
    @type parser: L{hlr_utils.IgsOptions}
    
    @param configure: The configuration object
    @type configure: L{hlr_utils.Configure}
    
    @param options: The parsed options from C{IgsOptions}
    @type options: C{Option}

    @param args: The parsed arguments from C{IgsOptions}
    @type args: C{list}
    """

    # Call the configuration setter for SNSOptions
    hlr_options.SnsConfiguration(parser, configure, options, args, inst="IGS")

    # Set the ROI file
    if hlr_utils.cli_provide_override(configure, "roi_file", "--roi-file"):
        configure.roi_file = hlr_utils.determine_files(options.roi_file,
                                                       one_file=True)

    # Set the monitor path
    if hlr_utils.cli_provide_override(configure, "mon_path", "--mon-path"):
        configure.mon_path = hlr_utils.NxPath(options.mon_path)

    # Set the dead time
    if hlr_utils.cli_provide_override(configure, "dead_time", "--dead-time"):
        configure.dead_time = hlr_utils.DrParameterFromString(\
            options.dead_time)

    # Set the time-independent background TOFs
    if hlr_utils.cli_provide_override(configure, "tib_tofs", "--tib-tofs"):
        if options.tib_tofs is not None:
            configure.tib_tofs = options.tib_tofs.split(',')
        else:
            configure.tib_tofs = options.tib_tofs

    # Set the time-independent background constant for data
    if hlr_utils.cli_provide_override(configure, "tib_data_const",
                                      "--tib-data-const"):
        configure.tib_data_const = hlr_utils.DrParameterFromString(\
                    options.tib_data_const, True)

    # Set the time-independent background constant for ecan
    if hlr_utils.cli_provide_override(configure, "tib_ecan_const",
                                      "--tib-ecan-const"):
        configure.tib_ecan_const = hlr_utils.DrParameterFromString(\
                    options.tib_ecan_const, True)

    # Set the time-independent background constant for back
    if hlr_utils.cli_provide_override(configure, "tib_back_const",
                                      "--tib-back-const"):    
        configure.tib_back_const = hlr_utils.DrParameterFromString(\
                    options.tib_back_const, True)

    # Set the time-independent background constant for norm
    if hlr_utils.cli_provide_override(configure, "tib_norm_const",
                                      "--tib-norm-const"):    
        configure.tib_norm_const = hlr_utils.DrParameterFromString(\
                    options.tib_norm_const, True)

    # Set the time-independent background constant for dsback
    if hlr_utils.cli_provide_override(configure, "tib_dsback_const",
                                      "--tib-dsback-const"):    
        configure.tib_dsback_const = hlr_utils.DrParameterFromString(\
                    options.tib_dsback_const, True)

    # Set the normalization start wavelength
    if hlr_utils.cli_provide_override(configure, "norm_start", "--norm_start"):
        configure.norm_start = float(options.norm_start)

    # Set the normalization end wavelength 
    if hlr_utils.cli_provide_override(configure, "norm_end", "--norm_end"):
        configure.norm_end = float(options.norm_end)

    # Set no_mon_norm flag
    if hlr_utils.cli_provide_override(configure, "no_mon_norm",
                                      "--no-mon-norm"):
        configure.no_mon_norm = options.no_mon_norm

    # Set no_mon_effc flag
    if hlr_utils.cli_provide_override(configure, "no_mon_effc",
                                      "--no-mon-effc"):
        configure.no_mon_effc = options.no_mon_effc

    # Set the final wavelength
    if hlr_utils.cli_provide_override(configure, "wavelength_final",
                                      "--wavelength-final"):    
        configure.wavelength_final = hlr_utils.DrParameterFromString(\
            options.wavelength_final, True)

    # Set the time-zero offset
    if hlr_utils.cli_provide_override(configure, "time_zero_offset",
                                      "--time-zero-offset"):    
        configure.time_zero_offset = hlr_utils.DrParameterFromString(\
            options.time_zero_offset, True)

    # Set the time-zero slope
    if hlr_utils.cli_provide_override(configure, "time_zero_slope",
                                      "--time-zero-slope"):    
        configure.time_zero_slope = hlr_utils.DrParameterFromString(\
            options.time_zero_slope, True)

    # Set the lambda bins for use with dump-mnorm-wave
    if hlr_utils.cli_provide_override(configure, "lambda_bins",
                                      "--lambda-bins"):    
        configure.lambda_bins = hlr_utils.AxisFromString(options.lambda_bins)

    # Set the ability to dump the time-independent background information
    if hlr_utils.cli_provide_override(configure, "dump_tib", "--dump-tib"): 
        configure.dump_tib = options.dump_tib

    # Set the ability to dump the wavelength information
    if hlr_utils.cli_provide_override(configure, "dump_wave", "--dump-wave"):
        configure.dump_wave = options.dump_wave

    # Set the ability to dump the monitor wavelength information
    if hlr_utils.cli_provide_override(configure, "dump_mon_wave",
                                      "--dump-mon-wave"):
        configure.dump_mon_wave = options.dump_mon_wave    

    # Set the ability to dump the rebinned monitor wavelength information
    if hlr_utils.cli_provide_override(configure, "dump_mon_rebin",
                                      "--dump-mon-rebin"):
        configure.dump_mon_rebin = options.dump_mon_rebin

    # Set the ability to dump the efficiency corrected monitor wavelength
    # information
    if hlr_utils.cli_provide_override(configure, "dump_mon_effc",
                                      "--dump-mon-effc"):
        configure.dump_mon_effc = options.dump_mon_effc

    # Set the ability to dump the wavelength information
    if hlr_utils.cli_provide_override(configure, "dump_wave_mnorm",
                                      "--dump-wave-mnorm"):
        configure.dump_wave_mnorm = options.dump_wave_mnorm

    if hlr_utils.cli_provide_override(configure, "dump_all", "--dump-all"):
        if options.dump_all:
            configure.dump_tib = True
            configure.dump_wave = True
            configure.dump_mon_wave = True
            configure.dump_mon_wave = True
            configure.dump_mon_effc = True
            configure.dump_mon_diml = True
            configure.dump_mon_rebin = True
            configure.dump_wave_mnorm = True        

    # Set the filter option
    if hlr_utils.cli_provide_override(configure, "filter", "--filter",
                                      "--no-filter"):    
        configure.filter = options.filter

    # Set MC option
    if hlr_utils.cli_provide_override(configure, "mc", "--mc"):
        configure.mc = options.mc

    # Set the early background subtraction option
    if hlr_utils.cli_provide_override(configure, "hwfix", "--hwfix"):
        configure.hwfix = options.hwfix        
    
    # Set the constant for scaling the background spectra: sample 
    if hlr_utils.cli_provide_override(configure, "scale_bs", "--scale-bs"):
        configure.scale_bs = hlr_utils.DrParameterFromString(options.scale_bs,
                                                             True)

    # Set the constant for scaling the background spectra: normalization
    if hlr_utils.cli_provide_override(configure, "scale_bn", "--scale-bn"):
        configure.scale_bn = hlr_utils.DrParameterFromString(options.scale_bn,
                                                             True)

    # Set the constant for scaling the background spectra: empty container
    # for sample 
    if hlr_utils.cli_provide_override(configure, "scale_bcs", "--scale-bcs"):
        configure.scale_bcs = hlr_utils.DrParameterFromString(\
            options.scale_bcs, True)

    # Set the constant for scaling the background spectra: empty container
    # for normalization
    if hlr_utils.cli_provide_override(configure, "scale_bcn", "--scale-bcn"):
        configure.scale_bcn = hlr_utils.DrParameterFromString(\
            options.scale_bcn, True)

    # Set the constant for scaling the empty container spectra: sample 
    if hlr_utils.cli_provide_override(configure, "scale_cs", "--scale-cs"):
        configure.scale_cs = hlr_utils.DrParameterFromString(options.scale_cs,
                                                             True)

    # Set the constant for scaling the empty container spectra: normalization
    if hlr_utils.cli_provide_override(configure, "scale_cn", "--scale-cn"):
        configure.scale_cn = hlr_utils.DrParameterFromString(options.scale_cn,
                                                             True)

    # Set the elastic peak range in TOF
    if hlr_utils.cli_provide_override(configure, "tof_elastic",
                                      "--tof-elastic"):
        if options.tof_elastic is not None:
            configure.tof_elastic = options.tof_elastic.split(',')
        else:
            configure.tof_elastic = options.tof_elastic
