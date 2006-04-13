def rebin_axis_2D(obj,axis1_out,axis2_out):
    """
    This function rebins two primary axes for a SOM or a SO based on the
    given NessiList axis1 and axis2.

    Parameters:
    ----------
    -> obj is the SOM or SO to be rebinned
    -> axis1_out is a NessiList containing the 1st axis to rebin the SOM or SO
       to
    -> axis2_out is a NessiList containing the 2nd axis to rebin the SOM or SO
       to

    Returns:
    -------
    <- A SOM or SO that has been rebinned according to the provided axis

    Exceptions:
    ----------
    <- TypeError is raised if the rebinning axis given is not a NessiList
    <- TypeError is raised if object being rebinned is not a SOM or a SO
    """
    
    # import the helper functions
    import hlr_utils

    # set up for working through data
    try:
        axis1_out.__type__
    except AttributeError:
        raise TypeError, "Rebinning axis 1 must be a NessiList!"

    try:
        axis2_out.__type__
    except AttributeError:
        raise TypeError, "Rebinning axis 2 must be a NessiList!"
        
    o_descr,d_descr=hlr_utils.get_descr(obj)

    if o_descr == "number":
        raise TypeError, "Do not know how to handle given type"
    
    result,res_descr=hlr_utils.empty_result(obj)

    result=hlr_utils.copy_som_attr(result,res_descr,obj,o_descr)

    # iterate through the values
    import axis_manip
    
    for i in range(hlr_utils.get_length(obj)):
        axis1_in = hlr_utils.get_value(obj,i,o_descr,"x",0)
        axis2_in = hlr_utils.get_value(obj,i,o_descr,"x",1)
        val = hlr_utils.get_value(obj,i,o_descr)
        err2 = hlr_utils.get_err2(obj,i,o_descr)

        value=axis_manip.rebin_axis_2D(axis1_in, axis2_in, val, err2,
                                       axis1_out, axis2_out)
        xvals=[]
        xvals.append(axis1_out)
        xvals.append(axis2_out)

        map_so = hlr_utils.get_map_so(obj,None,i)
        hlr_utils.result_insert(result,res_descr,value,map_so,"all",0,xvals)

    return result


if __name__=="__main__":
    import hlr_test
    import nessi_list

    som1=hlr_test.generate_som("histogram",2)

    axis1=nessi_list.NessiList()
    axis1.extend(0,2.5,5)
    axis2=nessi_list.NessiList()
    axis2.extend(0,2.5,5)

    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1]

    print "********** rebin_axis_2D"
    print "* rebin som:",rebin_axis_2D(som1,axis1,axis2)
    print "* rebin so :",rebin_axis_2D(som1[0],axis1,axis2)

