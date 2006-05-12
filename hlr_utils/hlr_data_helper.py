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

import nessi_list
import SOM

# this should be replaced with an enum
SOM_type="SOM"
SO_type="SO"
list_type="list"
num_type="number"
empty_type=""

def empty_result(obj1,obj2=None):
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

    if obj2 == None:
        if obj1_type == SOM_type:
            return (SOM.SOM(), SOM_type)
        elif obj1_type == SO_type:
            return (SOM.SO(obj1.dim()), SO_type)
        elif obj1_type == list_type:
            return ([], list_type)
        else:
            return ([], num_type)
    # If obj2 != None, go on.
    else:
        pass
    
    obj2_type = get_type(obj2)

    if (obj1_type == SOM_type or obj2_type == SOM_type):
        return (SOM.SOM(), SOM_type)
    elif (obj1_type == SO_type or obj2_type == SO_type):
        if obj1_type == SO_type:
            return (SOM.SO(obj1.dim()), SO_type)
        elif obj2_type == SO_type:
            return (SOM.SO(obj2.dim()), SO_type)
    elif (obj1_type == list_type or obj2_type == list_type):
        return ([], list_type)
    else:
        return ([], num_type)


def result_insert(result,descr,value,map_so,axis="y",pap=0,xvals=None):
    """
    This function takes value and puts it into the result in an
    appropriate fashion. The description is used for decision making.

    Parameters:
    ----------
    -> result is a SOM, SO, list or tuple
    -> descr is the object descriptor
    -> value is a tuple containing information to be place in result directly
       or an object that will be placed into result
    -> map_so is a SO that has information that will be mapped to a SO if
       result is either a SOM or a SO
    -> axis (OPTIONAL) is the axis to grab the value from
    -> pap (OPTIONAL) is the primary axis position. This is used to pull the
       value from the correct primary axis position.
    -> xvals (OPTIONAL) is a list of x-axes that are not provided by either
       value or map_so      

    Returns:
    -------
    <- A SOM, SO, list or tuple with the provided information inserted
    """
    
    if descr == None:
        result_type = get_type(result)
    else:
        result_type = descr

    if (result_type == SOM_type):
        if axis.lower() == "y":
            so = SOM.SO(map_so.dim())
            so.y = value[0]
            so.var_y = value[1]
            so.id = map_so.id
            so.axis = map_so.axis

            result.append(so)
        elif axis.lower() == "x":
            so = SOM.SO(map_so.dim())
            so.id = map_so.id
            so.y = map_so.y
            so.var_y = map_so.var_y
            for i in range(map_so.dim()):
                if i == pap:
                    so.axis[pap].val = value[0]
                    if map_so.axis[pap].var != None:
                        so.axis[pap].var = value[1]
                else:
                    so.axis[i].val = map_so.axis[i].val
                    if map_so.axis[i].var != None:
                        so.axis[i].var = map_so.axis[i].var

            result.append(so)
        elif axis.lower() == "all":
            if map_so != None:
                so = SOM.SO(map_so.dim())
                so.id = map_so.id
                so.y = value[0]
                so.var_y = value[1]
                for i in range(len(xvals)):
                    if i % 2 == 0:
                        so.axis[i].val = xvals[i]
                    elif i % 2 != 0:
                        if map_so.axis[i-1].var == None:
                            so.axis[i].val = xvals[i]
                        else:
                            so.axis[i-1].var = xvals[i]
                            
                result.append(so)
            else:
                result.append(value)
                
    elif (result_type == SO_type):
        if axis.lower() == "y":
            result.y = value[0]
            result.var_y = value[1]
            result.id = map_so.id
            result.axis = map_so.axis

        elif axis.lower() == "x":
            result.id = map_so.id
            result.y = map_so.y
            result.var_y = map_so.var_y
            for i in range(map_so.dim()):
                if i == pap:
                    result.axis[pap].val = value[0]
                    if map_so.axis[pap].var != None:
                        result.axis[pap].var = value[1]
                else:
                    result.axis[i].val = map_so.axis[i].val
                    if map_so.axis[i].var != None:
                        result.axis[i].var = map_so.axis[i].var

        elif axis.lower() == "all":
            if map_so != None:
                result.id = map_so.id
                result.y = value[0]
                result.var_y = value[1]
                for i in range(len(xvals)):
                    if i % 2 == 0:
                        result.axis[i].val = xvals[i]
                    elif i % 2 != 0:
                        if map_so.axis[i-1].var == None:
                            result.axis[i].val = xvals[i]
                        else:
                            result.axis[i-1].var = xvals[i]

            else:
                result.id = value.id
                result.y = value.y
                result.var_y = value.var_y
                result.axis = value.axis

    elif (result_type == num_type or result_type == list_type):
        if axis.lower() == "all":
            result.append(tuple(value))
        else:
            result.append(value[0])
            result.append(value[1])

        tuple(result)
    else:
        raise TypeError, "Object type not recognized by result_insert"\
              +" function."


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
    <- RuntimeError is raised if one or both objects are None
    """
    
    (obj1_type,obj2_type) = get_descr(obj1,obj2)
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
    elif (obj1_type == list_type or obj2_type == list_type):
        if(obj1_type == list_type):
            return len(obj1)
        elif(obj2_type == list_type):
            return len(obj2)
        else:
            raise RuntimeError, "hlr_utils.get_length: Should never get here!"
    elif (obj1_type != SOM_type and obj2_type != SOM_type):
        return 1
    else:
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
        return get_value(obj[index],index,"SO",axis,pap)
    elif (obj_type == SO_type):
        if axis.lower() == "y":
            return obj.y
        elif axis.lower() == "x":
            return obj.axis[pap].val
        elif axis.lower() == "all":
            return obj
    elif (obj_type == list_type):
        return get_value(obj[index],index,"number",axis,pap)
    elif (obj_type == num_type):
        if axis.lower() == "all":
            return obj
        else:
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
        return get_err2(obj[index],index,"SO",axis,pap)
    elif (obj_type == SO_type):
        if axis.lower() == "y":
            return obj.var_y
        elif axis.lower() == "x":
            if obj.axis[pap].var == None:
                return nessi_list.NessiList(len(obj.axis[pap].val))
            else:
                return obj.axis[pap].var
    elif (obj_type == list_type):
        return get_err2(obj[index],index,"number",axis,pap)
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
        pass
    
    try:
        obj.id
        return  SO_type
    except AttributeError:
        pass

    try:
        obj[0][0]
        return list_type
    except TypeError:
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

def get_map_so(obj1,obj2,index):
    """
    This function takes a SOM and returns the first SO for use in mapping. If
    the object is a SO, it is immediately returned.

    Parameters:
    ----------
    -> obj1 is a SOM, SO or tuple
    -> obj2 is a SOM, SO or tuple

    Returns:
    -------
    <- A mapping SO (can be None if obj is a tuple or empty
    """

    obj1_type = get_type(obj1)
    if obj2 == None:
        if obj1_type == SO_type:
            return obj1
        elif obj1_type == SOM_type:
            return obj1[index]
        else:
            return None

    obj2_type = get_type(obj2)

    if obj1_type == SO_type and obj2_type == SO_type:
        return obj1
    elif obj1_type == SO_type and obj2_type == num_type or \
             obj1_type == SO_type and obj2_type == list_type:
        return obj1
    elif obj1_type == num_type and obj2_type == SO_type or \
             obj1_type == list_type and obj2_type == SO_type:
        return obj2
    elif obj1_type == SOM_type and obj2_type == SOM_type:
        return obj1[index]
    elif obj1_type == SOM_type and obj2_type != SOM_type:
        return obj1[index]
    elif obj1_type != SOM_type and obj2_type == SOM_type:
        return obj2[index]
    else:
        return None


def copy_som_attr(result, res_descr, obj1, obj1_descr,
                  obj2=None, obj2_descr=None, force=1):
    """
    This function takes a result object and one or two other arbitrary
    objects and copies the attributes from the objects to the result object if
    the arbitrary objects are SOMs.

    Parameters:
    ----------
    -> result is SOM, SO or tuple
    -> res_descr is the descriptor for the result object
    -> obj1 is SOM, SO or tuple
    -> obj1_descr is the descriptor for the obj1 object
    -> obj2 (OPTIONAL) is SOM, SO or tuple
    -> obj2_descr (OPTIONAL) is the descriptor for the obj2 object
    -> force (OPTIONAL) is a flag that says which object to copy last

    Returns:
    -------
    <- A SOM with copied attributes
    """

    if res_descr != SOM_type:
        return result

    if force == 1:
        if obj2 != None and obj2_descr == SOM_type:
            result.copyAttributes(obj2)
        if obj1_descr == SOM_type:
            result.copyAttributes(obj1)
    else:
        if obj1_descr == SOM_type:
            result.copyAttributes(obj1)
        if obj2 != None and obj2_descr == SOM_type:
            result.copyAttributes(obj2)

    return result


def get_parameter(param,so,inst):
    """
    This function takes a parameter string, a SO and an Instrument and returns
    the appropriate parameter based on the parameter string. The SO is used
    to obtain the spectrum ID for the Instrument object.

    Parameters:
    ----------
    -> param is the string containing the requested parameter
    -> so is the required SO for the id
    -> inst is the instrument object from which to fetch the parameter
       information

    Returns:
    -------
    <- The result parameter and its associated error in a tuple

    Exceptions:
    ----------
    <- RuntimeError is raised is a SO is not passed
    """

    try:
        so.id
    except AttributeError:
        raise RuntimeError, "Wrong object for function call. Please pass a "\
              +"SO."

    if param == "az" or param == "azimuthal":
        return inst.get_azimuthal(so.id)
    elif param == "polar":
        return inst.get_polar(so.id)
    elif param == "primary":
        return inst.get_primary(so.id)
    elif param == "secondary":
        return inst.get_secondary(so.id)
    else:
        raise RuntimeError, "Parameter %s is not an understood type." % \
              param
         
