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

def calc_substrate_trans(obj, subtrans_coeff, substrate_thick):
    """
    This function calculates substrate transmission via the following formula:
    T = exp[-(A + B * wavelength) * t] where A is a constant with units of
    cm^-1, B is a constant with units of cm^-2 and t is the substrate
    thickness in units of cm.

    @param obj: The data object that contains the TOF axes to calculate the
                transmission from.
    @type obj: C{SOM.SOM}

    @param subtrans_coeff: The two coefficients for substrate transmission
           calculation.
    @type subtrans_coeff: C{tuple} of two C{float}s

    @param substrate_thick: The thickness of the substrate.
    @type substrate_thick: C{float}
    """

    return None
