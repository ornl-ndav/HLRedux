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

def init_scatt_wavevector_to_scalar_Q(initk, scattk, **kwargs):
    """
    This function takes an initial wavevector and a scattered wavevector as a
    C{tuple} and a C{SOM}, a C{tuple} and a C{SO} or two C{tuple}s and
    calculates the quantity scalar Q units of I{1/Angstroms}. The C{SOM}
    principle axis must be in units of I{1/Angstroms}. The C{SO}s and
    C{tuple}(s) is(are) assumed to be in units of I{1/Angstroms}. The polar
    angle must be provided if one of the initial arguments is not a C{SOM}. If
    a C{SOM} is passed, by providing the polar angle at the function call time,
    the polar angle carried in the C{SOM} instrument will be overridden.

    @param initk: Object holding the initial wavevector
    @type initk: C{SOM.SOM}, C{SOM.SO} or C{tuple}
    
    @param scattk: Object holding the scattered wavevector
    @type scattk: C{SOM.SOM}, C{SOM.SO} or C{tuple}
    
    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword polar: The polar angle and its associated error^2
    @type polar: C{tuple} or C{list} of C{tuple}s

    @keyword units: The expected units for this function. The default for this
                    function is I{1/Angstroms}.
    @type units: C{string}


    @return: Object converted to scalar Q
    @rtype: C{SOM.SOM}, C{SOM.SO} or C{tuple}


    @raise TypeError: The C{SOM}-C{SOM} operation is attempted
    
    @raise TypeError: The C{SOM}-C{SO} operation is attempted
    
    @raise TypeError: The C{SO}-C{SOM} operation is attempted
    
    @raise TypeError: The C{SO}-C{SO} operation is attempted
    
    @raise RuntimeError: The C{SOM} x-axis units are not I{1/Angstroms}
    
    @raise RuntimeError: A C{SOM} is not passed and no polar angle is provided
    
    @raise RuntimeError: No C{SOM.Instrument} is provided in a C{SOM}
    """

    # import the helper functions
    import hlr_utils

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(initk, scattk)
    (i_descr, s_descr) = hlr_utils.get_descr(initk, scattk)

    # error checking for types
    if i_descr == "SOM" and s_descr == "SOM":
        raise TypeError("SOM-SOM operation not supported")
    elif i_descr == "SOM" and s_descr == "SO":
        raise TypeError("SOM-SO operation not supported")
    elif i_descr == "SO" and s_descr == "SOM":
        raise TypeError("SO-SOM operation not supported")
    elif i_descr == "SO" and s_descr == "SO":
        raise TypeError("SO-SO operation not supported")
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
        units = "1/Angstroms"

    result = hlr_utils.copy_som_attr(result, res_descr, initk, i_descr,
                                     scattk, s_descr)
    if res_descr == "SOM":
        index = hlr_utils.one_d_units(result, units)
        result = hlr_utils.force_units(result, units, index)
        result.setAxisLabel(index, "scalar wavevector transfer")
        result.setYUnits("Counts/A-1")
        result.setYLabel("Intensity")
    else:
        pass

    if polar is None:
        if i_descr == "SOM":
            try:
                initk.attr_list.instrument.get_primary()
                inst = initk.attr_list.instrument
            except RuntimeError:
                raise RuntimeError("A detector was not provided!")

        elif s_descr == "SOM":
            try:
                scattk.attr_list.instrument.get_primary()
                inst = scattk.attr_list.instrument
            except RuntimeError:
                raise RuntimeError("A detector was not provided!")

        else:
            raise RuntimeError("If no SOM is provided, then polar "\
                               +"information must be given.")
    else:
        p_descr = hlr_utils.get_descr(polar)

    # iterate through the values
    import axis_manip
    
    for i in xrange(hlr_utils.get_length(initk, scattk)):
        val1 = hlr_utils.get_value(initk, i, i_descr, "x")
        err2_1 = hlr_utils.get_err2(initk, i, i_descr, "x")
        
        val2 = hlr_utils.get_value(scattk, i, s_descr, "x")
        err2_2 = hlr_utils.get_err2(scattk, i, s_descr, "x")

        map_so = hlr_utils.get_map_so(initk, scattk, i)

        if polar is None:
            (angle, angle_err2) = hlr_utils.get_parameter("polar", map_so,
                                                          inst)
        else:
            angle = hlr_utils.get_value(polar, i, p_descr)
            angle_err2 = hlr_utils.get_err2(polar, i, p_descr)
            
        value = axis_manip.init_scatt_wavevector_to_scalar_Q(val1, err2_1,
                                                             val2, err2_2,
                                                             angle, angle_err2)

        hlr_utils.result_insert(result, res_descr, value, map_so, "x")

    return result


if __name__ == "__main__":
    import hlr_test
    import SOM

    som1 = hlr_test.generate_som()
    som1.setAllAxisUnits(["1/Angstroms"])
    som1.attr_list.instrument = SOM.ASG_Instrument()
    pa = (0.785, 0.005)

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** init_scatt_wavevector_to_scalar_Q"
    print "* som -scal:", init_scatt_wavevector_to_scalar_Q(som1, (1, 1))
    print "* scal-som :", init_scatt_wavevector_to_scalar_Q((1, 1), som1)
    print "* so  -scal:", init_scatt_wavevector_to_scalar_Q(som1[0], (1, 1),
                                                            polar=pa)
    print "* scal-so  :", init_scatt_wavevector_to_scalar_Q((1, 1), som1[0],
                                                            polar=pa)
    print "* scal-scal:", init_scatt_wavevector_to_scalar_Q((2, 1), (1, 1),
                                                            polar=pa)




