import array_manip
import SOM.so
import SOM.som

def div_ncerr(left,right):
    """
    This function divides two objects (SOM, SO or tuple[val,val_err2]) and
    returns the result of the division in an SOM. The function does not
    handle the case of tuple/tuple.

    Parameters:
    ----------
    -> left  Object on the left of the division sign
    -> right Object on the right of the division sign

    Returns:
    -------
    <- A SOM or SO containing the results of the division

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
    result,res_descr=hlr_utils.empty_result(left,right)
    (l_descr,r_descr)=hlr_utils.get_descr(left,right)

    # error check information
    if r_descr=="SOM" and l_descr=="SOM":
        hlr_utils.hlr_math_compatible(left,l_descr,right,r_descr)
    elif l_descr=="number" and r_descr=="number":
        raise RuntimeError, "tuple, tuple operation is not supported!"

    result=hlr_utils.copy_som_attr(result,res_descr,left,l_descr,right,r_descr)

    # iterate through the values
    for i in range(hlr_utils.get_length(left,right)):
        val1 = hlr_utils.get_value(left,i,l_descr)
        val2 = hlr_utils.get_value(right,i,r_descr)
        (descr_1,descr_2)=hlr_utils.get_descr(val1, val2)
        hlr_utils.hlr_math_compatible(val1, descr_1, val2, descr_2)

        value=array_manip.div_ncerr(val1,
                                    hlr_utils.get_err2(left,i,l_descr),
                                    val2,
                                    hlr_utils.get_err2(right,i,r_descr))

        map_so = hlr_utils.get_map_so(left,right,i)
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

    print "********** div_ncerr"
    print "* som /som :",div_ncerr(som1,som2)
    print "* som /so  :",div_ncerr(som1,som1[0])
    print "* so  /som :",div_ncerr(som1[0],som1)
    print "* som /scal:",div_ncerr(som1,(2,1))
    print "* scal/som :",div_ncerr((2,1),som1)
    print "* so  /so  :",div_ncerr(som1[0],som1[1])
    print "* so  /scal:",div_ncerr(som1[0],(2,1))
    print "* scal/so  :",div_ncerr((2,1),som1[0])

