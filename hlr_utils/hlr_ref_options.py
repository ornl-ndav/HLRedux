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

class RefOptions(hlr_options.InstOptions):
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
        hlr_options.InstOptions.__init__(self, usage, option_list,
                                         Option, version, conflict_handler,
                                         description, inst="REF")

        # Remove inst-geom option since we'll duplicate it below
        self.remove_option("--inst-geom")

        # Add REF specific options
        self.add_option("", "--data-inst-geom", dest="data_inst_geom",
                        metavar="FILENAME",
                        help="Specify the data instrument geometry file")

        self.add_option("", "--norm-inst-geom", dest="norm_inst_geom",
                        metavar="FILENAME",
                        help="Specify the normalization instrument geometry "\
                        +"file")        
        
        self.add_option("", "--angle-offset", dest="angle_offset",
                        help="Specify the global offset for the polar angle: "\
                        +"angle, err^2, and units=<degrees or radians>")

        self.add_option("", "--data-roi-file", dest="data_roi_file",
                        help="Specify the file containing the list pixel IDs "\
                        +"for the sample data region.")
        
        self.add_option("", "--norm-roi-file", dest="norm_roi_file",
                        help="Specify the file containing the list pixel IDs "\
                        +"for the normalization data region.")

        self.add_option("", "--dbkg-roi-file", dest="dbkg_roi_file",
                        help="Specify the file containing the list pixel IDs "\
                        +"for the sample data background region.")
        
        self.add_option("", "--nbkg-roi-file", dest="nbkg_roi_file",
                        help="Specify the file containing the list pixel IDs "\
                        +"for the normalization background region.")        
        
        self.add_option("", "--no-bkg", action="store_true", dest="no_bkg",
                        help="Flag to turn off background estimation and "\
                        +"subtraction")
        self.set_defaults(no_bkg=False)

        self.add_option("", "--no-norm-bkg", action="store_true",
                        dest="no_norm_bkg",
                        help="Flag to turn off normalization background "\
                        +"estimation and subtraction")
        self.set_defaults(no_norm_bkg=False)

        self.add_option("", "--mom-trans-bins", dest="Q_bins",
                        help="Specify the minimum and maximum momentum "\
                        +"transfer values and the momentum transfer bin "\
                        +"width in Angstroms^-1")

        self.add_option("", "--tof-cuts", dest="tof_cuts",
                        help="Specify the TOF bins (comma-separated) that "\
                        +"will be zeroed out in the data and normalization "\
                        +"spectra")

        self.add_option("", "--no-filter", action="store_true",
                        dest="no_filter",
                        help="Flag to turn off bad data filtering.")
        self.set_defaults(no_filter=False)

        self.add_option("", "--store-dtot", action="store_true",
                        dest="store_dtot",
                        help="Flag to turn on storage of delta t over t in "\
                        +"TOF output file.")
        self.set_defaults(store_dtot=False)

        self.add_option("", "--data-peak-excl", dest="data_peak_excl",
                        type="int", nargs=2,
                        help="Peak exclusion range pixel IDs for sample data.")

        self.add_option("", "--norm-peak-excl", dest="norm_peak_excl",
                        type="int", nargs=2,
                        help="Peak exclusion range pixel IDs for "\
                        +"normalization data.")    

        self.add_option("", "--dump-specular", action="store_true",
                        dest="dump_specular",
                        help="Flag to dump the combined specular TOF "\
                        +"information. Creates a *.sdc file.")
        self.set_defaults(dump_specular=False)
        
        self.add_option("", "--dump-sub", action="store_true",
                        dest="dump_sub",
                        help="Flag to dump the combined subtracted TOF "\
                        +"information. Creates a *.sub file.")
        self.set_defaults(dump_sub=False)
        
        self.add_option("", "--dump-bkg", action="store_true", dest="dump_bkg",
                        help="Flag to dump the combined background TOF "\
                        +"information. Creates a *.bkg file.")
        self.set_defaults(dump_bkg=False)

        self.add_option("", "--dump-rtof", action="store_true",
                        dest="dump_rtof",
                        help="Flag to dump the R(TOF) information. Creates a "\
                        +"*.rtof file.")
        self.set_defaults(dump_rtof=False)

        self.add_option("", "--dump-rtof-comb", action="store_true",
                        dest="dump_rtof_comb",
                        help="Flag to dump the combined R(TOF) information. "\
                        +"Creates a *.crtof file.")
        self.set_defaults(dump_rtof_comb=False)        

        self.add_option("", "--dump-rq", action="store_true",
                        dest="dump_rq",
                        help="Flag to dump the R(Q) information. Creates a "\
                        +"*.rq file.")
        self.set_defaults(dump_rq=False)        

        self.add_option("", "--dump-rqr", action="store_true",
                        dest="dump_rqr",
                        help="Flag to dump the R(Q) after rebinning "\
                        +"information. Creates a *.rqr file.")
        self.set_defaults(dump_rqr=False)        

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

    # Call the configuration setter for InstOptions
    hlr_options.InstConfiguration(parser, configure, options, args, inst="REF")

    # Set the data instrument geometry file
    if hlr_utils.cli_provide_override(configure, "data_inst_geom",
                                      "--data-inst-geom"):
        configure.data_inst_geom = hlr_utils.determine_files(\
            options.data_inst_geom,
            one_file=True)

    # Set the normalization instrument geometry file
    if hlr_utils.cli_provide_override(configure, "norm_inst_geom",
                                      "--norm-inst-geom"):
        configure.norm_inst_geom = hlr_utils.determine_files(\
            options.norm_inst_geom,
            one_file=True)        

    # Get the data path for the sample data ROI file
    if hlr_utils.cli_provide_override(configure, "data_roi_file",
                                      "--data-roi-file"):
        configure.data_roi_file = hlr_utils.determine_files(\
                     options.data_roi_file,
                     one_file=True)
    
    # Get the data path for the normalization data ROI file
    if hlr_utils.cli_provide_override(configure, "norm_roi_file",
                                      "--norm-roi-file"):
        if options.norm_roi_file is not None:
            configure.norm_roi_file = hlr_utils.determine_files(\
                     options.norm_roi_file,
                     one_file=True)
        else:
            configure.norm_roi_file = configure.data_roi_file

    # Get the data path for the sample data background ROI file
    if hlr_utils.cli_provide_override(configure, "dbkg_roi_file",
                                      "--dbkg-roi-file"):
        configure.dbkg_roi_file = hlr_utils.determine_files(\
                     options.dbkg_roi_file,
                     one_file=True)
    
    # Get the data path for the normalization background ROI file
    if hlr_utils.cli_provide_override(configure, "nbkg_roi_file",
                                      "--nbkg-roi-file"):
        if options.nbkg_roi_file is not None:
            configure.nbkg_roi_file = hlr_utils.determine_files(\
                     options.nbkg_roi_file,
                     one_file=True)
        else:
            configure.nbkg_roi_file = configure.dbkg_roi_file            
    
    # Get the polar angle offset
    if hlr_utils.cli_provide_override(configure, "angle_offset",
                                      "--angle-offset"):
        configure.angle_offset = hlr_utils.DrParameterFromString(\
            options.angle_offset, True)

    # Set the ability to turn off background estimation and subtraction
    if hlr_utils.cli_provide_override(configure, "no_bkg", "--no-bkg"):    
        configure.no_bkg = options.no_bkg

    # Set the ability to turn off normalization background estimation
    # and subtraction
    if hlr_utils.cli_provide_override(configure, "no_norm_bkg",
                                      "--no-norm-bkg"):    
        configure.no_norm_bkg = options.no_norm_bkg

    # Set the TOF bins to zero out from the data and normalization spectra
    if hlr_utils.cli_provide_override(configure, "tof_cuts", "--tof-cuts"):
        if options.tof_cuts is not None:
            configure.tof_cuts = options.tof_cuts.split(',')
        else:
            configure.tof_cuts = options.tof_cuts

    # Set the momentum transfer bins
    if hlr_utils.cli_provide_override(configure, "Q_bins", "--mom-trans-bins"):
        configure.Q_bins = hlr_utils.AxisFromString(options.Q_bins)

    # Set the no bad data filter flag
    if hlr_utils.cli_provide_override(configure, "no_filter", "--no-filter"):
        configure.no_filter = options.no_filter

    # Set the store delta t over t flag
    if hlr_utils.cli_provide_override(configure, "store_dtot", "--store-dtot"):
        configure.store_dtot = options.store_dtot        

    # Set the pixel ID range values for peak exclusion from sample data
    if hlr_utils.cli_provide_override(configure, "data_peak_excl",
                                      "--data-peak-excl"):
        configure.data_peak_excl = options.data_peak_excl

    # Set the pixel ID range values for peak exclusion from normalization data
    if hlr_utils.cli_provide_override(configure, "norm_peak_excl",
                                      "--norm-peak-excl"):
        configure.norm_peak_excl = options.norm_peak_excl        

    # Set the ability to dump the combined specular TOF information
    if hlr_utils.cli_provide_override(configure, "dump_specular",
                                      "--dump-specular"): 
        configure.dump_specular = options.dump_specular

    # Set the ability to dump the combined background TOF information
    if hlr_utils.cli_provide_override(configure, "dump_bkg", "--dump-bkg"):
        configure.dump_bkg = options.dump_bkg

    # Set the ability to dump the combined subtracted TOF information
    if hlr_utils.cli_provide_override(configure, "dump_sub", "--dump-sub"):    
        configure.dump_sub = options.dump_sub

    # Set the ability to dump the R(TOF) information
    if hlr_utils.cli_provide_override(configure, "dump_rtof", "--dump-rtof"): 
        configure.dump_rtof = options.dump_rtof

    # Set the ability to dump the combined R(TOF) information
    if hlr_utils.cli_provide_override(configure, "dump_rtof_comb",
                                      "--dump-rtof-comb"): 
        configure.dump_rtof_comb = options.dump_rtof_comb        

    # Set the ability to dump the R(Q) information
    if hlr_utils.cli_provide_override(configure, "dump_rq", "--dump-rq"): 
        configure.dump_rq = options.dump_rq

    # Set the ability to dump the R(Q) after rebinning information
    if hlr_utils.cli_provide_override(configure, "dump_rqr", "--dump-rqr"): 
        configure.dump_rqr = options.dump_rqr        

    if hlr_utils.cli_provide_override(configure, "dump_all", "--dump-all"):
        if options.dump_all:
            configure.dump_specular = True
            configure.dump_bkg = True
            configure.dump_sub = True
            configure.dump_rtof = True
            configure.dump_rtof_comb = True
            configure.dump_rq = True
            configure.dump_rqr = True
