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

def igs_energy_transfer(obj, **kwargs):
    """
    This function takes a SOM or a SO and calculates the energy transfer for
    the IGS class of instruments. It is different from
    common_lib.energy_transfer in that the final wavelength is provided in a
    SOM.Information, SOM.CompositeInformation or a tuple, then converted to
    energy in place before being given to the common_lib.energy_transfer
    function.

    Parameters:
    ----------
    -> obj
    -> kwargs is a list of key word arguments that the function accepts:
          units= a string containing the expected units for this function.
                 The default for this function is meV
          lambda_f= a SOM.Information, SOM.CompositeInformation or a tuple
                    containing the final wavelength information
          offset= a SOM.Information or SOM.CompositeInformation containing
                  the final energy offsets

    Returns:
    -------
    <- A SOM or SO with the energy transfer calculated in units of THz

    Exceptions:
    ----------
    <- RuntimeError is raised if the x-axis units are not meV
    <- RuntimeError is raised if a SOM or SO is not given to the function
    <- RuntimeError is raised if the final wavelength is not provided to the
       function
    """

    # import the helper functions
    import hlr_utils

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj)
    o_descr = hlr_utils.get_descr(obj)

    if o_descr == "number" or o_descr == "list":
        raise RuntimeError, "Must provide a SOM of a SO to the function."
    # Go on
    else:
        pass

    # Setup keyword arguments
    try:
        units = kwargs["units"]
    except KeyError:
        units = "meV"

    try:
        lambda_f = kwargs["lambda_f"]
    except KeyError:
        lambda_f = None

    try:
        offset = kwargs["offset"]
    except KeyError:
        offset = None

        
    # Primary axis for transformation. If a SO is passed, the function, will
    # assume the axis for transformation is at the 0 position
    if o_descr == "SOM":
        axis = hlr_utils.hlr_1D_units(obj, units)
    else:
        axis = 0

    if lambda_f is None:
        if o_descr == "SOM":
            try:
                lambda_f = obj.attr_list["Wavelength_final"]
            except KeyError:
                raise RuntimeError("Must provide a final wavelength via the "\
                                   +"incoming SOM or the lambda_f keyword")
        else:
            raise RuntimeError("Must provide a final wavelength via the "\
                                   +"lambda_f keyword")
    else:
        pass
    

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)
    if res_descr == "SOM":
        result = hlr_utils.hlr_force_units(result, "ueV", axis)
        result.setAxisLabel(axis, "energy_transfer")
        result.setYUnits("Counts/ueV")
        result.setYLabel("Intensity")
    else:
        pass

    # iterate through the values
    import array_manip
    import axis_manip

    for i in xrange(hlr_utils.get_length(obj)):
        val = hlr_utils.get_value(obj, i, o_descr, "x", axis)
        err2 = hlr_utils.get_err2(obj, i, o_descr, "x", axis)

        y_val = hlr_utils.get_value(obj, i, o_descr, "y", axis)
        y_err2 = hlr_utils.get_err2(obj, i, o_descr, "y", axis)
        
        map_so = hlr_utils.get_map_so(obj, None, i)
        
        l_f = hlr_utils.get_special(lambda_f, map_so)

        (E_f, E_f_err2) = axis_manip.wavelength_to_energy(l_f[0], l_f[1])

        if offset is not None:
            info = hlr_utils.get_special(offset, map_so)
            try:
                E_f_new = array_manip.add_ncerr(E_f, E_f_err2,
                                                info[0], info[1])
            except TypeError:
                # Have to do this since add_ncerr does not support
                # scalar-scalar operations
                value1 = E_f + info[0]
                value2 = E_f_err2 + info[1]
                E_f_new = (value1, value2)
        else:
            E_f_new = (E_f, E_f_err2)

        value = array_manip.sub_ncerr(val, err2, E_f_new[0], E_f_new[1])

        # Convert from meV to ueV
        value2 = array_manip.mult_ncerr(value[0], value[1], 1000.0, 0.0)
        value3 = array_manip.mult_ncerr(y_val, y_err2, 1.0/1000.0, 0.0)

        hlr_utils.result_insert(result, res_descr, value3, map_so, "all",
                                0, [value2[0]])

    return result

if __name__ == "__main__":
    import hlr_test
    import SOM

    som1 = hlr_test.generate_som()
    som1.setAllAxisUnits(["meV"])

    l_f = SOM.Information([7.0], [0.1], "Angstroms", "ZSelector")
    som1.attr_list["Wavelength_final"] = l_f
    
    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** igs_energy_transfer"
    print "* som:", igs_energy_transfer(som1)
    print "* so:", igs_energy_transfer(som1[0], lambda_f=l_f)


   
