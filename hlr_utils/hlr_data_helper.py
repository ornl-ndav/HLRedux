import nessi_list
import SOM

# this should be replaced with an enum
SOM_type="SOM"
SO_type="SO"
num_type="number"
empty_type=""

def empty_result(obj1,obj2):
    """
    This function inspects the arguments and returns an appropriate
    return type for an operation using the arguments. The object can
    be filled using result_insert.

    Parameters:
    ----------
    -> obj1 is a SOM, SO or tuple
    -> obj2 is a SOM, SO or tuple

    Returns:
    -------
    <- A tuple containing the requested object (SOM, SO or tuple) and the
       corresponding descriptor
    """
    
    obj1_type = get_type(obj1)
    obj2_type = get_type(obj2)

    if (obj1_type == SOM_type and obj2_type == SOM_type) or \
           (obj1_type == SOM_type and obj2_type != SOM_type) or \
           (obj1_type != SOM_type and obj2_type == SOM_type):
        return (SOM.SOM(),SOM_type)
    elif (obj1_type == SO_type and obj2_type == SO_type) or \
             (obj1_type == num_type and obj2_type == SO_type) or \
             (obj1_type == SO_type and obj2_type == num_type):
        return (SOM.SO(), SO_type)
    else:
        return ([], num_type)


def result_insert(result,descr,value,map_so,axis="y",pap=0):
    """
    This function takes value and puts it into the result in an
    appropriate fashion. The description is used for decision making.
    """
    if descr == None:
        result_type = get_type(result)
    else:
        result_type = descr

    if (result_type == SOM_type):
        if axis.lower() == "y":
            so = SOM.SO()
            so.y = value[0]
            so.var_y = value[1]
            so.id = map_so.id
            so.axis = map_so.axis

            result.append(so)
        elif axis.lower() == "x":
            so = SOM.SO()
            so.id = map_so.id


            result.append(so)
    elif (result_type == SO_type):
        if axis.lower() == "y":
            result.y = value[0]
            result.var_y = value[1]
            result.id = map_so.id
            result.axis = map_so.axis
            return result.y
        elif axis.lower() == "x":
            result.id = map_so.id
    elif (result_type == num_type):
        result[0] = value[0]
        result[1] = value[1]
    else:
        raise TypeError, "Object type not recognized by get_value function."


def get_length(obj1,obj2=None):
    """
    This function returns the length appropriate for iterating
    through the objects.

    Parameters:
    ----------
    -> obj1 is a SOM, SO or tuple
    -> obj2 (OPTIONAL) is a SOM, SO or tuple

    Returns:
    -------
    <- The iteration length of the top hierarchy object (SOM > SO or tuple)

    Exceptions:
    ----------
    <- IndexError is raised if the two incoming objects are SOMs and the number
       of SOs in them are not equal
    """
    
    obj1_type,obj2_type = get_descr(obj1,obj2)
    if (obj1_type == SOM_type and obj2_type == SOM_type):
        if len(obj1) != len(obj2):
            raise IndexError,"Can only add SOMs with same number of spectra"
        return len(obj1)
    elif (obj1_type == SOM_type and obj2_type != SOM_type):
        return len(obj1)
    elif (obj1_type != SOM_type and obj2_type == SOM_type):
        return len(obj2)
    elif (obj1_type == empty_type and obj2_type == empty_type):
        raise RuntimeError, "One or two objects need to be defined."
    elif (obj1_type != SOM_type and obj2_type != SOM_type):
        return 1


def get_descr(obj1,obj2=None):
    """
    This function takes one or two arbitrary objects and returns the descriptor
    for those objects.

    Parameters:
    ----------
    -> obj1 is a SOM, SO or tuple
    -> obj2 (OPTIONAL) is a SOM, SO or tuple

    Returns:
    -------
    <- A tuple containing the descriptors obj1 and obj2
    """
    
    return (get_type(obj1), get_type(obj2))


