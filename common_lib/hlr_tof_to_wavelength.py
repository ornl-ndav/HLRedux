import axis_manip
import SOM.so
import SOM.som

def tof_to_wavelength(obj,pathlength=None,units="microseconds"):
    """
    This function converts a primary axis of a SOM or SO from time-of-flight
    to wavelength. The wavelength axis for a SOM must be in units of
    microseconds. The primary axis of a SO is assumed to be in units of
    microseconds. A tuple of [wavelength, wavelength_err2] (assumed to be in
    units of microseconds) can be converted to [wavelength, wavelength_err2].

    Parameters:
    ----------
    -> obj is the SOM, SO or tuple to be converted

    Return:
    ------
    <- A SOM or SO with a primary axis in wavelength or a tuple converted to
       wavelength

    Exceptions:
    ----------
    <- TypeError is raised if the incoming object is not a type the function
       recognizes
    <- RuntimeError is raised if the SOM x-axis units are not microseconds
    """

    # import the helper functions
    import hlr_utils

    # set up for working through data
    result,res_descr=hlr_utils.empty_result(obj)
    o_descr,d_descr=hlr_utils.get_descr(obj)

    # Primary axis for transformation. If a SO is passed, the function, will
    # assume the axis for transformation is at the 0 position
    if o_descr == "SOM":
        axis = hlr_utils.hlr_1D_units(obj, units)
    else:
        axis = 0

    result=hlr_utils.copy_som_attr(result,res_descr,obj,o_descr)
    if res_descr == "SOM":
        result = hlr_utils.hlr_force_units(result, "Angstroms", axis)

    if pathlength == None:
        pathlength=[20.0, 0.1]

    # iterate through the values
    for i in range(hlr_utils.get_length(obj)):
        val = hlr_utils.get_value(obj,i,o_descr,"x",axis)
        err2 = hlr_utils.get_err2(obj,i,o_descr,"x",axis)

        value=axis_manip.tof_to_wavelength(val, err2,
                                           pathlength[0], pathlength[1])

        map_so = hlr_utils.get_map_so(obj,None,i)
        hlr_utils.result_insert(result,res_descr,value,map_so,"x",axis)

    return result


if __name__=="__main__":
    import hlr_test

    som1=hlr_test.generate_som()
    som1.setAllAxisUnits(["microseconds"])

    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1]

    print "********** tof_to_wavelength"
    print "* tof_to_wavelength som :",tof_to_wavelength(som1)
    print "* tof_to_wavelength so  :",tof_to_wavelength(som1[0])
    print "* tof_to_wavelength scal:",tof_to_wavelength([1,1])
