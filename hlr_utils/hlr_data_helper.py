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
SOM_type = "SOM"
SO_type = "SO"
list_type = "list"
num_type = "number"
empty_type = ""

def empty_result(obj1, obj2=None):
    """
    This function inspects the arguments and returns an appropriate
    return type for an operation using the arguments. The object can
    be filled using L{result_insert}.

    @param obj1: The first object to be inspected
    @type obj1: C{SOM.SOM}, C{SOM.SO} or C{tuple}
    
    @param obj2: (OPTIONAL) The second object to be inspected
    @type obj2: C{SOM.SOM}, C{SOM.SO} or C{tuple}

    
    @return: A C{tuple} containing the requested object (C{SOM}, C{SO} or
             C{tuple}) and the corresponding descriptor
    @rtype: C{tuple}
    """

    obj1_type = get_type(obj1)

    if obj2 is None:
        if obj1_type == SOM_type:
            return (SOM.SOM(), SOM_type)
        elif obj1_type == SO_type:
            return (SOM.SO(obj1.dim()), SO_type)
        elif obj1_type == list_type:
            return ([], list_type)
        else:
            return ([], num_type)
    # If obj2 is not None, go on.
    else:
        pass
    
    obj2_type = get_type(obj2)

    if obj1_type == SOM_type or obj2_type == SOM_type:
        return (SOM.SOM(), SOM_type)
    elif obj1_type == SO_type or obj2_type == SO_type:
        if obj1_type == SO_type:
            return (SOM.SO(obj1.dim()), SO_type)
        elif obj2_type == SO_type:
            return (SOM.SO(obj2.dim()), SO_type)
    elif obj1_type == list_type or obj2_type == list_type:
        return ([], list_type)
    else:
        return ([], num_type)

def result_insert(result, descr, value, map_so, axis="y", pap=0, xvals=None):
    """
    This function takes value and puts it into the result in an
    appropriate fashion. The description is used for decision making.

    @param result: Object used for insertion
    @type result: C{SOM.SOM}, C{SOM.SO}, C{list} or C{tuple}
    
    @param descr: The object descriptor
    @type descr: C{string}
    
    @param value: Information to be place in result directly or an object that
    will be placed into result
    @type value: C{tuple}
    
    @param map_so: A C{SO} that has information that will be mapped to a C{SO}
    if result is either a C{SOM} or a C{SO}
    @type map_so: C{SOM.SO}
    
    @param axis: (OPTIONAL) The axis from which to grab the values. The
                            possible values are I{y} (copy id and axis, insert
                            y and var_y), I{x} (copy id, y and var_y, insert
                            axis), I{yonly} (copy id, axis and var_y, insert
                            y) and I{all} (insert id, axis, y and var_y).
    @type axis: C{string}
    
    @param pap: (OPTIONAL) The primary axis position. This is used to pull the
    value from the correct primary axis position.
    @type pap: C{int}
    
    @param xvals: (OPTIONAL) A C{list} of x-axes that are not provided by
    either value or map_so
    @type xvals: C{list}


    @return: Object with the provided information inserted
    @rtype: C{SOM.SOM}, C{SOM.SO} or C{tuple}
    """

    import copy
    
    if descr is None:
        result_type = get_type(result)
    else:
        result_type = descr

    if result_type == SOM_type:
        if map_so is not None:
            so = SOM.SO(map_so.dim())
            
        if axis.lower() == "y" or axis.lower() == "yonly":
            result_insert(so, None, value, map_so, axis, pap, xvals)
            result.append(so)
        elif axis.lower() == "x":
            result_insert(so, None, value, map_so, axis, pap, xvals)
            result.append(so)
        elif axis.lower() == "all":
            if map_so is not None:
                result_insert(so, None, value, map_so, axis, pap, xvals)
                result.append(so)
            else:
                result.append(value)
                
    elif result_type == SO_type:
        if axis.lower() == "y" or axis.lower() == "yonly":
            result.y = value[0]
            result.var_y = value[1]
            result.id = map_so.id
            if not axis.lower() == "yonly":
                result.axis = copy.deepcopy(map_so.axis)

        elif axis.lower() == "x":
            result.id = map_so.id
            result.y = copy.deepcopy(map_so.y)
            result.var_y = copy.deepcopy(map_so.var_y)
            for i in range(map_so.dim()):
                if i == pap:
                    result.axis[pap].val = value[0]
                    if map_so.axis[pap].var is not None:
                        result.axis[pap].var = value[1]
                else:
                    result.axis[i].val = copy.deepcopy(map_so.axis[i].val)
                    if map_so.axis[i].var is not None:
                        result.axis[i].var = copy.deepcopy(map_so.axis[i].var)

        elif axis.lower() == "all":
            if map_so is not None:
                result.id = map_so.id
                result.y = value[0]
                result.var_y = value[1]
                axis_number = 0
                for i in range(len(xvals)):
                    if i % 2 == 0:
                        result.axis[axis_number].val = xvals[i]
                    else:
                        # Assumes x data given as (x1, x2, x3, ...)
                        if map_so.axis[axis_number].var is None:
                            axis_number += 1
                            result.axis[axis_number].val = xvals[i]
                            axis_number += 1
                        # Assumes x data given as (x1, ex1, x2, ex2, ...)
                        else:
                            result.axis[axis_number].var = xvals[i]
                            axis_number += 1

            else:
                result.id = value.id
                result.y = copy.deepcopy(value.y)
                result.var_y = copy.deepcopy(value.var_y)
                result.axis = copy.deepcopy(value.axis)

    elif result_type == num_type:
        result.append(value[0])
        result.append(value[1])
        # Note: the following call does not do what is expected. The result
        # object returns from this function as a list and not as the expected
        # tuple. The way to correct this is to return the result object
        # directly. This will result in a major feature change for many
        # functions, so it should go into the ITC2 release.
        result = tuple(result)

    elif result_type == list_type:
        if axis.lower() == "all":
            result.append(tuple(value))
        else:
            result.append((value[0], value[1]))
    else:
        raise TypeError("Object type not recognized by result_insert "\
                        +"function.")

