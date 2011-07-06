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
import hlr_ref_options
import hlr_utils

class SmhrOptions(hlr_ref_options.RefOptions):
    """
    This class provides options for the REF specmh_reduction driver.
    """

    def __init__(self, usage=None, option_list=None, options_class=None,
                 version=None, conflict_handler='error', description=None,
                 **kwargs):
        """
        Constructor for C{SmhrOptions}

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
        hlr_ref_options.RefOptions.__init__(self, usage, option_list,
                                            Option, version, conflict_handler,
                                            description)        

        self.add_option("", "--beamdiv-corr", dest="beamdiv_corr",
                        action="store_true", help="Flag to turn on the beam "\
                        +"divergence correction.")
        self.set_defaults(beamdiv_corr=False)

        self.add_option("", "--det-spat-res", dest="det_spat_res", type="float",
                        nargs=1, help="Specify the detector spatial "\
                        +"resolution (mm).")

        self.add_option("", "--center-pix", dest="center_pix", type="float",
                        nargs=1, help="Specify the center pixel.")

        self.add_option("", "--num-bins-clean", dest="num_bins_clean",
                        type="int", nargs=1, help="Specify the number of "\
                        +"extra bins to clean from the cuts.")
        self.set_defaults(num_bins_clean=0)

        self.add_option("", "--cuts-in-Q", dest="cuts_in_Q",
                        action="store_true", help="Flag to pass Q cuts via "\
                        +"the TOF cuts flag.")
        self.set_defaults(cuts_in_Q=False)

        self.add_option("", "--theta-vals", dest="theta_vals", help="A list "\
                        +"of scattering angles for the incoming data.")

        self.add_option("", "--theta-vals-units", dest="theta_vals_units",
                        help="The units for the scattering angle value list.")

def SmhrConfiguration(parser, configure, options, args):
    """
    This function sets the incoming C{Configure} object with all the options
    that have been specified via the C{SmhrOptions} object.

    @param parser: The parser object
    @type parser: L{hlr_utils.SmhrOptions}
    
    @param configure: The configuration object
    @type configure: L{hlr_utils.Configure}
    
    @param options: The parsed options from C{SmhrOptions}
    @type options: C{Option}

    @param args: The parsed arguments from C{SmhrOptions}
    @type args: C{list}
    """

    # Call the configuration setter for RefOptions
    hlr_ref_options.RefConfiguration(parser, configure, options, args)

    # Set the beam divergence calculation flag
    if hlr_utils.cli_provide_override(configure, "beamdiv_corr",
                                      "--beamdiv-corr"):
        configure.beamdiv_corr = options.beamdiv_corr

    # Set the detector spatial resolution
    if hlr_utils.cli_provide_override(configure, "det_spat_res",
                                      "--det-spat-res"):
        if options.det_spat_res is None:
            configure.det_spat_res = options.det_spat_res
        else:
            # Set this to half its values for the acceptance polygon
            # and convert units to meters
            configure.det_spat_res = 0.5 * options.det_spat_res * 1.0e-3

    # Set the center pixel for the beam divergence calculation
    if hlr_utils.cli_provide_override(configure, "center_pix", "--center-pix"):
        configure.center_pix = options.center_pix

    # Set the number of bins to clean from a cut spectra
    if hlr_utils.cli_provide_override(configure, "num_bins_clean",
                                      "--num-bins-clean"):
        configure.num_bins_clean = options.num_bins_clean

    # Set the flag for passing Q cuts via the TOF cut options
    if hlr_utils.cli_provide_override(configure, "cuts_in_Q", "--cuts-in-Q"):
        configure.cuts_in_Q = options.cuts_in_Q

    # Set the scattering angle value list
    if hlr_utils.cli_provide_override(configure, "theta_vals", "--theta-vals"):
        configure.theta_vals = options.theta_vals

    # Set the units for the scattering angle list
    if hlr_utils.cli_provide_override(configure, "theta_vals_units",
                                      "--theta-vals-units"):
        configure.theta_vals_units = options.theta_vals_units
    
    if configure.theta_vals is not None and configure.theta_vals_units is None:
        parser.error("The scattering angle list units must be provided!")
        
    if configure.theta_vals is not None and configure.scatt_angle is not None:
        parser.error("Please specify a single scattering angle or a list of "\
                     +"scattering angles.")
