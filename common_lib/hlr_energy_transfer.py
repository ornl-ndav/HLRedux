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

def energy_transfer(left,right,units="meV"):
    """
    This function takes a tuple and a SOM, a tuple and a SO or two tuples and
    calculates the energy transfer in units of THz. The SOM principle axis
    must be in units of meV. The SO and tuples are assumed to be in units of
    meV.

    Parameters:
    ----------
    -> left is a SOM, SO or tuple on the left side of the subtraction
    -> right is a SOM, SO or tuple on the right side of the subtraction

    Return:
    ------
    <- A SOM, SO or tuple based on left - right in units of THz

    Exceptions:
    ----------

    <- RuntimeError is raised if the x-axis units are not meV
    """

    # import the helper functions
    import hlr_utils

    # set up for working through data
    (result,res_descr)=hlr_utils.empty_result(left,right)
    (l_descr,r_descr)=hlr_utils.get_descr(left,right)

    # error checking for types
    if l_descr == "SOM" and r_descr == "SOM":
        raise TypeError, "SOM-SOM operation not supported"
    elif l_descr == "SOM" and r_descr == "SO":
        raise TypeError, "SOM-SO operation not supported"
    elif l_descr == "SO" and r_descr == "SOM":
        raise TypeError, "SO-SOM operation not supported"
    elif l_descr == "SO" and r_descr == "SO":
        raise TypeError, "SO-SO operation not supported"
    else:
        pass
    
    result=hlr_utils.copy_som_attr(result,res_descr,left,l_descr,right,r_descr)
    if res_descr == "SOM":
        index = hlr_utils.hlr_1D_units(result, units)
        result = hlr_utils.hlr_force_units(result, "THz", index)
        result.setAxisLabel(index, "energy transfer")
        result.setYUnits("Counts/THz")
        result.setYLabel("Intensity")
    else:
        pass

    # iterate through the values
    import axis_manip
    
    for i in range(hlr_utils.get_length(left,right)):

        val1 = hlr_utils.get_value(left,i,l_descr,"x")
        err2_1 = hlr_utils.get_err2(left,i,l_descr,"x")
        
        val2 = hlr_utils.get_value(right,i,r_descr,"x")
        err2_2 = hlr_utils.get_err2(right,i,r_descr,"x")

        value=axis_manip.energy_transfer(val1, err2_1, val2, err2_2)

        map_so = hlr_utils.get_map_so(left,right,i)
        hlr_utils.result_insert(result,res_descr,value,map_so,"x")

    return result


if __name__=="__main__":
    import hlr_test

    som1=hlr_test.generate_som()
    som1.setAllAxisUnits(["meV"])
    som2=hlr_test.generate_som()
    som2.setAllAxisUnits(["meV"])

    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1]
    print "********** SOM2"
    print "* ",som2[0]
    print "* ",som2[1]

    print "********** energy_transfer"
    print "* som -scal:",energy_transfer(som1,(1,1))
    print "* som -slist:",energy_transfer(som1,[(1,1),(4,1)])
    print "* scal-som :",energy_transfer((1,1),som1)
    print "* so  -scal:",energy_transfer(som1[0],(1,1))
    print "* scal-so  :",energy_transfer((1,1),som1[0])
    print "* scal-scal:",energy_transfer((2,1),(1,1))
    print "* slist-slist:",energy_transfer([(2,1),(1,1)], [(5,1),(2,1)])




