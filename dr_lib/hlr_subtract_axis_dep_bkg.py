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

def subtract_axis_dep_bkg(obj, coeffs):
    """
    This function takes spectrum object(s) and a set of coefficients and
    subtracts an axis dependent background based on a polynomial. The order
    of the polynomial is based on the number of coefficients provided.

    @param obj: Object from which to subtract the individual background numbers
    @type obj: C{SOM.SOM} or C{SOM.SO}

    @param coeffs: The set of coefficients for the polynomial representation
                   of the background to be subtracted.
    @type coeffs: C{list} of C{floats}


    @return: Object with the axis dependent background subtracted
    @rtype: C{SOM.SOM} or C{SOM.SO}
    """

    return obj
