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

def tof_to_wavelength(obj, **kwargs):
    """
    This function converts a primary axis of a C{SOM} or C{SO} from
    time-of-flight to wavelength. The wavelength axis for a C{SOM} must be in
    units of I{microseconds}. The primary axis of a C{SO} is assumed to be in
    units of I{microseconds}. A C{tuple} of C{(tof, tof_err2)} (assumed to be
    in units of I{microseconds}) can be converted to C{(wavelength,
    wavelength_err2)}.

    @param obj: Object to be converted
    @type obj: C{SOM.SOM}, C{SOM.SO} or C{tuple}
    
    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword pathlength: The pathlength and its associated error^2
    @type pathlength: C{tuple} or C{list} of C{tuple}s

    @keyword inst_param: The type of parameter requested from an associated
                         instrument. For this function the acceptable
                         parameters are I{primary}, I{secondary} and I{total}.
                         Default is I{primary}.
    @type inst_param: C{string}

    @keyword lojac: A flag that allows one to turn off the calculation of the
                    linear-order Jacobian. The default action is I{True} for
                    histogram data.
    @type lojac: C{boolean}

    @keyword units: The expected units for this function. The default for this
                    function is I{microseconds}.
    @type units: C{string}
 

    @return: Object with a primary axis in time-of-flight converted to
             wavelength
    @rtype: C{SOM.SOM}, C{SOM.SO} or C{tuple}


    @raise TypeError: The incoming object is not a type the function recognizes
    
    @raise RuntimeError: The C{SOM} x-axis units are not I{microseconds}
    
    @raise RuntimeError: A C{SOM} does not contain an instrument and no
                         pathlength was provided
                         
    @raise RuntimeError: No C{SOM} is provided and no pathlength given
    """

    # import the helper functions
    import hlr_utils

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj)
    o_descr = hlr_utils.get_descr(obj)

    # Setup keyword arguments
    try:
        inst_param = kwargs["inst_param"]
    except KeyError:
        inst_param = "primary"

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

    # Primary axis for transformation. If a SO is passed, the function, will
    # assume the axis for transformation is at the 0 position
    if o_descr == "SOM":
        axis = hlr_utils.one_d_units(obj, units)
    else:
        axis = 0

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)
    if res_descr == "SOM":
        result = hlr_utils.force_units(result, "Angstroms", axis)
        result.setAxisLabel(axis, "wavelength")
        result.setYUnits("Counts/A")
        result.setYLabel("Intensity")
    else:
        pass

    if pathlength is not None:
        p_descr = hlr_utils.get_descr(pathlength)
    else:
        if o_descr == "SOM":
            try:
                obj.attr_list.instrument.get_primary()
                inst = obj.attr_list.instrument
            except RuntimeError:
                raise RuntimeError("A detector was not provided")
        else:
            raise RuntimeError("If no SOM is provided, then pathlength "\
                               +"information must be provided")

    # iterate through the values
    import axis_manip
    if lojac:
        import utils
    
    for i in xrange(hlr_utils.get_length(obj)):
        val = hlr_utils.get_value(obj, i, o_descr, "x", axis)
        err2 = hlr_utils.get_err2(obj, i, o_descr, "x", axis)

        map_so = hlr_utils.get_map_so(obj, None, i)

        if pathlength is None:
            (pl, pl_err2) = hlr_utils.get_parameter(inst_param, map_so, inst)
        else:
            pl = hlr_utils.get_value(pathlength, i, p_descr)
            pl_err2 = hlr_utils.get_err2(pathlength, i, p_descr)

        value = axis_manip.tof_to_wavelength(val, err2, pl, pl_err2)

        if lojac:
            y_val = hlr_utils.get_value(obj, i, o_descr, "y")
            y_err2 = hlr_utils.get_err2(obj, i, o_descr, "y")
            counts = utils.linear_order_jacobian(val, value[0],
                                                 y_val, y_err2)
            hlr_utils.result_insert(result, res_descr, counts, map_so,
                                    "all", axis, [value[0]])

        else:
            hlr_utils.result_insert(result, res_descr, value, map_so,
                                    "x", axis)

    return result


if __name__ == "__main__":
    import hlr_test
    import SOM

    pli = (20.0, 0.1)

    som1 = hlr_test.generate_som()
    som1.setAllAxisUnits(["microseconds"])
    som1.attr_list.instrument = SOM.ASG_Instrument()

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** tof_to_wavelength"
    print "* tof_to_wavelength som :", tof_to_wavelength(som1)
    print "* tof_to_wavelength so  :", tof_to_wavelength(som1[0],
                                                         pathlength=pli)
    print "* tof_to_wavelength scal:", tof_to_wavelength([1, 1],
                                                         pathlength=pli)
