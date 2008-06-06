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
                       angle. The possible values are I{total}, I{primary} and
                       I{secondary}. The default is I{secondary}.
    @type pathtype: C{string}
    """
    import hlr_utils

    # Check for keywords
    try:
        pathtype = kwargs["pathtype"]
    except KeyError:
        pathtype = "secondary"

    # Get pixel pathlength and square it (this is in meters)
    (pl, pl_err2) = hlr_utils.get_parameter(pathtype, pix, inst)
    pl2 = pl * pl

    import SOM
    npix = SOM.SO()

    import math

    # Get x pixel size
    x1 = hlr_utils.get_parameter("x-offset", pix, inst)

    # Make the neighboring pixel ID in the x direction
    try:
        npix.id = (pix.id[0], (pix.id[1][0]+1, pix.id[1][1]))
        x2 = hlr_utils.get_parameter("x-offset", npix, inst)
    except IndexError:
        npix.id = (pix.id[0], (pix.id[1][0]-1, pix.id[1][1]))
        x2 = hlr_utils.get_parameter("x-offset", npix, inst)

    # Pixel offsets are in meters
    xdiff = math.fabs(x2 - x1)

    # Get y pixel size
    y1 = hlr_utils.get_parameter("y-offset", pix, inst)

    # Make the neighboring pixel ID in the y direction
    try:
        npix.id = (pix.id[0], (pix.id[1][0], pix.id[1][1]+1))
        y2 = hlr_utils.get_parameter("y-offset", npix, inst)
    except IndexError:
        npix.id = (pix.id[0], (pix.id[1][0], pix.id[1][1]-1))
        y2 = hlr_utils.get_parameter("y-offset", npix, inst)

    # Pixel offsets are in meters
    ydiff = math.fabs(y2 - y1)

    # Make pixel area
    pix_area = xdiff * ydiff

    # Get the polar angle
    (polar, polar_err2) = hlr_utils.get_parameter("polar", pix, inst)
    
    solid_angle = (pix_area * math.cos(polar)) / pl2

    print "A:", pix.id, pl, pix_area, polar, pl2, solid_angle

    return solid_angle
    
    
