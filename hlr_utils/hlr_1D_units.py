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

def hlr_1D_units(som, units):
    """
    This function takes a SOM and a unit string and checks the SOMs primary
    axes for the requested units. Raises an exception if units are not found.

    Parameters:
    ----------
    -> som is the SOM to search the primary axes for units
    -> units is the units to search the SOM primary axes for

    Returns:
    -------
    <- The first index containing the requested units

    Exceptions:
    ----------
    <- RuntimeError is raised if the requested units are not found
    """
    
    if not som.hasAxisUnits(units):
        raise RuntimeError,"No primary axis with %s units" % units

    return som.axisUnitsAt(units)

def hlr_force_units(som, units, dim=1):
    """
    This function takse a SOM, a unit string and an optional dimension
    parameter and replaces the units for the dimensional parameter minus 1 in
    the SOM.

    Parameters:
    ----------
    -> som is the SOM in which an axis units will be replaced
    -> units is the units to replace the current one in the SOM
    -> dim is the order of the primary axis. It's actual position in the SOM
       list is dim-1

    Returns:
    -------
    <- The SOM with the units forced to the requested units
    """
    
    som.setAxisUnits(dim-1,units)
    return som