def get_length(obj1, obj2=None):
    """
    This function returns the length appropriate for iterating
    through the objects.

    @param obj1: First object for length checking
    @type obj1: C{SOM.SOM}, C{SOM.SO} or C{tuple}
    
    @param obj2: (OPTIONAL) Second object for length checking
    @type obj2: C{SOM.SOM}, C{SOM.SO} or C{tuple}


    @return: The iteration length of the top hierarchy object (C{SOM} > C{SO}
    or C{tuple})
    @rtype: C{int}


    @raise IndexError: The two incoming objects are C{SOM}s and the number of
                       C{SO}s in them are not equal
                       
    @raise RuntimeError: One or both objects are C{None}
    """

    if obj2 is None:
        obj1_type = get_descr(obj1)
        obj2_type = empty_type
    else:
        (obj1_type, obj2_type) = get_descr(obj1, obj2)
        
    if obj1_type == SOM_type and obj2_type == SOM_type:
        if len(obj1) != len(obj2):
            raise IndexError("Can only add SOMs with same number of spectra")
        return len(obj1)
    elif obj1_type == SOM_type and obj2_type != SOM_type:
        return len(obj1)
    elif obj1_type != SOM_type and obj2_type == SOM_type:
        return len(obj2)
    elif obj1_type == empty_type and obj2_type == empty_type:
        raise RuntimeError("One or two objects need to be defined.")
    elif obj1_type == list_type or obj2_type == list_type:
        if obj1_type == list_type:
            return len(obj1)
        elif obj2_type == list_type:
            return len(obj2)
        else:
            raise RuntimeError("hlr_utils.get_length: Should never get here!")
    elif obj1_type != SOM_type and obj2_type != SOM_type:
        return 1
    else:
        return 1

