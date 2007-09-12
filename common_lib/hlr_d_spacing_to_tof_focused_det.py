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

import SOM
    
def d_spacing_to_tof_focused_det(obj, **kwargs):
    """
    This function converts a primary axis of a C{SOM} or C{SO} from d-spacing
    to a focused time-of-flight. The focusing is done using the geometry
    information from a single detector pixel. The d-spacing axis for a C{SOM}
    must be in units of I{Angstroms}. The primary axis of a C{SO} is assumed
    to be in units of I{Angstroms}.

    @param obj: Object to be converted
    @type obj: C{SOM.SOM} or C{SOM.SO}
    
    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword polar: The polar angle and its associated error^2
    @type polar: C{tuple} or C{list} of C{tuple}s
    
    @keyword pathlength: The total pathlength and its associated error^2
    @type pathlength: C{tuple} or C{list} of C{tuple}s
    
    @keyword pixel_id: The pixel ID from which the geometry information will
                       be retrieved from the instrument
    @type pixel_id: C{tuple}=(\"bankN\", (x, y))
    
    @keyword verbose: This determines if the pixel geometry information is
                      printed. The default is False
    @type verbose: C{boolean}
    
    @keyword units: The expected units for this function. The default for
                    this function is I{microseconds}.
    @type units: C{string}


    @return: Object with a primary axis in d-spacing converted to
             time-of-flight
    @rtype: C{SOM.SOM} or C{SOM.SO}

 
    @raise RuntimeError: A C{SOM} or C{SO} is not provided to the function
    
    @raise RuntimeError: No C{SOM.Instrument} is provided in a C{SOM}
    
    @raise RuntimeError: No C{SOM} is given and both the pathlength and polar
                         angle are not provided
                         
    @raise RuntimeError: No C{SOM} is given and the pathlength is not provided
    
    @raise RuntimeError: No C{SOM} is given and the polar angle is not provided
    """

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
        axis = hlr_utils.one_d_units(obj, units)
    else:
        axis = 0

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)
    if res_descr == "SOM":
        result = hlr_utils.force_units(result, "microseconds", axis)
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
        p_descr = hlr_utils.get_descr(pathlength)

    if polar is not None:
        a_descr = hlr_utils.get_descr(polar)

    # iterate through the values
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
        angle = hlr_utils.get_value(polar, 0, a_descr)
        angle_err2 = hlr_utils.get_err2(polar, 0, a_descr)

    # iterate through the values
    import axis_manip
    
    for i in xrange(hlr_utils.get_length(obj)):
        val = hlr_utils.get_value(obj, i, o_descr, "x", axis)
        err2 = hlr_utils.get_err2(obj, i, o_descr, "x", axis)

        map_so = hlr_utils.get_map_so(obj, None, i)

        value = axis_manip.d_spacing_to_tof_focused_det(val, err2, pl, pl_err2,
                                                        angle, angle_err2)
                                                        
        hlr_utils.result_insert(result, res_descr, value, map_so, "x", axis)

    return result

if __name__ == "__main__":
    import hlr_test

    pathlen = (20.0, 0.1)
    po = (0.785, 0.005)   
    pid = 14
    
    som1 = hlr_test.generate_som()
    som1.setAllAxisUnits(["Angstroms"])
    som1.attr_list.instrument = SOM.ASG_Instrument()

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1] 
    print "********** d_spacing_to_tof_focused_det"
    print "* d_spacing_to_tof_focused_det som :", \
          d_spacing_to_tof_focused_det(som1, pixel_id=pid, verbose=True)
    print "* d_spacing_to_tof_focused_det so  :", \
          d_spacing_to_tof_focused_det(som1[0], pathlength=pathlen, polar=po)

