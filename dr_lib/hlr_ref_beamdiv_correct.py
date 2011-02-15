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

def ref_beamdiv_correct(attrs, pix_id, epsilon, **kwargs):
    """

    @param attrs: The attribute list of a C{SOM.SOM}
    @type attrs: C{SOM.AttributeList}

    @param pix_id: The pixel ID for which the correction will be calculated
    @type pix_id: C{tuple}

    @param epsilon: The pixel spatial resolution in units of meters
    @type epsilon: C{float}

    @param kwargs: A list of keyword arguments that the function accepts:

    @kwarg det_secondary: The main sample to detector flightpath in meters.
    @type det_secondary: C{float}

    @kwarg pix_width: The width of a pixel in the high resolution direction
    @type pix_width: C{float}


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

    # Get sorting direction, y is True, x is False
    y_sort = attrs["ref_sort"]
    
    # Get keyword arguments
    det_secondary = kwargs.get("det_secondary")
    pix_width = kwargs.get("pix_width")

    # Check keyword arguments
    if det_secondary is None:
        det_secondary = attrs.instrument.get_det_secondary()[0]

    if pix_width is None:
        pix_width = __get_pixel_width(inst_name)

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

    last_slit_to_det = attrs[last_slit_dist][0] + det_secondary

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

    if y_sort:
        cur_offset = attrs.instrument.get_y_pix_offset(pix_id)
        next_id = (pix_id[0], (pix_id[1][0], pix_id[1][1]+1))
        next_offset = attrs.instrument.get_y_pix_offset(next_id)
    else:
        cur_offset = attrs.instrument.get_x_pix_offset(pix_id)
        next_id = (pix_id[0], (pix_id[1][0]+1, pix_id[1][1]))
        next_offset = attrs.instrument.get_x_pix_offset(next_id)

    pix_width = math.fabs(next_offset - cur_offset)

    xMinus = cur_offset - (0.5 * pix_width)
    xPlus = cur_offset + (0.5 * pix_width)

    yLeftCross = -1
    yRightCross = -1

    xI = accept_poly_x[0]
    yI = accept_poly_y[0]

    int_poly_x = nessi_list.NessiList()
    int_poly_y = nessi_list.NessiList()

    for i in xrange(len(accept_poly_x)):
        xF = accept_poly_y[i]
        yF = accept_poly_x[i]

        if xI < xF:
            if xI < xMinus and xF >= xMinus:
                yLeftCross = yI + (yF - yI) * (xMinus - xI) / (xF - xI)
                int_poly_y.append(yLeftCross)
                int_poly_x.append(xMinus)

            if xI < xPlus and xF >= xPlus:
                yRightCross = yI + (yF - yI) * (xPlus - xI) / (xF - xI);
                int_poly_y.append(yRightCross)
                int_poly_x.append(xPlus)
                
        else:
            if xF < xPlus and xI >= xPlus:
                yRightCross = yI + (yF - yI) * (xPlus - xI) / (xF - xI);
                int_poly_y.append(yRightCross)
                int_poly_x.append(xPlus)

            if xF < xMinus and xI >= xMinus:
                yLeftCross = yI + (yF - yI) * (xMinus - xI) / (xF - xI);
                int_poly_y.append(yLeftCross)
                int_poly_x.append(xMinus)
                
        # This catches points on the polygon inside the range of interest
        if xF >= xMinus and xF < xPlus:
            int_poly_y.append(yF)
            int_poly_x.append(xF)

        xI = xF
        yI = yF

    if len(int_poly_x) > 2:
        int_poly_x.append(int_poly_x[0])
        int_poly_y.append(int_poly_y[0])
        int_poly_x.append(int_poly_x[1])
        int_poly_y.append(int_poly_y[1])
    else:
        # Intersection polygon is NULL, point or line, so has no area
        # Therefore there is no angle correction
        return 0.0

    # Calculate intersection polygon aread
    import utils
    area = utils.calc_area_2D_polygon(int_poly_x, int_poly_y,
                                      len(int_poly_x) - 2)
    
    return __calc_center_of_mass(int_poly_x, int_poly_y, area)

def __calc_center_of_mass(arr_x, arr_y, A):
    center_of_mass = 0.0;
    SIXTH = 1. / 6.
    for j in xrange(len(arr_x) -2):
        center_of_mass += (arr_y[j] + arr_y[j + 1]) \
                          * ((arr_y[j] * arr_x[j + 1]) - \
                             (arr_y[j + 1] * arr_x[j]))

    if A != 0.0:
        return (SIXTH * center_of_mass) / A
    else:
        return 0.0

def __get_pixel_width(iname):
    None
    
if __name__ == "__main__":
    import SOM
    
    attrs = SOM.AttributeList()
    attrs["instrument_name"] = "REF_L"
    attrs["data-slit1_size"] = (1.52e-4, "metre")
    attrs["data-slit2_size"] = (1.54e-4, "metre")
    attrs["data-slit12_distance"] = (0.885, "metre")
    attrs["data-slit2_distance"] = (0.654, "metre")

    pix_id = ("bank1", (172, 126))
    pl = 1.35
    epsilon = None

    print "************ ref_beam_div_correct"
    print "* ref_beam_div_correct: ", ref_beam_div_correct(attrs, pix_id,
                                                           epsilon,
                                                           det_secondary=pl)