def get_descr(obj1, obj2=None):
    """
    This function takes one or two arbitrary objects and returns the descriptor
    for those objects.

    @param obj1: First object for descriptor retrieval
    @type obj1: C{SOM.SOM}, C{SOM.SO} or C{tuple}
    
    @param obj2: (OPTIONAL) Second object for descriptor retrieval
    @type obj2: C{SOM.SOM}, C{SOM.SO} or C{tuple}


    @return: A single descriptor or a C{tuple} of the descriptors for both
             objects
    @rtype: C{string} or C{tuple}
    """

    if obj2 is None:
        return get_type(obj1)
    else:
        return (get_type(obj1), get_type(obj2))

def get_value(obj, index=0, descr=None, axis="y", pap=0):
    """
    This function takes an arbitrary object and returns the value for
    the given index. If the object is not a collection the index is
    ignored.

    @param obj: Object from which to retrieve value 
    @type obj: C{SOM.SOM}, C{SOM.SO} or C{tuple}
    
    @param index: A possible index for use in a C{SOM}
    @type index: C{int}
    
    @param descr: (OPTIONAL) The object descriptor, default is C{None}
    @type descr: C{string}
    
    @param axis: (OPTIONAL) The axis from which to grab the value
    @type axis: C{string}=<y or x>
    
    @param pap: (OPTIONAL) The primary axis position. This is used to pull the
                           value from the correct axis position in a
                           multidimensional object.
    @type pap: C{int}   


    @return: The appropriate object containing the value
    @rtype: C{nessi_list.NessiList} or C{float}


    @raise TypeError: obj is not a recognized type
    """
    
    if descr is None:
        obj_type = get_type(obj)
    else:
        obj_type = descr

    if obj_type == SOM_type:
        return get_value(obj[index], index, "SO", axis, pap)
    elif obj_type == SO_type:
        if axis.lower() == "y":
            return obj.y
        elif axis.lower() == "x":
            return obj.axis[pap].val
        elif axis.lower() == "all":
            return obj
    elif obj_type == list_type:
        return get_value(obj[index], index, "number", axis, pap)
    elif obj_type == num_type:
        if axis.lower() == "all":
            return obj
        else:
            return obj[0]
    else:
        raise TypeError("Object type not recognized by get_value function.")

def get_err2(obj, index, descr=None, axis="y", pap=0):
    """
    This function takes an arbitrary object and returns the uncertainty
    squared for the given index. If the object is not a collection the index
    is ignored.

    @param obj: Object from which to retrieve error^2 
    @type obj: C{SOM.SOM}, C{SOM.SO} or C{tuple}
    
    @param index: A possible index for use in a C{SOM}
    @type index: C{int}
    
    @param descr: (OPTIONAL) The object descriptor, default is C{None}
    @type descr: C{string}
    
    @param axis: (OPTIONAL) The axis from which to grab the error^2
    @type axis: C{string}=<y or x>
    
    @param pap: (OPTIONAL) The primary axis position. This is used to pull the
                           error^2 from the correct axis position in a
                           multidimensional object.
    @type pap: C{int}   


    @return: The appropriate object containing the error^2
    @rtype: C{nessi_list.NessiList} or C{float}


    @raise TypeError: obj is not a recognized type
    """

    if descr is None:
        obj_type = get_type(obj)
    else:
        obj_type = descr

    if obj_type == SOM_type:
        return get_err2(obj[index], index, "SO", axis, pap)
    elif obj_type == SO_type:
        if axis.lower() == "y":
            return obj.var_y
        elif axis.lower() == "x":
            if obj.axis[pap].var is None:
                return nessi_list.NessiList(len(obj.axis[pap].val))
            else:
                return obj.axis[pap].var
    elif obj_type == list_type:
        return get_err2(obj[index], index, "number", axis, pap)
    elif obj_type == num_type:
        return obj[1]
    else:
        raise TypeError("Object type not recognized by get_err2 function.")

def get_type(obj):
    """
    This function taks an arbitraray object and returns the descriptor for
    the object.

    @param obj: Object for descriptor determination
    @type obj: C{SOM.SOM}, C{SOM.SO} or C{tuple}


    @return: The descriptor for the corresponding object
    @rtype: C{string}
    """
    
    if obj is None:
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

