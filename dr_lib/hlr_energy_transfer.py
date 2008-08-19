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

def energy_transfer(obj, itype, lambda_const, **kwargs):
    """
    This function takes a SOM or a SO with a wavelength axis (initial for IGS
    and final for DGS) and calculates the energy transfer.  

    @param obj: The object containing the wavelength axis
    @type obj: C{SOM.SOM} or C{SOM.SO}

    @param itype: The instrument class type. The choices are either I{IGS} or
    I{DGS}.
    @type itype: C{string}

    @param lambda_const: The attribute name for the wavelength constant
                         (final for IGS and initial for DGS).
    @type lambda_const: C{string}

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
    @rtype: C{SOM.SOM} or C{SOM.SO}


    @raise RuntimeError: The instrument class type is not recognized
    @raise RuntimeError: The x-axis units are not Angstroms
    @raise RuntimeError: A SOM or SO is not given to the function
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

    if o_descr == "number" or o_descr == "list":
        raise RuntimeError("Must provide a SOM of a SO to the function.")
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

        
    # Primary axis for transformation. If a SO is passed, the function, will
    # assume the axis for transformation is at the 0 position
    if o_descr == "SOM":
        axis = hlr_utils.one_d_units(obj, units)
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
        result = hlr_utils.force_units(result, "ueV", axis)
        result.setAxisLabel(axis, "energy_transfer")
        result.setYUnits("Counts/ueV")
        result.setYLabel("Intensity")
    else:
        pass

    # iterate through the values
    import array_manip
    import axis_manip
    import utils

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

        # Scale counts by lambda_f / lambda_i
        if scale:
            l_i = axis_manip.energy_to_wavelength(val, err2)

            l_i_bc = utils.calc_bin_centers(l_i[0], l_i[1])

            ratio = array_manip.div_ncerr(l_f[0], l_f[1],
                                          l_i_bc[0], l_i_bc[1])

            scale_y = array_manip.mult_ncerr(y_val, y_err2, ratio[0], ratio[1])
        else:
            scale_y = (y_val, y_err2)

        value = array_manip.sub_ncerr(val, err2, E_f_new[0], E_f_new[1])
            
        # Convert from meV to ueV
        value2 = array_manip.mult_ncerr(value[0], value[1], 1000.0, 0.0)
        value3 = array_manip.mult_ncerr(scale_y[0], scale_y[1],
                                        1.0/1000.0, 0.0)

        hlr_utils.result_insert(result, res_descr, value3, map_so, "all",
                                0, [value2[0]])

    return result

if __name__ == "__main__":
    import hlr_test
    import SOM

    som1 = hlr_test.generate_som()
    som1.setAllAxisUnits(["meV"])

    la_f = SOM.Information([7.0], [0.1], "Angstroms", "ZSelector")
    som1.attr_list["Wavelength_final"] = la_f
    
    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** igs_energy_transfer"
    print "* som        :", igs_energy_transfer(som1)
    print "* som (scale):", igs_energy_transfer(som1, scale=True)
    print "* so         :", igs_energy_transfer(som1[0], lambda_f=la_f)


   
