def rebin_axis_1D(obj,axis_out):
    """
    This function rebins the primary axis for a SOM or a SO based on the
    given NessiList axis.

    Parameters:
    ----------
    -> obj is the SOM or SO to be rebinned
    -> axis_out is a NessiList containing the axis to rebin the SOM or SO to

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
        axis_out.__type__
    except AttributeError:
        raise TypeError, "Rebinning axis must be a NessiList!"
        
    (o_descr,d_descr)=hlr_utils.get_descr(obj)

    if o_descr == "number" or o_descr == "list":
        raise TypeError, "Do not know how to handle given type: %s" %\
              o_descr
    
    (result,res_descr)=hlr_utils.empty_result(obj)

    result=hlr_utils.copy_som_attr(result,res_descr,obj,o_descr)

    # iterate through the values
    import axis_manip
    
    for i in range(hlr_utils.get_length(obj)):
        axis_in = hlr_utils.get_value(obj,i,o_descr,"x",0)
        val = hlr_utils.get_value(obj,i,o_descr)
        err2 = hlr_utils.get_err2(obj,i,o_descr)

        value=axis_manip.rebin_axis_1D(axis_in, val, err2, axis_out)
        xvals=[]
        xvals.append(axis_out)

        map_so = hlr_utils.get_map_so(obj,None,i)
        hlr_utils.result_insert(result,res_descr,value,map_so,"all",0,xvals)

    return result


if __name__=="__main__":
    import hlr_test
    import nessi_list

    som1=hlr_test.generate_som()

    axis=nessi_list.NessiList()
    axis.extend(0,2.5,5)

    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1]

    print "********** rebin_axis_1D"
    print "* rebin som:",rebin_axis_1D(som1,axis)
    print "* rebin so :",rebin_axis_1D(som1[0],axis)