def swap_args(left, right):
    """
    This function takes two arguments and returns the objects in the reversed
    positions.

    @param left: The object to be swapped to the right position
    @type left: C{SOM.SOM}, C{SOM.SO}, C{list} of C{tuple}s or C{tuple}
    
    @param right: The object to be swapped to the left position
    @type right: C{SOM.SOM}, C{SOM.SO}, C{list} of C{tuple}s or C{tuple}


    @return: The incoming objects in the swapped locations
    @rtype: C{tuple}
    """

    temp = left
    left = right
    right = temp

    return (left, right)

def get_map_so(obj1, obj2, index):
    """
    This function takes a C{SOM} and returns the first C{SO} for use in
    mapping. If the object is a C{SO}, it is immediately returned.

    @param obj1: Object from which to retrieve mapping object
    @type obj1: C{SOM.SOM}, C{SOM.SO} or C{tuple}
    
    @param obj2: Object from which to retrieve mapping object
    @type obj2: C{SOM.SOM}, C{SOM.SO} or C{tuple}


    @return: A mapping object (can be C{None} if obj is a C{tuple} or empty)
    @rtype: C{SOM.SO}
    """

    obj1_type = get_type(obj1)
    if obj2 is None:
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
                  obj2=None, obj2_descr=None, force=1, add_nxpars=False):
    """
    This function takes a result object and one or two other arbitrary
    objects and copies the attributes from the objects to the result object if
    the arbitrary objects are C{SOM}s.

    @param result: Object to have its attributes copied
    @type result: C{SOM.SOM}, C{SOM.SO} or C{tuple}
    
    @param res_descr: The descriptor for the result object
    @type res_descr: C{string}
    
    @param obj1: First object for attribute copying
    @type obj1: C{SOM.SOM}, C{SOM.SO} or C{tuple}
    
    @param obj1_descr: The descriptor for the obj1 object
    @type obj1_descr: C{string}

    @param obj2: (OPTIONAL) Second object for attribute copying
    @type obj2: C{SOM.SOM}, C{SOM.SO} or C{tuple}
    
    @param obj2_descr: (OPTIONAL) The descriptor for the obj2 object
    @type obj2_descr: C{string}    

    @param force: (OPTIONAL) Flag that says which object to copy last
    @type force: C{boolean}
    
    @param add_nxpars: (OPTIONAL) Flag that determines if C{NxParameters} in
                                  the attribute list are added
    @type add_nxpars: C{boolean}

                             
    @return: Object with copied attributes
    @rtype: C{SOM.SOM} 
    """

    if res_descr != SOM_type:
        return result

    if force == 1:
        if obj2 is not None and obj2_descr == SOM_type:
            result.copyAttributes(obj2, add_nxpars)
        if obj1_descr == SOM_type:
            result.copyAttributes(obj1, add_nxpars)
    else:
        if obj1_descr == SOM_type:
            result.copyAttributes(obj1, add_nxpars)
        if obj2 is not None and obj2_descr == SOM_type:
            result.copyAttributes(obj2, add_nxpars)

    return result

def get_parameter(param, so, inst):
    """
    This function takes a parameter string, a SO and an Instrument and returns
    the appropriate parameter based on the parameter string. The SO is used
    to obtain the spectrum ID for the Instrument object.

    @param param: The requested parameter
    @type param: C{string}
    
    @param so: The required C{SO} for the id
    @type so: C{SOM.SO}
    
    @param inst: Object from which to fetch the parameter information
    @type inst: C{SOM.Instrument} or C{SOM.CompositeInstrument}


    @return: The parameter and its associated error^2
    @rtype: C{tuple}


    @raise RuntimeError: A C{SO} is not passed to the function
    """

    try:
        so.id
    except AttributeError:
        raise RuntimeError("Wrong object for function call. Please pass a "\
                           +"SO.")

    if param == "az" or param == "azimuthal":
        return inst.get_azimuthal(so.id)
    elif param == "polar":
        return inst.get_polar(so.id)
    elif param == "primary":
        return inst.get_primary(so.id)
    elif param == "secondary":
        return inst.get_secondary(so.id)
    elif param == "total":
        return inst.get_total_path(so.id)
    elif param == "x-offset":
        return inst.get_x_pix_offset(so.id)
    elif param == "y-offset":
        return inst.get_y_pix_offset(so.id)
    elif param == "radius":
        return inst.get_radius(so.id)
    elif param in inst.get_diff_geom_keys():
        return inst.get_diff_geom(param, so.id)
    else:
        raise RuntimeError("Parameter %s is not an understood type." % \
                           param)

