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

def create_det_eff(obj):
    """
    This function creates detector efficiency spectra based on the wavelength
    spectra from the given object. The efficiency spectra are created based on
    the following formalism: Ci*exp(-di*lambda) where i represents the
    constants for a given detector pixel.

    @param obj: Object containing spectra that will create the detector
                efficiency spectra.
    @type obj: C{SOM.SOM} or C{SOM.SO}


    @return: Object containing the detector efficiency spectra
    @rtype: C{SOM.SOM} or C{SOM.SO}
    """

    return None
