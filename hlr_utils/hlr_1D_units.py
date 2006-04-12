def hlr_1D_units(som, units):
    """
    This function takes a SOM and a unit string and checks the SOMs primary
    axes for the requested units. Raises an exception if units are not found.

    Parameters:
    ----------
    -> som is the SOM to search the primary axes for units
    -> units is the units to search the SOM primary axes for

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
    """
    
    som.setAxisUnits(units,dim-1)
