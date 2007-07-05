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

def wavelength_to_d_spacing(obj, **kwargs):
    """
    This function converts a primary axis of a C{SOM} or C{SO} from wavelength
    to d-spacing. The wavelength axis for a C{SOM} must be in units of
    I{Angstroms}. The primary axis of a C{SO} is assumed to be in units of
    I{Angstroms}. A C{tuple} of C{(wavelength, wavelength_err2)} (assumed to
    be in units of I{Angstroms}) can be converted to C{(d_spacing,
    d_spacing_err2)}.

    @param obj: Object to be converted
    @type obj: C{SOM.SOM}, C{SOM.SO} or C{tuple}
    
    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword polar:The polar angle and its associated error^2
    @type polar: C{tuple}

    @keyword units: The expected units for this function. The default for this
                    function is I{Angstroms}
    @type units: C{string}


    @return: Object with a primary axis in wavelength converted to d-spacing
    @rtype: C{SOM.SOM}, C{SOM.SO} or C{tuple}


    @raise TypeError: The incoming object is not a type the function recognizes

    @raise RuntimeError: A C{SOM} is not passed and no polar angle is provided

    @raise RuntimeError: The C{SOM} x-axis units are not I{Angstroms}
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
        units = kwargs["units"]
    except KeyError:
        units = "Angstroms"

    # Primary axis for transformation. If a SO is passed, the function, will
    # assume the axis for transformation is at the 0 position
    if o_descr == "SOM":
        axis = hlr_utils.one_d_units(obj, units)
    else:
        axis = 0

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)
    if res_descr == "SOM":
        result = hlr_utils.force_units(result, "Angstroms", axis)
        result.setAxisLabel(axis, "d-spacing")
        result.setYUnits("Counts/A")
        result.setYLabel("Intensity")
    else:
        pass

    if polar is None:
        if o_descr == "SOM":
            try:
                obj.attr_list.instrument.get_primary()
                inst = obj.attr_list.instrument
            except RuntimeError:
                raise RuntimeError("A detector was not provided!")
        else:
            raise RuntimeError("If no SOM is provided, then polar "\
                               +"information must be given.")
    else:
        p_descr = hlr_utils.get_descr(polar)

    # iterate through the values
    import axis_manip
    
    for i in xrange(hlr_utils.get_length(obj)):
        val = hlr_utils.get_value(obj, i, o_descr, "x", axis)
        err2 = hlr_utils.get_err2(obj, i, o_descr, "x", axis)

        map_so = hlr_utils.get_map_so(obj, None, i)

        if polar is None:
            (angle, angle_err2) = hlr_utils.get_parameter("polar", map_so,
                                                          inst)
        else:
            angle = hlr_utils.get_value(polar, i, p_descr)
            angle_err2 = hlr_utils.get_err2(polar, i, p_descr) 

        value = axis_manip.wavelength_to_d_spacing(val, err2, angle,
                                                   angle_err2)
        
        hlr_utils.result_insert(result, res_descr, value, map_so, "x",
                                axis)

    return result


if __name__ == "__main__":
    import hlr_test
    import SOM

    pa = (0.785, 0.005)

    som1 = hlr_test.generate_som()
    som1.setAllAxisUnits(["Angstroms"])
    som1.attr_list.instrument = SOM.ASG_Instrument()

    som2 = hlr_test.generate_som()
    som2.setAllAxisUnits(["Angstroms"])
    som2.attr_list.instrument = SOM.ASG_Instrument()

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** SOM2"
    print "* ", som2[0]
    print "* ", som2[1]

    print "********** wavelength_to_d_spacing"
    print "* som  :", wavelength_to_d_spacing(som1)
    print "* so   :", wavelength_to_d_spacing(som2[0], polar=pa)
    print "* scal :", wavelength_to_d_spacing((1, 1), polar=pa)


