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

def create_binner_string(config):
    """
    This function takes a L{hlr_utils.Configuration} object, removes the
    elements from it that are not fundamental to a given run of the data
    reduction and create an MD5 sum ID from that configuration.

    @param config: The current data reduction configuration
    @type config: L{hlr_utils.Configuration}


    @return: A unique string based off an MD5 sum of the configuration
    @rtype: C{string}
    """

    return ""
