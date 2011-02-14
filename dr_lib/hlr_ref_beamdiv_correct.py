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

import math
import nessi_list

def ref_beamdiv_correct(attrs, pix_id, pathlength, epsilon, **kwargs):
    """

    @param attrs: The attribute list of a C{SOM.SOM}
    @type attrs: C{SOM.AttributeList}

    @param pix_id: The pixel ID for which the correction will be calculated
    @type pix_id: C{tuple}

    @param pathlength: The sample to detector distance.
    @type pathlength: C{float}

    @param epsilon: The pixel spatial resolution in units of meters
    @type epsilon: C{float}

    @param kwargs: A list of keyword arguments that the function accepts:

    @return: The beam divergence correction to the scattering angle
    @type: float

    @raise RuntimeError: If the instrument name is not recognized.
    """
    # Set instrument specific strings
    inst_name = attrs["instrument_name"]
    if inst_name == "REF_L":
        first_slit_size = "data-slit1_size"
        last_slit_size = "data-slit2_size"
        last_slit_dist = "data-slit2_distance"
        slit_dist = "data-slit12_distance"

    elif inst_name == "REF_M":
        first_slit_size = "data-slit1_size"
        last_slit_size = "data-slit3_size"
        last_slit_dist = "data-slit3_distance"
        slit_dist = "data-slit13_distance"
    else:
        raise RuntimeError("Do not know how to handle instrument %s" \
                           % inst_name)

    # This is currently set to the same number for both REF_L and REF_M
    if epsilon is None:
        epsilon = 0.5 * 1.3 * 1.0e-3
    
    gamma_plus = math.atan2(0.5 * (attrs[first_slit_size][0] + \
                                   attrs[last_slit_size][0]),
                            attrs[slit_dist][0])
    
    gamma_minus = math.atan2(0.5 * (attrs[first_slit_size][0] - \
                                    attrs[last_slit_size][0]),
                             attrs[slit_dist][0])
    
    half_last_aperture = 0.5 * attrs[last_slit_size][0]
    neg_half_last_aperture = -1.0 * half_last_aperture

    last_slit_to_det = attrs[last_slit_dist][0] + pathlength

    dist_last_aper_det_sin_gamma_plus = last_slit_to_det * math.sin(gamma_plus)
    dist_last_aper_det_sin_gamma_minus = last_slit_to_det * \
                                         math.sin(gamma_minus)

    # Set the delta theta coordinates of the acceptance polygon
    accept_poly_x = nessi_list.NessiList()
    accept_poly_x.append(-1.0 * gamma_minus)
    accept_poly_x.append(gamma_plus)
    accept_poly_x.append(gamma_plus)
    accept_poly_x.append(gamma_minus)
    accept_poly_x.append(-1.0 * gamma_plus)
    accept_poly_x.append(-1.0 * gamma_plus)
    accept_poly_x.append(accept_poly_x[0])

    # Set the z coordinates of the acceptance polygon
    accept_poly_y = nessi_list.NessiList()
    accept_poly_y.append(half_last_aperture - \
                         dist_last_aper_det_sin_gamma_minus + epsilon)
    accept_poly_y.append(half_last_aperture + \
                         dist_last_aper_det_sin_gamma_plus + epsilon)
    accept_poly_y.append(half_last_aperture + \
                         dist_last_aper_det_sin_gamma_plus - epsilon)
    accept_poly_y.append(neg_half_last_aperture + \
                         dist_last_aper_det_sin_gamma_minus - epsilon)
    accept_poly_y.append(neg_half_last_aperture - \
                         dist_last_aper_det_sin_gamma_plus - epsilon)
    accept_poly_y.append(neg_half_last_aperture - \
                         dist_last_aper_det_sin_gamma_plus + epsilon)
    accept_poly_y.append(accept_poly_y[0])

    
    
    return 0
    
