
def hlr_math_compatible(som1, som2):
    """
    This function takes two SOMs and checks them for the following conditions:
    1. The units of the primary axes in SOM1 match those in SOM2
    2. The y units of SOM1 match the y units in SOM2

    If all three steps pass, nothing is done. If one step fails an exception
    is raised.
    
    Parameters:
    ----------
    -> som1 is the first SOM to compare
    -> som2 is the second SOM to compare

    Exceptions:
    ----------
    <- RuntimeError is raised if the units of the primary axes in SOM1 do not
       match those in SOM2
    <- RuntimeError is raised if the y units in SOM1 is not the same as in SOM2
    """
    
    som1_axis_units = som1.getAllAxisUnits()
    som2_axis_units = som2.getAllAxisUnits()

    value = True
    count = []
    index = 1
    for (unit1, unit2) in map(None, som1_axis_units, som2_axis_units):
        if unit1 != unit2:
            count.append(index)
            value = False
        index += 1
            
    if not value:
        raise RuntimeError, "X units at %s do not match" % str(count)

    if som1.getYUnits()!=som2.getYUnits():
        raise RuntimeError,"Y units do not match"
                
