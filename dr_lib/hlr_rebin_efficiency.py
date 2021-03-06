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

def rebin_efficiency(obj1, obj2, **kwargs):
    """
    This function takes two objects and rebins the data for obj1 onto the axis
    provided by obj2. The units on the x-axes needs to be I{Angstroms}, since
    this is what the efficiencies will be present as.

    @param obj1: Object that will be rebinned
    @type obj1: C{SOM.SOM} or C{SOM.SO}
    
    @param obj2: Object that will provide the axis for rebinning
    @type obj2: C{SOM.SOM} or C{SOM.SO}
    
    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword units: The expected units for this function. The default for this
                    function is I{Angstroms}.
    @type units: C{string}


    @return: Object that has been rebinned
    @rtype: C{SOM.SOM} or C{SOM.SO}


    @raise TypeError: The C{SOM}-C{SO} operation is attempted
    
    @raise TypeError: The C{SO}-C{SOM} operation is attempted
    
    @raise TypeError: obj1 not a C{SOM} or C{SO}
    
    @raise TypeError: obj2 not a C{SOM} or C{SO}
    
    @raise IndexError: The C{SOM}s do not have the same number of C{SO}s
    
    @raise RuntimeError: The C{SOM} x-axis units are not I{Angstroms}
    
    @raise RuntimeError: The x-axis units of the C{SOM}s do not match
    """

    # import the helper functions
    import hlr_utils

    # Kickout if monitor object is None
    if obj1 is None:
        return obj1
    
    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj1, obj2)
    (o1_descr, o2_descr) = hlr_utils.get_descr(obj1, obj2)
    
    # error checking for types
    if o1_descr == "SOM" and o2_descr == "SO":
        raise TypeError, "SOM-SO operation not supported"
    elif o1_descr == "SO" and o2_descr == "SOM":
        raise TypeError("SO-SOM operation not supported")
    # Have the right object combination, go on
    else:
        pass

    # Setup keyword arguments
    try:
        units = kwargs["units"]
    except KeyError:
        units = "Angstroms"
   
    if o1_descr == "SOM" and o2_descr == "SOM":
        hlr_utils.math_compatible(obj1, o1_descr, obj2, o2_descr)
    # If both objects are not SOMs, do nothing
    else:
        pass

    result = hlr_utils.copy_som_attr( result, res_descr, obj2, o2_descr)

    if res_descr == "SOM":
        result = hlr_utils.force_units(result, units)
    # Can't force units on anything other than a SOM
    else:
        pass

    # iterate through the values
    import common_lib

    for i in xrange(hlr_utils.get_length(obj1, obj2)):
        val1 = hlr_utils.get_value(obj1, i, o1_descr, "all")
        val2 = hlr_utils.get_value(obj2, i, o2_descr, "x")
        
        value = common_lib.rebin_axis_1D(val1, val2)
        
        hlr_utils.result_insert(result, res_descr, value, None, "all")

    return result
                                                    
    
if __name__ == "__main__":
    import hlr_test
    import SOM

    som1 = SOM.SOM()
    som1.setAllAxisUnits(["Angstroms"])
    so1 = SOM.SO()    
    so1.id = 1
    so1.axis[0].val.extend(range(0, 7, 2))
    so1.y.extend(0.994, 0.943, 0.932)
    so1.var_y.extend(0.010, 0.012, 0.013)
    som1.append(so1)
    so2 = SOM.SO()    
    so2.id = 2
    so2.axis[0].val.extend(range(0, 7, 2))
    so2.y.extend(0.934, 0.986, 0.957)
    so2.var_y.extend(0.011, 0.010, 0.015)
    som1.append(so2)

    som2 = hlr_test.generate_som()
    som2.setAllAxisUnits(["Angstroms"])

    
    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** SOM2"
    print "* ", som2[0]
    print "* ", som2[1]

    print "********** rebin_efficiency"
    print "* som+som :", rebin_efficiency(som1, som2)
    print "* so +so  :", rebin_efficiency(som1[0], som2[0])

    
