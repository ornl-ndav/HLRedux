import array_manip
import SOM.so
import SOM.som

def add_ncerr(left,right):
    """
    This function adds two objects (SOM, SO or tuple[val,val_err2]) and
    returns the result of the addition in an SOM. The function does not
    handle the case of tuple/tuple.

    Parameters:
    ----------
    -> left  Object on the left of the addition sign
    -> right Object on the right of the addition sign

    Returns:
    -------
    <- A SOM or SO containing the results of the addition

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
    if (r_descr=="SOM" and l_descr!="SOM") \
           or (r_descr=="SO" and l_descr!="SO"):
        temp=left
        left=right
        right=temp
    elif r_descr=="SOM" and l_descr=="SOM":
        hlr_utils.hlr_math_compatible(left,right)
    elif l_descr=="number" and r_descr=="number":
        raise RuntimeError

    # iterate through the values
    for i in range(hlr_utils.get_length(left,right)):
        value=array_manip.add_ncerr(hlr_utils.get_value(left,i,l_descr),
                                    hlr_utils.get_err2(left,i,l_descr),
                                    hlr_utils.get_value(right,i,r_descr),
                                    hlr_utils.get_err2(right,i,r_descr))
        
        hlr_utils.result_insert(result,res_descr,value)

    return result

if __name__=="__main__":
    def generate_so(start,stop=0):
        if stop<start:
            stop=start
            start=0

        so=SOM.so.SO()
        if start==stop:
            return so

        so.x.extend(range(stop-start))
        so.y.extend(range(start,stop))
        so.var_y.extend(range(start,stop))
        return so

    def so_to_str(so):
        if so==None:
            return None
        else:
            return so.id,so.x,so.y,so.var_y

    som1=SOM.som.SOM()
    count=0
    for i in range(2):
        so=generate_so(count,count+5)
        so.id=i+1
        som1.append(so)
        count+=5

    som2=SOM.som.SOM()
    count=0
    for i in range(2):
        so=generate_so(count,count+5)
        so.id=i+1
        som2.append(so)
        count+=5

    print "********** SOM1"
    print "* ",so_to_str(som1[0])
    print "* ",so_to_str(som1[1])
    print "********** SOM2"
    print "* ",so_to_str(som2[0])
    print "* ",so_to_str(som2[1])

    print "********** add_ncerr"
    print "* so +scal:",so_to_str(add_ncerr(som1[0],(1,1)))
    print "* so +so  :",so_to_str(add_ncerr(som1[0],som1[1]))
    print "* som+scal:",add_ncerr(som1,(1,1))
    print "* som+so  :",add_ncerr(som1,som1[0])
    print "* som+som :",add_ncerr(som1,som2)
