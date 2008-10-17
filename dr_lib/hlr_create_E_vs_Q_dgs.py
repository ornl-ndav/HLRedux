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

def create_E_vs_Q_dgs(som, E_i, Q_final, **kwargs):
    """
    This function starts with the rebinned energy transfer and turns this
    into a 2D spectra with E and Q axes for DGS instruments.

    @param som: The input object with initial IGS wavelength axis
    @type som: C{SOM.SOM}

    @param E_i: The initial energy for the given data.
    @type E_i: C{tuple}

    @param Q_final: The momentum transfer axis to rebin the data to
    @type Q_final: C{nessi_list.NessiList}

    @param kwargs: A list of keyword arguments that the function accepts:

    @keyword corner_geom: The filename that contains the corner geometry
                          information.
    @type corner_geom: C{string}    
    """

    # Check keywords
    try:
        corner_geom = kwargs["corner_geom"]
    except KeyError:
        corner_geom = ""
        
    return None
