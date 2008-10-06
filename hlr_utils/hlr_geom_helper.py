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

import hlr_utils

class Angles(object):
    """
    This is a helper object for storing the angle information for the corners
    of DGS instrument pixels.
    """

    def __init__(self):
        """
        Object constructor
        """

def get_corner_geometry(filename):
    """
    This function will read in a geometry file containing the corner angle
    information for DGS instruments.

    @param filename: The name of the geometry file to read.
    @type filename: C{string}


    @return: The angle information for the particular DGS instrument.
    @rtype: C{dict}
    """

    return None
