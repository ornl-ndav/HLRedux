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

def calc_solid_angle(inst, pix, **kwargs):
    """
    This function calculates the solid angle of a given pixel by taking the
    area of the pixel and dividing it by the square of the pathlength.

    @param inst: The object containing the geometry information.
    @type inst: C{Instrument} or C{CompositeInstrument}

    @param pix: The pixel to calculate the solid angle for.
    @type pix: C{SOM.SO}

    @param kwargs: A list of keyword arguments that the function accepts:

    @keyword pathtype: The pathlength type from which to calculate the solid
    angle. The possible values are I{total} and I{primary}. The default is
    I{total}.
    @type pathtype: C{string}
    """
    import hlr_utils

    # Check for keywords
    try:
        pathtype = kwargs["pathtype"]
    except KeyError:
        pathtype = "total"

    # Get pixel pathlength and square it (this is in meters)
    (pl, pl_err2) = hlr_utils.get_parameter(pathtype, pix, inst)
    pl2 = pl * pl

    pix_area = 0.0

    return pix_area / pl2
    
    
