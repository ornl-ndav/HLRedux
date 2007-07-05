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

class RefOptions(hlr_options.SNSOptions):
    """
    This class provides options for the REF class of instruments for use in
    reducing neutron scattering data with the data reduction drivers.
    """

    def __init__(self, usage=None, option_list=None, options_class=None,
                 version=None, conflict_handler='error', description=None,
                 **kwargs):
        """
        Constructor for C{RefOptions}

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
                                        description, inst="REF")

        # Add REF specific options
        self.add_option("", "--det-angle", dest="det_angle",
                      help="Specify the detector inclination angle, err^2, "\
                      +"and units=<degrees or radians>")

        self.add_option("", "--signal-roi-file", dest="signal_roi_file",
                        help="Specify the file containing the list pixel IDs "\
                        +"for the signal region.")
        
        self.add_option("", "--bkg-roi-file", dest="bkg_roi_file",
                        help="Specify the file containing the list pixel IDs "\
                        +"for the background region.")
        
        self.add_option("", "--norm-signal-roi-file",
                        dest="norm_signal_roi_file",
                        help="Specify the file containing the list pixel IDs "\
                        +"for the normalization signal region.")
        
        self.add_option("", "--norm-bkg-roi-file", dest="norm_bkg_roi_file",
                        help="Specify the file containing the list pixel IDs "\
                        +"for the normalization background region.")    
        
        self.add_option("", "--combine", action="store_true", dest="combine",
                        help="Flag to combine all sample data spectra in one "\
                        +"spectrum")
        self.set_defaults(combine=False)

        self.add_option("", "--no-bkg", action="store_true", dest="no_bkg",
                        help="Flag to turn off background estimation and "\
                        +"subtraction")
        self.set_defaults(no_bkg=False)

        self.add_option("", "--no-norm-bkg", action="store_true",
                        dest="no_norm_bkg",
                        help="Flag to turn off normalization background "\
                        +"estimation and subtraction")
        self.set_defaults(no_norm_bkg=False)

        self.add_option("", "--dump-specular", action="store_true",
                        dest="dump_specular",
                        help="Flag to dump the combined specular TOF "\
                        +"information. Creates a *.sdc file.")
        self.set_defaults(dump_specular=False)
        
        self.add_option("", "--dump-norm", action="store_true",
                        dest="dump_norm",
                        help="Flag to dump the combined normalization TOF "\
                        +"information. Creates a *.nom file.")
        self.set_defaults(dump_norm=False)
        
        self.add_option("", "--dump-sub", action="store_true",
                        dest="dump_sub",
                        help="Flag to dump the combined subtracted TOF "\
                        +"information. Creates a *.sub file.")
        self.set_defaults(dump_sub=False)
        
        self.add_option("", "--dump-bkg", action="store_true", dest="dump_bkg",
                        help="Flag to dump the combined background TOF "\
                        +"information. Creates a *.bkg file.")
        self.set_defaults(dump_bkg=False)
        
        self.add_option("", "--dump-norm-bkg", action="store_true",
                        dest="dump_norm_bkg",
                        help="Flag to dump the combined normalization "\
                        +"background TOF information. Creates a *.bnm file.")
        self.set_defaults(dump_norm_bkg=False)

        self.add_option("", "--dump-all", action="store_true", dest="dump_all",
                        help="Flag to dump combined information")
        self.set_defaults(dump_all=False)
        
        
def RefConfiguration(parser, configure, options, args):
    """
    This function sets the incoming C{Configure} object with all the options
    that have been specified via the C{RefOptions} object.

    @param parser: The parser object
    @type parser: L{hlr_utils.RefOptions}
    
    @param configure: The configuration object
    @type configure: L{hlr_utils.Configure}
    
    @param options: The parsed options from C{RefOptions}
    @type options: C{Option}

    @param args: The parsed arguments from C{RefOptions}
    @type args: C{list}
    """

    # Call the configuration setter for SNSOptions
    hlr_options.SnsConfiguration(parser, configure, options, args, inst="REF")

    # Get the data path for the signal ROI file
    if hlr_utils.cli_provide_override(configure, "signal_roi_file",
                                      "--signal-roi-file"):
        configure.signal_roi_file = hlr_utils.determine_files(\
                     options.signal_roi_file,
                     one_file=True)
    
    # Get the data path for the background ROI file
    if hlr_utils.cli_provide_override(configure, "bkg_roi_file",
                                      "--bkg-roi-file"):
        configure.bkg_roi_file = hlr_utils.determine_files(\
                     options.bkg_roi_file,
                     one_file=True)
    
    # Get the data path for the normalization signal ROI file
    if hlr_utils.cli_provide_override(configure, "norm_signal_roi_file",
                                      "--norm-signal-roi-file"):
        if options.norm_signal_roi_file is not None:
            configure.norm_signal_roi_file = hlr_utils.determine_files(\
                     options.norm_signal_roi_file,
                     one_file=True)
        else:
            configure.norm_signal_roi_file = configure.signal_roi_file
    
    # Get the data path for the normalization background ROI file
    if hlr_utils.cli_provide_override(configure, "norm_bkg_roi_file",
                                      "--norm-bkg-roi-file"):
        if options.norm_bkg_roi_file is not None:
            configure.norm_bkg_roi_file = hlr_utils.determine_files(\
                     options.norm_bkg_roi_file,
                     one_file=True)
        else:
            configure.norm_bkg_roi_file = configure.bkg_roi_file

    # Get the detector angle
    if hlr_utils.cli_provide_override(configure, "det_angle", "--det-angle"):
        configure.det_angle = hlr_utils.DrParameterFromString(\
            options.det_angle, True)

    # Set the ability to turn off background estimation and subtraction
    if hlr_utils.cli_provide_override(configure, "no_bkg", "--no-bkg"):    
        configure.no_bkg = options.no_bkg

    # Set the ability to turn off normalization background estimation
    # and subtraction
    if hlr_utils.cli_provide_override(configure, "no_norm_bkg",
                                      "--no-norm-bkg"):    
        configure.no_norm_bkg = options.no_norm_bkg

    # Set the ability to combine sample data spectra into one spectrum
    if hlr_utils.cli_provide_override(configure, "combine", "--combine"):   
        configure.combine = options.combine

    # Set the ability to dump the combined specular TOF information
    if hlr_utils.cli_provide_override(configure, "specular", "--specular"): 
        configure.dump_specular = options.dump_specular

    # Set the ability to dump the combined background TOF information
    if hlr_utils.cli_provide_override(configure, "dump_bkg", "--dump-bkg"):
        configure.dump_bkg = options.dump_bkg

    # Set the ability to dump the combined normalization TOF information
    if hlr_utils.cli_provide_override(configure, "dump_norm", "--dump-norm"):
        configure.dump_norm = options.dump_norm

    # Set the ability to dump the combined subtracted TOF information
    if hlr_utils.cli_provide_override(configure, "dump_sub", "--dump-sub"):    
        configure.dump_sub = options.dump_sub

    # Set the ability to dump the combined normalization background TOF
    # information
    if hlr_utils.cli_provide_override(configure, "dump_norm_bkg",
                                      "--dump-norm-bkg"):    
        configure.dump_norm_bkg = options.dump_norm_bkg

    if hlr_utils.cli_provide_override(configure, "dump_all", "--dump-all"):
        if options.dump_all:
            configure.dump_specular = True
            configure.dump_bkg = True
            configure.dump_sub = True
            configure.dump_norm = True
            configure.dump_norm_bkg = True
            
