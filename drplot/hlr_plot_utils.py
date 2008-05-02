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

import numpy

def clean_data(axis, x, y, var_y=None, var_x=None):
    """
    This function cleans data for plotting.

    @param axis: The particular axis to clean. This is either I{x} or I{y}.
    @type axis:


    @return: The cleaned arrays. The order is I{(x, y, var_y, var_x)}.
    @rtype: C{tuple} of C{NumPy} arrays
    """
    return (x, y, var_y, var_x)
