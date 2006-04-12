
def hlr_math_compatible(obj1, obj1_descr, obj2, obj2_descr):
    """
    This function takes two SOMs and checks them for the following conditions:
    1. The units of the primary axes in SOM1 match those in SOM2
    2. The y units of SOM1 match the y units in SOM2

    If all three steps pass, nothing is done. If one step fails an exception
    is raised.
    
    Parameters:
    ----------
    -> som1 is the first SOM to compare
    -> obj2 is the second SOM to compare

    Exceptions:
    ----------
    <- RuntimeError is raised if the units of the primary axes in SOM1 do not
       match those in SOM2
    <- RuntimeError is raised if the y units in SOM1 is not the same as in SOM2
    """

    if obj1_descr == "SOM" and obj2_descr == "SOM":
        
        obj1_axis_units = obj1.getAllAxisUnits()
        obj2_axis_units = obj2.getAllAxisUnits()
        
        value = True
        count = []
        index = 1
        for (unit1, unit2) in map(None, obj1_axis_units, obj2_axis_units):
            if unit1 != unit2:
                count.append(index)
                value = False
                index += 1
                
        if not value:
            raise RuntimeError, "X units at %s do not match" \
                  % str(count)
                
        if obj1.getYUnits()!=obj2.getYUnits():
            raise RuntimeError,"Y units do not match"


    elif obj1_descr == "SO" and obj2_descr == "SO":

        if obj1.dim() != obj2.dim():
            raise IndexError, "SO1 and SO2 are not the same dimension."

        value = True
        count = []
        index = 1
        for (axis1, axis2) in map(None, obj1, obj2):
            if axis1 != axis2:
                count.append(index)
                value = False
                index += 1
                
        if not value:
            raise RuntimeError, "X axes at %s do not match" \
                  % str(count)

