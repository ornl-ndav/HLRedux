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

import nessi_list

def rebin_axis_1D_frac(obj, axis_out):
    """
    This function rebins the primary axis for a C{SOM} or a C{SO} based on the
    given C{NessiList} axis.

    @param obj: Object to be rebinned
    @type obj: C{SOM.SOM} or C{SOM.SO}

    @param axis_out: The axis to rebin the C{SOM} or C{SO} to
    @type axis_out: C{NessiList}


    @return: Two objects that have been rebinned according to the provided
             axis. The first object contains the rebinned counts and the second
             contains the fractional area.
    @rtype: C{tuple} of two C{SOM.SOM}s or C{SOM.SO}s


    @raise TypeError: The rebinning axis given is not a C{NessiList}

    @raise TypeError: The object being rebinned is not a C{SOM} or a C{SO}
    """
    # import the helper functions
    import hlr_utils

    return (None, None)
