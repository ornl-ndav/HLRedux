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

def cut_spectra(obj, low_cut, high_cut):
    """
    This function takes spectra and a given set of axis cutoff values and
    produces spectra that is smaller than the original by removing information
    outside the cut range.
    
    @param obj: The object containing the spectra to be zeroed
    @type obj: C{SOM.SOM}

    @param low_cut: The low-side axis cutoff. All values less than this will
                    be discarded.
    @type low_cut: C{float}

    @param high_cut: The high-side axis cutoff. All values greater than this
                     will be discarded.
    @type high_cut: C{float}    


    @return: Object containing the zeroed spectra
    @rtype: C{SOM.SOM}

    """
    # Kickout if both cuts are None
    if low_cut is None and high_cut is None:
        return obj

    # import the helper functions
    import hlr_utils

    return obj
