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

def filter_normalization(obj, threshold):
    """
    This function takes an object with normalization integration information
    and a threshold and creates a mask file containing the pixel IDs that do
    not make it above the threshold.

    @param obj: The object containing the normalization information
    @type obj: C{SOM.SOM} or C{SOM.SO}

    @param threshold: The upper bound for masked pixels
    @type threshold: C{float}

    
    """
    pass
