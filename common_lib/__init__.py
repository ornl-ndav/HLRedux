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
This module contains HLRedux representations of functions found in the
U{SCL<neutrons.ornl.gov/asg/projects/SCL>}.
"""

from hlr_add_ncerr import *
from hlr_div_ncerr import *
from hlr_d_spacing_to_tof_focused_det import *
from hlr_energy_to_wavelength import *
from hlr_energy_transfer import *
from hlr_frequency_to_energy import *
from hlr_init_scatt_wavevector_to_scalar_Q import *
from hlr_mult_ncerr import *
from hlr_rebin_axis_1D import *
from hlr_rebin_axis_1D_linint import *
from hlr_rebin_axis_2D import *
from hlr_reverse_array_cp import *
from hlr_sub_ncerr import *
from hlr_sumw_ncerr import *
from hlr_tof_to_initial_wavelength_igs import *
from hlr_tof_to_initial_wavelength_igs_lin_time_zero import *
from hlr_tof_to_scalar_Q import *
from hlr_tof_to_wavelength import *
from hlr_tof_to_wavelength_lin_time_zero import *
from hlr_wavelength_to_d_spacing import *
from hlr_wavelength_to_energy import *
from hlr_wavelength_to_scalar_k import *
from hlr_wavelength_to_scalar_Q import *
from hlr_weighted_average import *

from HLR_version import version as __version__

#version
__id__ = "$Id$"
