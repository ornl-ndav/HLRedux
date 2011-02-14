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

def ref_beamdiv_correct(attrs, pix_id, **kwargs):
    """

    @param attrs: The attribute list of a C{SOM.SOM}
    @type attrs: C{SOM.AttributeList}

    @param pix_id: The pixel ID for which the correction will be calculated
    @type pix_id: C{tuple}


    @return: The beam divergence correction to the scattering angle
    @type: float

    @raise RuntimeError: If the instrument name is not recognized.
    """
    # Set instrument specific strings
    inst_name = attrs["instrument_name"]
    if inst_name == "REF_L":
        first_slit_size = "data-slit1_size"
        last_slit_size = "data-slit2_size"
        last_slit_distot = "data-slit12_distance"
    elif inst_name == "REF_M":
        first_slit_size = "data-slit1_size"
        last_slit_size = "data-slit3_size"
        last_slit_distot = "data-slit13_distance"
    else:
        raise RuntimeError("Do not know how to handle instrument %s" \
                           % inst_name)
    
    gamma_plus = math.atan2(0.5 * (attrs[first_slit_size][0] + \
                                   attrs[last_slit_size][0]),
                            attrs[last_slit_distot][0])
    
    gamma_minus = math.atan2(0.5 * (attrs[first_slit_size][0] - \
                                    attrs[last_slit_size][0]),
                             attrs[last_slit_distot][0])
    
    half_last_aperture = 0.5 * attrs[last_slit_size][0]
    neg_half_last_aperture = -1.0 * half_last_aperture

    
    

    return 0
    
