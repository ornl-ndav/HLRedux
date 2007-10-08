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

"""
This module contains functions that represent higher-level aggregations of
data reduction functionality.
"""

from hlr_add_files import *
from hlr_calc_deltat_over_t import *
from hlr_calc_delta_theta_over_theta import *
from hlr_calculate_ref_background import *
from hlr_create_axis_from_data import *
from hlr_create_E_vs_Q_igs import create_E_vs_Q_igs
from hlr_convert_single_to_list import *
from hlr_create_X_vs_pixpos import *
from hlr_determine_time_indep_bkg import *
from hlr_determine_ref_background import *
from hlr_feff_correct_mon import *
from hlr_filter_ref_data import *
from hlr_igs_energy_transfer import *
from hlr_integrate_axis import *
from hlr_integrate_spectra import *
from hlr_lin_interpolate_spectra import *
from hlr_process_igs_data import process_igs_data
from hlr_process_ref_data import process_ref_data
from hlr_rebin_efficiency import *
from hlr_rebin_monitor import *
from hlr_subtract_bkg_from_data import *
from hlr_subtract_time_indep_bkg import *
from hlr_sum_all_spectra import *
from hlr_zero_bins import *
from hlr_zero_spectra import *

from HLR_version import version as __version__

#version
__id__ = "$Id$"
