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

def tof_to_ref_scalar_Q(obj, **kwargs):
    """
    This function converts a primary axis of a C{SOM} or C{SO} from
    time-of-flight to reflectometer scalar Q. This means that a single angle
    and a single flightpath is used. The time-of-flight axis for a C{SOM} must
    be in units of I{microseconds}. The primary axis of a C{SO} is assumed to
    be in units of I{microseconds}. A C{tuple} of C{(time-of-flight,
    time-of-flight_err2)} (assumed to be in units of I{microseconds}) can be
    converted to C{(scalar_Q, scalar_Q_err2)}.

    @param obj: Object to be converted
    @type obj: C{SOM.SOM}, C{SOM.SO} or C{tuple}
    
    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword polar: The polar angle and its associated error^2
    @type polar: C{tuple}
    
    @keyword pathlength: The pathlength and its associated error^2
    @type pathlength: C{tuple}

    @keyword angle_offset: A constant offset for the polar angle and its
                           associated error^2. The units of the offset should
                           be in radians.
    @type angle_offset: C{tuple}

    @keyword lojac: A flag that allows one to turn off the calculation of the
                    linear-order Jacobian. The default action is True for
                    histogram data.
    @type lojac: C{boolean}    
    
    @keyword units: The expected units for this function. The default for this
                    function is I{microseconds}.
    @type units: C{string}
 

    @return: Object with a primary axis in time-of-flight converted to
             reflectometer scalar Q
    @rtype: C{SOM.SOM}, C{SOM.SO} or C{tuple}


    @raise TypeError: The incoming object is not a type the function recognizes
    
    @raise RuntimeError: A C{SOM} is not passed and no polar angle is provided
    
    @raise RuntimeError: The C{SOM} x-axis units are not I{microseconds}
    """
    
    # import the helper functions
    import hlr_utils

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj)
    o_descr = hlr_utils.get_descr(obj)

    if o_descr == "list":
        raise TypeError("Do not know how to handle given type: %s" % \
                        o_descr)
    else:
        pass

    # Setup keyword arguments
    try:
        polar = kwargs["polar"]
    except KeyError:
        polar = None

    try:
        pathlength = kwargs["pathlength"]
    except KeyError:
        pathlength = None

    try:
        units = kwargs["units"]
    except KeyError:
        units = "microseconds"

    try:
        lojac = kwargs["lojac"]
    except KeyError:
        lojac = hlr_utils.check_lojac(obj)

    try:
        angle_offset = kwargs["angle_offset"]
    except KeyError:
        angle_offset = None
        
    # Primary axis for transformation. If a SO is passed, the function, will
    # assume the axis for transformation is at the 0 position
    if o_descr == "SOM":
        axis = hlr_utils.one_d_units(obj, units)
    else:
        axis = 0

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)
    if res_descr == "SOM":
        result = hlr_utils.force_units(result, "1/Angstroms", axis)
        result.setAxisLabel(axis, "scalar wavevector transfer")
        result.setYUnits("Counts/A-1")
        result.setYLabel("Intensity")
    else:
        pass

    if pathlength is None or polar is None:
        if o_descr == "SOM":
            try:
                obj.attr_list.instrument.get_primary()
                inst = obj.attr_list.instrument
            except RuntimeError:
                raise RuntimeError("A detector was not provided")
        else:
            if pathlength is None and polar is None:
                raise RuntimeError("If no SOM is provided, then pathlength "\
                                   +"and polar angle information must be "\
                                   +"provided")
            elif pathlength is None:
                raise RuntimeError("If no SOM is provided, then pathlength "\
                                   +"information must be provided")
            elif polar is None:
                raise RuntimeError("If no SOM is provided, then polar angle "\
                                   +"information must be provided")
            else:
                raise RuntimeError("If you get here, see Steve Miller for "\
                                   +"your mug.")
    else:
        pass

    if pathlength is None:
        (pl, pl_err2) = obj.attr_list.instrument.get_total_path(obj[0].id,
                                                             det_secondary=True)
    else:
        (pl, pl_err2) = pathlength

    if polar is None:
        # Function returns 3-tuple, only need first to elements
        (angle, angle_err2) = hlr_utils.get_special(obj.attr_list["Theta"],
                                                    obj[0])[:2]
    else:
        (angle, angle_err2) = polar

    if angle_offset is not None:
        angle += angle_offset[0]
        angle_err2 += angle_offset[1]
        
    # iterate through the values
    import axis_manip
    if lojac:
        import utils

    for i in xrange(hlr_utils.get_length(obj)):
        val = hlr_utils.get_value(obj, i, o_descr, "x", axis)
        err2 = hlr_utils.get_err2(obj, i, o_descr, "x", axis)

        map_so = hlr_utils.get_map_so(obj, None, i)

        value = axis_manip.tof_to_scalar_Q(val, err2, pl, pl_err2, angle,
                                           angle_err2)

        if lojac:
            y_val = hlr_utils.get_value(obj, i, o_descr, "y")
            y_err2 = hlr_utils.get_err2(obj, i, o_descr, "y")
            counts = utils.linear_order_jacobian(val, value[0],
                                                 y_val, y_err2)
        else:
            pass

        if o_descr != "number":
            value1 = axis_manip.reverse_array_cp(value[0])
            value2 = axis_manip.reverse_array_cp(value[1])
            rev_value = (value1, value2)
        else:
            rev_value = value

        if map_so is not None:
            if not lojac:
                map_so.y = axis_manip.reverse_array_cp(map_so.y)
                map_so.var_y = axis_manip.reverse_array_cp(map_so.var_y)
            else:
                map_so.y = axis_manip.reverse_array_cp(counts[0])
                map_so.var_y = axis_manip.reverse_array_cp(counts[1])
        else:
            pass

        hlr_utils.result_insert(result, res_descr, rev_value, map_so, "x",
                                axis)

    return result

if __name__ == "__main__":
    import hlr_test
    import SOM

    ple = (20.0, 0.1)
    pa = (0.785, 0.005)
    ao = (0.785, 0.000)
    
    som1 = hlr_test.generate_som()
    som1.setAllAxisUnits(["microseconds"])
    som1.attr_list.instrument = SOM.ASG_Instrument()
    som1.attr_list["Theta"] = ao

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]
    
    print "********** tof_to_ref_scalar_Q"
    print "* tof_to_ref_scalar_Q som :", tof_to_ref_scalar_Q(som1)
    print "* tof_to_ref_scalar_Q so  :", tof_to_ref_scalar_Q(som1[0],
                                                     pathlength=ple,
                                                     polar=pa)
    print "* tof_to_ref_scalar_Q som (offset):", tof_to_ref_scalar_Q(som1,
                                                             angle_offset=ao)
