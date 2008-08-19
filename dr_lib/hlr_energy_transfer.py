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

def energy_transfer(obj, itype, axis_const, **kwargs):
    """
    This function takes a SOM with a wavelength axis (initial for IGS and
    final for DGS) and calculates the energy transfer.  

    @param obj: The object containing the wavelength axis
    @type obj: C{SOM.SOM}

    @param itype: The instrument class type. The choices are either I{IGS} or
                  I{DGS}.
    @type itype: C{string}

    @param axis_const: The attribute name for the axis constant which is the 
                         final wavelength for I{IGS} and the initial energy for
                         I{DGS}.
    @type axis_const: C{string}

    @param kwargs: A list of keyword arguments that the function accepts:

    @keyword units: The units for the incoming axis. The default is
                    I{Angstroms}.
    @type units: C{string}

    @keyword change_units: A flag that signals the function to convert from
                           I{meV} to I{ueV}. The default is I{False}.
    @type change_units: C{boolean}

    @keyword scale: A flag to scale the y-axis by lambda_f/lambda_i for I{IGS}
                    and lambda_i/lambda_f for I{DGS}. The default is I{False}.
    @type scale: C{boolean}
    

    @return: Object with the energy transfer calculated in units of I{meV} or
             I{ueV}. The default is I{meV}.
    @rtype: C{SOM.SOM}


    @raise RuntimeError: The instrument class type is not recognized
    @raise RuntimeError: The x-axis units are not Angstroms
    @raise RuntimeError: A SOM is not given to the function
    """
    # Check the instrument class type to make sure its allowed
    allowed_types = ["DGS", "IGS"]

    if itype not in allowed_types:
        raise RuntimeError("The instrument class type %s is not known. "\
                           +"Please use DGS or IGS" % itype)

    # import the helper functions
    import hlr_utils

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj)
    o_descr = hlr_utils.get_descr(obj)

    if o_descr != "SOM":
        raise RuntimeError("Must provide a SOM to the function.")
    # Go on
    else:
        pass

    # Setup keyword arguments
    try:
        units = kwargs["units"]
    except KeyError:
        units = "Angstroms"

    try:
        change_units = kwargs["change_units"]
    except KeyError:
        change_units = False       

    try:
        scale = kwargs["scale"]
    except KeyError:
        scale = False
        
    # Primary axis for transformation. 
    axis = hlr_utils.one_d_units(obj, units)

    # Get the subtraction constant
    try:
        axis_c = obj.attr_list[axis_const]
    except KeyError:
        raise RuntimeError("Must provide a final wavelength (IGS) or initial "\
                           +"energy (DGS) via the incoming SOM")
    
    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)
    if change_units:
        unit_str = "ueV"
    else:
        unit_str = "meV"
    result = hlr_utils.force_units(result, unit_str, axis)
    result.setAxisLabel(axis, "energy_transfer")
    result.setYUnits("Counts/" + unit_str)
    result.setYLabel("Intensity")

    # iterate through the values
    import array_manip
    import axis_manip
    import utils

    for i in xrange(hlr_utils.get_length(obj)):
        if itype == "IGS":
            l_i = hlr_utils.get_value(obj, i, o_descr, "x", axis)
            l_i_err2 = hlr_utils.get_err2(obj, i, o_descr, "x", axis)
        else:
            l_f = hlr_utils.get_value(obj, i, o_descr, "x", axis)
            l_f_err2 = hlr_utils.get_err2(obj, i, o_descr, "x", axis)
            
        y_val = hlr_utils.get_value(obj, i, o_descr, "y", axis)
        y_err2 = hlr_utils.get_err2(obj, i, o_descr, "y", axis)
        
        map_so = hlr_utils.get_map_so(obj, None, i)

        if itype == "IGS":
            (E_i, E_i_err2) = axis_manip.wavelength_to_energy(l_i, l_i_err2)
            l_f = hlr_utils.get_special(axis_c, map_so)[:2]
            (E_f, E_f_err2) = axis_manip.wavelength_to_energy(l_f[0], l_f[1])
        else:
            (E_i, E_i_err2) = axis_c.toValErrTuple()
            (E_f, E_f_err2) = axis_manip.wavelength_to_energy(l_f, l_f_err2)

        if scale:
            # Scale counts by lambda_f / lambda_i
            if itype == "IGS":
                (l_d, l_d_err2) = utils.calc_bin_centers(l_i, l_i_err2)
                (l_n, l_n_err2) = l_f
            # Scale counts by lambda_i / lambda_f                
            else:
                (l_d, l_d_err2) = utils.calc_bin_centers(l_f, l_f_err2)
                (l_n, l_n_err2) = axis_manip.energy_to_wavelength(E_i,
                                                                  E_i_err2)
                
            ratio = array_manip.div_ncerr(l_n, l_n_err2, l_d, l_d_err2)
            scale_y = array_manip.mult_ncerr(y_val, y_err2, ratio[0], ratio[1])
        else:
            scale_y = (y_val, y_err2)

        value = array_manip.sub_ncerr(E_i, E_i_err2, E_f, E_f_err2)

        if change_units:
            # Convert from meV to ueV
            value2 = array_manip.mult_ncerr(value[0], value[1], 1000.0, 0.0)
            value3 = array_manip.mult_ncerr(scale_y[0], scale_y[1],
                                            1.0/1000.0, 0.0)
        else:
            value2 = value
            value3 = scale_y

        # Reverse the values due to the conversion
        value_y = axis_manip.reverse_array_cp(scale_y[0])
        value_var_y = axis_manip.reverse_array_cp(scale_y[1])
        value_x = axis_manip.reverse_array_cp(value2[0])

        hlr_utils.result_insert(result, res_descr, (value_y, value_var_y),
                                map_so, "all", 0, [value_x])

    return result

if __name__ == "__main__":
    import hlr_test
    import SOM

    som1 = hlr_test.generate_som()
    som1.setAllAxisUnits(["Angstroms"])

    la_f = SOM.Information([7.0], [0.1], "Angstroms", "ZSelector")
    som1.attr_list["Wavelength_final"] = la_f
    
    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** energy_transfer"
    print "* som        :", energy_transfer(som1, "IGS", "Wavelength_final",
                                            change_units=True, scale=True)


   
