def subtract_time_indep_bkg(obj, B_list):
    """
    This function takes a SOM or a SO and a list of time-independent background
    tuples and subtracts the numbers from the appropriate SO in the SOM or the
    given SO. The list of tuples (could be just one tuple in the case of the
    SO) is assumed to be in the same order as the SOs in the SOM.

    Parameters:
    ----------
    -> obj is a SOM or SO from which to subtract the individual Bs from the
       B_list
    -> B_list are the time-independent backgrounds to subtract from the SOs in
       the SOM or a SO

    Return:
    -------
    <- A SOM or SO with the time-independent backgrounds subtracted

    Exceptions:
    ----------
    <- IndexError is raised if the B_list object is empty
    <- TypeError is raised if the first argument is not a SOM or SO
    <- RuntimeError is raised if the SOM and list are not the same length
    """

    if len(B_list) <= 0:
        raise IndexError, "List of time-independent background cannot be empty"

    # import the helper functions
    import hlr_utils

    o_descr,l_descr=hlr_utils.get_descr(obj,B_list)

    if o_descr == "number" or o_descr == "list":
        raise TypeError, "First argument must be a SOM or a SO!"

    result,res_descr=hlr_utils.empty_result(obj)

    result=hlr_utils.copy_som_attr(result,res_descr,obj,o_descr)

    import common_lib

    # iterate through the values
    for i in range(hlr_utils.get_length(obj)):
        val1 = hlr_utils.get_value(obj,i,o_descr,"all")
        val2 = hlr_utils.get_value(B_list,i,l_descr,"all")
        value = common_lib.sub_ncerr(val1, val2)

        hlr_utils.result_insert(result,res_descr,value,None,"all")

    return result

if __name__=="__main__":
    import hlr_test
    
    som1=hlr_test.generate_som()
        
    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1]

    print "********** subtract_time_indep_bkg"
    print "* som -scal   :",subtract_time_indep_bkg(som1,(3,1))
    print "* som -l(scal):",subtract_time_indep_bkg(som1,[(1,1), (2,1)])
    print "* so  -scal   :",subtract_time_indep_bkg(som1[0],(1,1))