def get_special(info, so):
    """
    This function takes an information object and returns the appropriate
    information for the pixel ID contained in the C{SO}. If the information
    object in not an C{Information} object, but a C{tuple}, the function
    handles that case by just returning the C{tuple}.

    @param info: Object containing values and errors associated with the
                 particular information
    @type info: C{SOM.Information}, C{SOM.CompositeInformation} or C{tuple}
    
    @param so: Object that contains the spectrum ID to interrogate the info
               object for its information
    @type so: C{SOM.SO}


    @return: A object containing the value and error^2 of the information
    @rtype: C{tuple}
    """

    try:
        return info.get_value(so.id)
    except AttributeError:
        return info

def check_lojac(obj):
    """
    This function takes an data set and determines if the linear-order
    Jacobian (lojac) should be calculated.

    @param obj: Object to check if lojac should be calculated
    @type obj: C{SOM.SOM}, C{SOM.SO}, C{list} of C{tuple}s or a C{tuple}


    @return: Determination for the calculation of lojac
    @rtype: C{boolean}
    """

    descr = get_type(obj)

    if descr == "SOM":
        if obj.getDataSetType() != "histogram":
            return False
        else:
            return True
    elif descr == "SO":
        if len(obj) == len(obj.axis[0].val) - 1:
            return True
        elif len(obj) == len(obj.axis[0].val):
            return False
        else:
            return False
    else:
        return False

def get_ref_integration_direction(direc, inst_name, inst):
    """
    This function finds the integration direction and the central pixel for
    the I{REF_L} and I{REF_M} instruments. If direc is C{None}, the default
    behavior is the y direction for I{REF_L} and the x direction for I{REF_M}.

    @param direc: The direction of the integration. This should be either I{x}
                  or I{y}.
    @type direc: C{string}

    @param inst_name: The name of the reflectometer.
    @type inst_name: C{string}

    @param inst: The instrument geometry for the detector
    @type inst: C{SOM.Instrument}

    @return: The direction of integration and the central pixel for the
             opposing direction. This direction of integration is C{True} for
             y and C{False} for x.
    @rtype: C{tuple} of (C{boolean}, C{int})
    """
    if inst_name is None or inst_name == "":
        raise RuntimeError("You need to specify a reflectometer instrument "\
                           +"name for this function.")

    if direc is None:
        if inst_name == "REF_L":
            int_dir = True
        if inst_name == "REF_M":
            int_dir = False
    else:
        if direc == "x":
            int_dir = False
        if direc == "y":
            int_dir = True

    # Get the detector direction opposite the integration direction
    if int_dir:
        cpixel = inst.get_num_x()
    else:
        cpixel = inst.get_num_y()

    # Make this the centerline value (to low side)
    cpixel = (cpixel / 2) - 1

    return (int_dir, cpixel)

def scale_proton_charge(ipc, scale_units):
    """
    This function takes a proton charge and scales it to either Coulombs
    (I{C}), milliCoulombs (I{mC}) or microCoulombs (I{uC}).

    @param ipc: The proton charge to be scaled
    @type ipc: C{SOM.NxParameter}

    @param scale_units: The short units to scale the proton charge into
    @type scale_units: C{string}


    @return: The scaled proton charge
    @rtype: C{SOM.NxParameter}
    """
    scale_info = {"C": {"scale": 1.0e-12, "units": "Coulomb"},
                  "mC": {"scale": 1.0e-9, "units": "milliCoulomb"},
                  "uC": {"scale": 1.0e-6, "units": "microCoulomb"}}

    pc_new = ipc.getValue() * scale_info[scale_units]["scale"]

    return SOM.NxParameter(pc_new, scale_info[scale_units]["units"])
