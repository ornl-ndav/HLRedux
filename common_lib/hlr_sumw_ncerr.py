import array_manip
import SOM.so
import SOM.som
def sumw_ncerr(obj1,obj2):
    """
    This function sums by weighting errors of two objects (SOM or SO) and
    returns the result of that action in an SOM. The function does not
    handle the cases of SOM+tuple, SO+tuple or tuple+tuple.

    Parameters:
    ----------
    -> obj1  First object in the weighted sum
    -> obj2  Second object in the the weighted sum

    Returns:
    -------
    <- A SOM or SO containing the results of the weighted sum

    Exceptions:
    ----------
    <- TypeError is raised if the tuple/tuple case is presented to the function
    <- IndexError is raised if the two SOMs do not contain the same number
       of spectra
    <- RunTimeError is raised if the x-axis units of the SOMs do not match
    <- RunTimeError is raised if the y-axis units of the SOMs do not match
    <- RunTimeError is raised if the x-axes of the two SOs are not equal
    """
    # import the helper functions
    import hlr_utils

    # set up for working through data
    result,res_descr=hlr_utils.empty_result(obj1,obj2)
    (o1_descr,o2_descr)=hlr_utils.get_descr(obj1,obj2)

    # error check information
    if o1_descr=="number" or o2_descr=="number":
        raise RuntimeError, "Operations with tuples are not supported!"
    elif (o2_descr=="SOM" and o1_descr=="SO"):
        obj1,obj2 = hlr_utils.swap_args(obj1,obj2)
        o1_descr,o2_descr = hlr_utils.swap_args(o1_descr,o2_descr)
    elif o2_descr=="SOM" and o1_descr=="SOM":
        hlr_utils.hlr_math_compatible(obj1,o1_descr,obj2,o2_descr)

    result=hlr_utils.copy_som_attr(result,res_descr,obj1,o1_descr,
                                   obj2,o2_descr)

    # iterate through the values
    for i in range(hlr_utils.get_length(obj1,obj2)):
        val1 = hlr_utils.get_value(obj1,i,o1_descr)
        val2 = hlr_utils.get_value(obj2,i,o2_descr)
        (descr_1,descr_2)=hlr_utils.get_descr(val1, val2)
        hlr_utils.hlr_math_compatible(val1, descr_1, val2, descr_2)

        value=array_manip.sumw_ncerr(val1,
                                     hlr_utils.get_err2(obj1,i,o1_descr),
                                     val2,
                                     hlr_utils.get_err2(obj2,i,o2_descr))
        
        map_so = hlr_utils.get_map_so(obj1,None,i)
        hlr_utils.result_insert(result,res_descr,value,map_so)

    return result


if __name__=="__main__":
    import hlr_test

    som1=hlr_test.generate_som()
    som2=hlr_test.generate_som()

    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1]
    print "********** SOM2"
    print "* ",som2[0]
    print "* ",som2[1]

    print "********** sumw_ncerr"
    print "* so +so  :",sumw_ncerr(som1[0],som2[1])
    print "* som+so  :",sumw_ncerr(som1,som2[0])
    print "* som+som :",sumw_ncerr(som1,som2)