def get_value(obj,index=0,descr=None,axis="y",pap=0):
    """
    This function takes an arbitrary object and returns the value for
    the given index. If the object is not a collection the index is
    ignored.

    Parameters:
    ----------
    -> obj is a SOM, SO or tuple
    -> index is a possible index for use in a SOM
    -> descr (OPTIONAL) is the object descriptor, default is None
    -> axis (OPTIONAL) is the axis to grab the value from
    -> pap (OPTIONAL) is the primary axis position. This is used to pull the
       value from the correct primary axis position.

    Returns:
    -------
    <- The appropriate object containing the value

    Exceptions:
    ----------
    <- TypeError is raised if obj is not a recognized type
    """
    
    if descr == None:
        obj_type = get_type(obj)
    else:
        obj_type = descr
    if (obj_type == SOM_type):
        if axis.lower() == "y":
            return obj[index].y
        elif axis.lower() == "x":
            return obj[index][pap].val
    elif (obj_type == SO_type):
        if axis.lower() == "y":
            return obj.y
        elif axis.lower() == "x":
            return obj[pap].val
    elif (obj_type == num_type):
        return obj[0]
    else:
        raise TypeError, "Object type not recognized by get_value function."


def get_err2(obj,index,descr=None,axis="y",pap=0):
    """
    This function takes an arbitrary object and returns the
    uncertainty squared for the given index. If the object is not a
    collection the index is ignored.

    Parameters:
    ----------
    -> obj is a SOM, SO or tuple
    -> index is a possible index for use in a SOM
    -> descr (OPTIONAL) is the object descriptor, default is None
    -> axis (OPTIONAL) is the axis to grab the error2 from
    -> pap (OPTIONAL) is the primary axis position. This is used to pull the
       error2 from the correct primary axis position.

    Returns:
    -------
    <- The appropriate object containing the error2

    Exceptions:
    ----------
    <- TypeError is raised if obj is not a recognized type
    """

    if descr == None:
        obj_type = get_type(obj)
    else:
        obj_type = descr

    if (obj_type == SOM_type):
        if axis.lower() == "y":
            return obj[index].var_y
        elif axis.lower() == "x":
            if obj[index][pap].var == None:
                return nessi_list.NessiList(len(obj[index][pap].val))
            else:
                return obj[index][pap].var
    elif (obj_type == SO_type):
        if axis.lower() == "y":
            return obj.var_y
        elif axis.lower() == "x":
            if obj[pap].var == None:
                return nessi_list.NessiList(len(obj[pap].val))
            else:
                return obj[pap].var
    elif (obj_type == num_type):
        return obj[1]
    else:
        raise TypeError, "Object type not recognized by get_err2 function."


def get_type(obj):
    """
    This function taks an arbitraray object and returnes the descriptor for
    the object.

    Parameters:
    ----------
    -> obj is a SOM, SO or tuple

    Returns:
    -------
    <- The descriptor for the corresponding object
    """
    
    if obj == None:
        return empty_type

    try:
        obj.attr_list
        return SOM_type
    except AttributeError:
        try:
            obj.id
            return  SO_type
        except AttributeError:
            return num_type


def swap_args(left,right):
    """
    This function takes two arguments and returns the objects in the reversed
    positions.

    Parameters:
    ----------
    -> left is one the object to be swapped to the right position
    -> right is one the object to be swapped to the left position

    Returns:
    -------
    <- The incoming objects in the swapped locations
    """

    temp = left
    left = right
    right = temp

    return left,right

def get_map_so(obj,index):
    """
    This function takes a SOM and returns the first SO for use in mapping. If
    the object is a SO, it is immediately returned.

    Parameters:
    ----------
    -> obj is a SOM or SO

    Returns:
    -------
    <- A mapping SO (can be None if obj is a tuple or empty
    """

    obj_type = get_type(obj)

    if obj_type == SO_type:
        return obj
    elif obj_type == SOM_type:
        return obj[index]
    else:
        return None
