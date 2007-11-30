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

def fix_index(index, end_index):
    """
    This function corrects a given index so that it remains on the correct
    bounds for a histogram value array which is one longer than the
    corresponding axis.

    @param index: The index to possible correct
    @type index: C{int}

    @param end_index: The last index in the value axis
    @type end_index: C{int}


    @return: The corrected index
    @rtype: C{int}
    """
    
    if index == -1:
        return 0
    elif index == end_index:
        return index - 1
    else:
        return index
