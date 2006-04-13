import SOM

def rebin_efficiency(obj1, obj2, units="Angstroms"):
    """
    This function takes two SOMs or two SOs and rebins the data for obj2 onto
    the axis provided by obj1. The units on the x-axes needs to be Angstroms,
    since this is what the efficiencies will be present as.

    Parameters:
    ----------
    -> obj1 is a SOM or SO that will provide the axis for rebinning
    -> obj2 is a SOM or SO that will be rebinned

    Returns:
    -------
    <- A SOM or SO that has been rebinned

    Exceptions:
    ----------
    <- TypeError is raised if the SOM-SO operation is attempted
    <- TypeError is raised if the SO-SOM operation is attempted
    <- TypeError is raised is obj1 not a SOM or SO
    <- TypeError is raised is obj2 not a SOM or SO
    <- IndexError is raised if the SOMs do not have the same number of SOs
    <- RuntimeError is raised if the SOM x-axis units are not Angstroms
    <- RuntimeError is raised if the x-axis units of the SOMs do not match
    """

    # import the helper functions
    import hlr_utils
    
    # set up for working through data
    result,res_descr=hlr_utils.empty_result(obj1,obj2)
    o1_descr,o2_descr=hlr_utils.get_descr(obj1,obj2)
    
    # error checking for types
    if o1_descr == "SOM" and o2_descr == "SO":
        raise TypeError, "SOM-SO operation not supported"
    elif o1_descr == "SO" and o2_descr == "SOM":
        raise TypeError, "SO-SOM operation not supported"

    if o1_descr == "SOM" and o2_descr == "SOM":
         hlr_utils.hlr_math_compatible(obj1,o1_descr,obj2,o2_descr)

    result=hlr_utils.copy_som_attr(result,res_descr,obj2,o2_descr)

    if res_descr == "SOM":
        result = hlr_utils.hlr_force_units(result, "Angstroms")

    # iterate through the values
    import common_lib
    
    for i in range(hlr_utils.get_length(obj1,obj2)):
        val = hlr_utils.get_value(obj1,i,o1_descr,"x")
        
        value=common_lib.rebin_axis_1D(obj2, val)
        print "1:",value
        
        map_so = hlr_utils.get_map_so(obj2,None,i)
        hlr_utils.result_insert(result,res_descr,value,map_so,"x")
        
        return result
                                                    
    
if __name__=="__main__":
    import hlr_test
        
    som1=hlr_test.generate_som()
    som1.setAllAxisUnits(["Angstroms"])

    som2=SOM.SOM()
    som2.setAllAxisUnits(["Angstroms"])
    so1=SOM.SO()    
    so1.id=1
    so1.axis[0].val.extend(range(0,7,2))
    so1.y.extend(0.994,0.943,0.932)
    so1.var_y.extend(0.010,0.012,0.013)
    som2.append(so1)
    so2=SOM.SO()    
    so2.id=2
    so2.axis[0].val.extend(range(0,7,2))
    so2.y.extend(0.934,0.986,0.957)
    so2.var_y.extend(0.011,0.010,0.015)
    som2.append(so2)
    
    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1]

    print "********** SOM2"
    print "* ",som2[0]
    print "* ",som2[1]

    print "********** rebin_efficiency"
    print "* som+som :",rebin_efficiency(som1,som2)
    print "* so +so  :",rebin_efficiency(som1[0],som2[0])

    
