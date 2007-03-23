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

def energy_to_wavelength(obj, **kwargs):
    """
    This function converts a primary axis of a SOM or SO from energy
    to wavelength. The energy axis for a SOM must be in units of meV.
    The primary axis of a SO is assumed to be in units of meV. A tuple
    of [energy, energy_err2] (assumed to be in units of meV) can
    be converted to [wavelength, wavelength_err2].

    Parameters:
    ----------
    -> obj is the SOM, SO or tuple to be converted
    -> kwargs is a list of key word arguments that the function accepts:
          lojac=<boolean> is a flag that allows one to turn off the
                          calculation of the linear-order Jacobian. The
                          default action is True for histogram data.
           units= a string containing the expected units for this function.
                 The default for this function is meV

    Return:
    ------
    <- A SOM or SO with a primary axis in energy or a tuple converted to
       wavelength

    Exceptions:
    ----------
    <- TypeError is raised if the incoming object is not a type the function
       recognizes
    <- RuntimeError is raised if the SOM x-axis units are not meV
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
        units = kwargs["units"]
    except KeyError:
        units = "meV"

    try:
        lojac = kwargs["lojac"]
    except KeyError:
        lojac = hlr_utils.check_lojac(obj)

    # Primary axis for transformation. If a SO is passed, the function, will
    # assume the axis for transformation is at the 0 position
    if o_descr == "SOM":
        axis = hlr_utils.hlr_1D_units(obj, units)
    else:
        axis = 0

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)
    if res_descr == "SOM":
        result = hlr_utils.hlr_force_units(result, "Angstroms", axis)
        result.setAxisLabel(axis, "wavelength")
        result.setYUnits("Counts/Angstrom")
        result.setYLabel("Intensity")
    else:
        pass

    # iterate through the values
    import array_manip
    import axis_manip
    if lojac:
        import utils

    for i in xrange(hlr_utils.get_length(obj)):
        val = hlr_utils.get_value(obj, i, o_descr, "x", axis)
        err2 = hlr_utils.get_err2(obj, i, o_descr, "x", axis)

        map_so = hlr_utils.get_map_so(obj, None, i)

        value = axis_manip.energy_to_wavelength(val, err2)

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

    som1 = hlr_test.generate_som()
    som1.setAllAxisUnits(["meV"])

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** energy_to_wavelength"
    print "* som  :", energy_to_wavelength(som1)
    print "* so   :", energy_to_wavelength(som1[1])
    print "* scal :", energy_to_wavelength((1, 1))
