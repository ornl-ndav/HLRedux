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

def shift_spectrum(obj, **kwargs):
    """
    This function takes a given spectrum and a central value and creates
    a spectrum that is shifted about that point. Values greater than the point
    are moved to the beginning of the new spectrum and values less than the
    point are move towards the end of the new spectrum.
    
    @param obj: Monitor object that will be shifted
    @type obj: C{SOM.SOM} or C{SOM.SO}

    @param kwargs: A list of keyword arguments that the function accepts    
    """
    pass
