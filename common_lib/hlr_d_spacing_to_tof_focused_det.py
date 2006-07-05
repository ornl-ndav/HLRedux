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

def d_spacing_to_tof_focused_det(obj, **kwargs):
    """
    This function converts a primary axis of a SOM or SO from d-spacing to
    a focused time-of-flight. The focusing is done using the geometry
    information from a single detector pixel. The d-spacing axis for a SOM
    must be in units of Angstroms. The primary axis of a SO is assumed to be
    in units of Angstroms.

    Parameters:
    ----------
    -> obj is the SOM or SO to be converted
    -> kwargs is a list of key word arguments that the function accepts:
          polar= a tuple or list of tuples containing the polar angle and
                 its associated error^2
          pathlength= a tuple or list of tuples containing the pathlength and
                      its associated error^2
          pixel_id= a string containing the pixel ID from which the geometry
                    information will be retrieved from the instrument
          verbose=<boolean> This determines if the pixel geometry
                            information is printed. The default is False
          units= a string containing the expected units for this function.
                 The default for this function is microseconds

    Returns:
    -------
    <- A SOM or SO with a primary axis in d-spacing converted to time-of-flight

    Exceptions:
    ----------
    <- RuntimeError is raised if a SOM or SO is not provided to the function
    <- RuntimeError is raised if no instrument is provided in a SOM
    <- RuntimeError is raised if no SOM is given and both the pathlength and
       polar angle are not provided
    <- RuntimeError is raised if no SOM is given and the pathlength is not
       provided
    <- RuntimeError is raised if no SOM is given and the polar angle is not
       provided
    """

    # import the helper functions
    import hlr_utils

    # constants
    M_OVER_H = 1.0 / 0.003956034
    M_OVER_H_2 = M_OVER_H * M_OVER_H

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj)
    (o_descr, d_descr) = hlr_utils.get_descr(obj)

    if o_descr == "number" or o_descr == "list":
        raise RuntimeError("Must provide a SOM of a SO to the function.")
    # Go on
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
        pixel_id = kwargs["pixel_id"]
    except KeyError:
        pixel_id = None

    try:
        verbose = kwargs["verbose"]
    except KeyError:
        verbose = False

    try:
        units = kwargs["units"]
    except KeyError:
        units = "Angstroms"

    # Primary axis for transformation. If a SO is passed, the function, will
    # assume the axis for transformation is at the 0 position
    if o_descr == "SOM":
        axis = hlr_utils.hlr_1D_units(obj, units)
    else:
        axis = 0

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)
    if res_descr == "SOM":
        result = hlr_utils.hlr_force_units(result, "microseconds", axis)
        result.setAxisLabel(axis, "time-of-flight")
        result.setYUnits("Counts/usec")
        result.setYLabel("Intensity")
    else:
        pass

    if pathlength is None or polar is None:
        if o_descr == "SOM":
            try:
                obj.attr_list.instrument.get_primary()
                inst = obj.attr_list.instrument
            except RuntimeError:
                raise RuntimeError("An instrument was not provided")
        else:
            if pathlength is None and polar is None:
                raise RuntimeError("If no SOM is provided, then pathlength "\
                +"and polar angle information must be provided")
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

    if pathlength is not None:
        (p_descr, e_descr) = hlr_utils.get_descr(pathlength)

    if polar is not None:
        (a_descr, e_descr) = hlr_utils.get_descr(polar)

    # iterate through the values
    import axis_manip
    import SOM
    
    import math

    if pixel_id is not None:
        tmp_so = SOM.SO()
        tmp_so.id = pixel_id
        (pl, pl_err2) = hlr_utils.get_parameter("total", tmp_so, inst)
        (angle, angle_err2) = hlr_utils.get_parameter("polar", tmp_so, inst)

        if verbose:
            format_str = "Pixel ID %s has polar angle: (%f,%f) and "
            format_str += "pathlength: (%f,%f)"
            print format_str % (str(pixel_id), angle, angle_err2, pl, pl_err2)
        else:
            pass
    else:
        pl = hlr_utils.get_value(pathlength, 0, p_descr)
        pl_err2 = hlr_utils.get_err2(pathlength, 0, p_descr)
        angle = hlr_utils.get_value(polar, 0, p_descr)
        angle_err2 = hlr_utils.get_err2(polar, 0, p_descr)
            
    L_foc_2 = pl * pl
    sin_foc = math.sin(angle/2.0)
    sin_foc_2 = sin_foc * sin_foc
    cos_foc_2 = math.cos(angle/2.0) * math.cos(angle/2.0)
    BIG_CONSTANT = 2.0 * M_OVER_H * pl * sin_foc

    import nessi_list

    for i in range(hlr_utils.get_length(obj)):
        val = hlr_utils.get_value(obj, i, o_descr, "x", axis)
        err2 = hlr_utils.get_err2(obj, i, o_descr, "x", axis)

        map_so = hlr_utils.get_map_so(obj, None, i)

        value = (nessi_list.NessiList(), nessi_list.NessiList())
        for v, e2 in map(None, val, err2):
            value[0].append(BIG_CONSTANT * v)

            term1 = v * v * sin_foc_2 * pl_err2
            term2 = 0.25 * cos_foc_2 * L_foc_2 * v * v * angle_err2
            term3 = sin_foc_2 * L_foc_2 * e2
            value[1].append(4.0 * M_OVER_H_2 * (term1 + term2 + term3))

        hlr_utils.result_insert(result, res_descr, value, map_so, "x", axis)

    return result


if __name__=="__main__":
    import hlr_test
    import SOM

    pl = (20.0, 0.1)
    po = (0.785, 0.005)   
    pid = 14
    
    som1=hlr_test.generate_som()
    som1.setAllAxisUnits(["Angstroms"])
    som1.attr_list.instrument = SOM.ASG_Instrument()

    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1] 
    print "********** d_spacing_to_tof_focused_det"
    print "* d_spacing_to_tof_focused_det som :",d_spacing_to_tof_focused_det(som1, pixel_id=pid, verbose=True)
    print "* d_spacing_to_tof_focused_det so  :",d_spacing_to_tof_focused_det(som1[0],pathlength=pl, polar=po)

