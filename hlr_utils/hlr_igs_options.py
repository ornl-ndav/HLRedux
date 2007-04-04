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

class IgsOptions(hlr_options.SNSOptions):
    """
    This class provides options for the IGS class of instruments for use in
    reducing neutron scattering data with the data reduction drivers.
    """

    def __init__(self, usage=None, option_list=None, version=None, **kwargs):
        """
        Constructor for IgsOptions

        Parameters:
        ----------
        -> usage (OPTIONAL) is a string that will print the correct usage of
                 program in which the option class is used
        -> option_list (OPTIONAL) is a list containing the alternative method
                       of providing options
        -> kwargs is a list of keyword arguments that the function accepts
        """
        # parent constructor
        hlr_options.SNSOptions.__init__(self, usage, option_list,
                                        Option, version, inst="IGS")

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
                        +"information for all pixels")
        self.set_defaults(dump_tib=False)
        
        self.add_option("", "--dump-wave", action="store_true",
                        dest="dump_wave",
                        help="Flag to dump the wavelength information for all"\
                        +" pixels")
        self.set_defaults(dump_wave=False)
        
        self.add_option("", "--dump-mon-wave", action="store_true",
                        dest="dump_mon_wave",
                        help="Flag to dump the wavelength information for the"\
                        +" monitor")
        self.set_defaults(dump_mon_wave=False)    

        self.add_option("", "--dump-mon-rebin", action="store_true",
                        dest="dump_mon_rebin",
                        help="Flag to dump the wavelength information for the"\
                        +" rebinned monitor")
        self.set_defaults(dump_mon_rebin=False)

        self.add_option("", "--dump-mon-effc", action="store_true",
                        dest="dump_mon_effc",
                        help="Flag to dump the wavelength information for the"\
                        +" efficiency corrected monitor")
        self.set_defaults(dump_mon_rebin=False)            
        
        self.add_option("", "--dump-wave-mnorm", action="store_true",
                        dest="dump_wave_mnorm",
                        help="Flag to dump the combined wavelength "\
                        +"information for all pixels after monitor "\
                        +"normalization")
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
        
        self.add_option("", "--timing", action="store_true", dest="timing",
                        help="Flag to turn on timing of code")
        self.set_defaults(timing=False)
        
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
