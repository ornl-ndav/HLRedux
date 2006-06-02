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

def tof_to_d_spacing(obj,pathlength=None,polar=None,
                     units="microseconds"):

    # import the helper functions
    import hlr_utils

    # set up for working through data
    (result,res_descr)=hlr_utils.empty_result(obj)
    (o_descr,d_descr)=hlr_utils.get_descr(obj)

    if o_descr == "number" or o_descr == "list":
        raise RuntimeError, "Must provide a SOM of a SO to the function."
    # Go on
    else:
        pass

    # Primary axis for transformation. If a SO is passed, the function, will
    # assume the axis for transformation is at the 0 position
    if o_descr == "SOM":
        axis = hlr_utils.hlr_1D_units(obj, units)
    else:
        axis = 0

    result=hlr_utils.copy_som_attr(result,res_descr,obj,o_descr)
    if res_descr == "SOM":
        result = hlr_utils.hlr_force_units(result, "Angstroms", axis)
        result.setAxisLabel(axis, "d-spacing")
        result.setYUnits("Counts/A")
        result.setYLabel("Intensity")
    else:
        pass

    if pathlength == None or polar == None:
        if o_descr == "SOM":
            try:
                obj.attr_list.instrument.get_primary()
                inst = obj.attr_list.instrument
            except RuntimeError:
                raise RuntimeError, "A detector was not provided"
        else:
            if pathlength == None and polar == None:
                raise RuntimeError, "If no SOM is provided, then pathlength "\
                      +"and polar angle information must be provided"
            elif pathlength == None:
                raise RuntimeError, "If no SOM is provided, then pathlength "\
                      +"information must be provided"
            elif polar == None:
                raise RuntimeError, "If no SOM is provided, then polar angle "\
                      +"information must be provided"
    else:
        pass

    if pathlength != None:
        (p_descr,e_descr) = hlr_utils.get_descr(pathlength)

    if polar != None:
        (a_descr,e_descr) = hlr_utils.get_descr(polar)

    # iterate through the values
    import axis_manip
    import math

    for i in range(hlr_utils.get_length(obj)):
        val = hlr_utils.get_value(obj,i,o_descr,"x",axis)
        err2 = hlr_utils.get_err2(obj,i,o_descr,"x",axis)

        map_so = hlr_utils.get_map_so(obj,None,i)

        if pathlength == None:
            (pl,pl_err2) = hlr_utils.get_parameter("total",map_so,inst)
        else:
            pl = hlr_utils.get_value(pathlength,i,p_descr)
            pl_err2 = hlr_utils.get_err2(pathlength,i,p_descr)

        value=axis_manip.tof_to_wavelength(val, err2, pl, pl_err2)
        
        if polar == None:
            (angle,angle_err2) = hlr_utils.get_parameter("polar",map_so,inst)
        else:
            angle = hlr_utils.get_value(polar,i,p_descr)
            angle_err2 = hlr_utils.get_err2(polar,i,p_descr)

        count = 0
        for v,e2 in map(None, value[0], value[1]):
            term1 = 1.0 / (2.0 * math.sin(angle))
            term2 = 1.0 / math.tan(angle)
            value[0][count] = v * term1
            v2 = value[0][count] * value[0][count]
            value[1][count] = term1*term1*e2 + v2*term2*term2*angle_err2
            count += 1

        hlr_utils.result_insert(result,res_descr,value,map_so,"x",axis)

    return result


if __name__=="__main__":
    import hlr_test
    import SOM

    pathlength = (20.0, 0.1)
    polar = (0.785, 0.005)   
    
    som1=hlr_test.generate_som()
    som1.setAllAxisUnits(["microseconds"])
    som1.attr_list.instrument = SOM.ASG_Instrument()

    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1] 
    print "********** tof_to_d_spacing"
    print "* tof_to_d_spacing som :",tof_to_d_spacing(som1)
    print "* tof_to_d_spacing so  :",tof_to_d_spacing(som1[0],pathlength,
                                                      polar)

