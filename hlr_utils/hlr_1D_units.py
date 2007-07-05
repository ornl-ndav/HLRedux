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

def one_d_units(som, units):
    """
    This function takes a C{SOM} and a unit string and checks the C{SOM}s
    primary axes for the requested units. 

    @param som: The C{SOM} to search the primary axes for units
    @type som: C{SOM.SOM}
    
    @param units: The units to search the C{SOM} primary axes for
    @type units: C{string}


    @return: The first index containing the requested units
    @rtype: C{int}


    @raise RuntimeError: The requested units are not found
    """
    
    if not som.hasAxisUnits(units):
        raise RuntimeError("No primary axis with %s units" % units)

    return som.axisUnitsAt(units)

def force_units(som, units, dim=1):
    """
    This function takes a C{SOM}, a unit string and an optional dimension
    parameter and replaces the units for the dimensional parameter minus 1 in
    the C{SOM}.

    @param som: The C{SOM} in which an axis units will be replaced
    @type som: C{SOM.SOM}
    
    @param units: The units to replace the current units in the C{SOM} with
    @type units: C{string}
    
    @param dim: The order of the primary axis. It's actual position in the
                C{SOM} list is dim-1
    @type dim: C{int}


    @return: The C{SOM} with the units forced to the requested units
    @rtype: C{SOM.SOM}
    """
    
    som.setAxisUnits(dim-1, units)
    return som
