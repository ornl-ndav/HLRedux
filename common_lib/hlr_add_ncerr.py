import array_manip
import SOM.so
import SOM.som

def copy_attr(source,destination):
    """
    This function copies the attributes from the source SOM to the destination
    SOM.

    Parameters:
    ----------
    -> source is the SOM from which to copy the attributes
    -> destination is the SOM that receives the copied attributes
    """

    for key in source.attr_list.keys():
        destination.attr_list[key]=source.attr_list[key]

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

    TITLE      = SOM.som.SOM.TITLE
    X_UNITS    = SOM.som.SOM.X_UNITS
    Y_UNITS    = SOM.som.SOM.Y_UNITS
    OPERATIONS = "operations"

    def add_som_som(som1,som2):
        # check that there is the same number of so
        if len(som1)!=len(som2):
            raise IndexError,"Can only add SOMs with same number of spectra"
        #check that the units match up
        if som1.attr_list[X_UNITS]!=som2.attr_list[X_UNITS]:
            raise RuntimeError,"X units do not match"
        if som1.attr_list[Y_UNITS]!=som2.attr_list[Y_UNITS]:
            raise RuntimeError,"Y units do not match"


        # create empty result som
        result=SOM.som.SOM()

        # attributes from som1 clobber those from som2
        copy_attr(som2,result)
        copy_attr(som1,result)

        # do the calculation
        for (so1,so2) in map(None,som1,som2):
            result.append(add_so_so(so1,so2))

        # update the attribute list to include operation
        if result.attr_list.has_key(OPERATIONS):
            operations=result.attr_list[OPERATIONS]
        else:
            operations=[]
        operations.append(("Step ?","add_ncerr(%s,%s)" % (som1,som2)))
        result.attr_list[OPERATIONS]=operations

        return result

    def add_som_so(som,so):
        # create empty result som
        result=SOM.som.SOM()

        # copy attributes from som
        copy_attr(som,result)

        # do the calculation
        for it in som:
            result.append(add_so_so(it,so))

        # update the attribute list to include operation
        if result.attr_list.has_key(OPERATIONS):
            operations=result.attr_list[OPERATIONS]
        else:
            operations=[]
        operations.append(("Step ?","add_ncerr(%s,%s)" % (som,so)))
        result.attr_list[OPERATIONS]=operations

        return result

    def add_som_num(som,num):
        # create empty result som
        result=SOM.som.SOM()

        # copy attributes from som
        copy_attr(som,result)

        # do the calculation
        for it in som:
            result.append(add_so_num(it,num))

        # update the attribute list to include operation
        if result.attr_list.has_key(OPERATIONS):
            operations=result.attr_list[OPERATIONS]
        else:
            operations=[]
        operations.append(("Step ?","add_ncerr(%s,%s)" % (som,num)))
        result.attr_list[OPERATIONS]=operations

        return result

    def add_so_so(so1,so2):
        if so1.x!=so2.x:
            raise RunTimeError,"x axis must be equal to add spectra"

        # set up the result
        result=SOM.so.SO()
        result.id=so1.id
        result.x=so1.x

        # do the math
        (result.y,result.var_y)=array_manip.add_ncerr(so1.y,so1.var_y,
                                                      so2.y,so2.var_y)

        return result

    def add_so_num(so,num):
        # set up the result
        result=SOM.so.SO()
        result.id=so.id
        result.x=so.x

        # do the math
        (result.y,result.var_y)=array_manip.add_ncerr(so.y,so.var_y,
                                                      num[0],num[1])

        return result

    # import the helper functions
    import hlr_utils

    # set up for working through data
    result,res_descr=hlr_utils.empty_result(left,right)
    l_descr=hlr_utils.get_descr(left)
    r_descr=hlr_utils.get_descr(right)

    # iterate through the values
    for i in range(hlr_utils.get_length(left,right)):
        value=array_manip.add_ncerr(hlr_utils.get_value(left,i,l_descr),
                                    hlr_utils.get_err2(left,i,l_descr),
                                    hlr_utils.get_value(right,i,r_descr),
                                    hlr_utils.get_err2(right,i,r_descr))
        hlr_utils.result_insert(result,res_descr,value)

    return result
"""
    # determine if the left is a som
    try:
        left.attr_list[TITLE]
        try:
            right.attr_list[TITLE]
            return add_som_som(left,right)
        except AttributeError:
            try:
                right.id
                return add_som_so(left,right)
            except AttributeError:
                return add_som_num(left,right)
    except AttributeError: # left is a so
        pass

    # determine if left is a so
    try:
        left.id
        try:
            right.attr_list[TITLE]
            return add_som_so(right,left)
        except AttributeError:
            try:
                right.id
                return add_so_so(left,right)
            except AttributeError:
                return add_so_num(left,right)
    except AttributeError:
        pass

    # left must be a tuple
    try:
        right.attr_list[TITLE]
        return add_som_num(right,left)
    except AttributeError:
        right.id
        return add_so_num(right,left)

    raise TypeError,"Do not know what to do with supplied types"
"""

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
