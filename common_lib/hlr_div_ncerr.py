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

    TITLE=SOM.som.SOM.TITLE
    X_UNITS=SOM.som.SOM.X_UNITS
    Y_UNITS=SOM.som.SOM.Y_UNITS


    def div_som_som(som1,som2):
        # check that there is the same number of so
        if len(som1)!=len(som2):
            raise IndexError,"Can only div SOMs with same number of spectra"
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
            result.append(div_so_so(so1,so2))
        return result

    def div_som_so(som,so):
        # create empty result som
        result=SOM.som.SOM()

        # copy attributes from som
        copy_attr(som,result)

        # do the calculation
        for it in som:
            result.append(div_so_so(it,so))
        return result

    def div_so_som(so,som):
        # create empty result som
        result=SOM.som.SOM()

        # copy attributes from som
        copy_attr(som,result)

        # do the calculation
        for it in som:
            result.append(div_so_so(so,it))
        return result

    def div_som_num(som,num):
        # create empty result som
        result=SOM.som.SOM()

        # copy attributes from som
        copy_attr(som,result)

        # do the calculation
        for it in som:
            result.append(div_so_num(it,num))
        return result

    def div_num_som(num,som):
        # create empty result som
        result=SOM.som.SOM()

        # copy attributes from som
        copy_attr(som,result)

        # do the calculation
        for it in som:
            result.append(div_num_so(num,it))
        return result

    def div_so_so(so1,so2):
        if so1.x!=so2.x:
            raise RunTimeError,"x axis must be equal to div spectra"

        # set up the result
        result=SOM.so.SO()
        result.id=so1.id
        result.x=so1.x

        # do the math
        (result.y,result.var_y)=array_manip.div_ncerr(so1.y,so1.var_y,
                                                      so2.y,so2.var_y)

        return result

    def div_so_num(so,num):
        # set up the result
        result=SOM.so.SO()
        result.id=so.id
        result.x=so.x

        # do the math
        (result.y,result.var_y)=array_manip.div_ncerr(so.y,so.var_y,
                                                      num[0],num[1])

        return result

    def div_num_so(num,so):
        # set up the result
        result=SOM.so.SO()
        result.id=so.id
        result.x=so.x

        # do the math
        (result.y,result.var_y)=array_manip.div_ncerr(num[0],num[1],
                                                      so.y,so.var_y)

        return result


    # determine if the left is a som
    try:
        left.attr_list[TITLE]
        try:
            right.attr_list[TITLE]
            return div_som_som(left,right)
        except AttributeError:
            try:
                right.id
                return div_som_so(left,right)
            except AttributeError:
                return div_som_num(left,right)
    except AttributeError: # left is a so
        pass

    # determine if left is a so
    try:
        left.id
        try:
            right.attr_list[TITLE]
            return div_so_som(left,right)
        except AttributeError:
            try:
                right.id
                return div_so_so(left,right)
            except AttributeError:
                return div_so_num(left,right)
    except AttributeError:
        pass

    # left must be a tuple
    try:
        right.attr_list[TITLE]
        return div_num_som(left,right)
    except AttributeError:
        right.id
        return div_num_so(left,right)

    raise TypeError,"Do not know what to do with supplied types"

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

    print "********** div_ncerr"
    print "* so  /scal:",so_to_str(div_ncerr(som1[0],(2,1)))
    print "* scal/so  :",so_to_str(div_ncerr((2,1),som1[0]))
    print "* so  /so  :",so_to_str(div_ncerr(som1[0],som1[1]))
    print "* som /scal:",div_ncerr(som1,(2,1))
    print "* scal/som :",div_ncerr((2,1),som1)
    print "* som /so  :",div_ncerr(som1,som1[0])
    print "* so  /som :",div_ncerr(som1[0],som1)
    print "* som /som :",div_ncerr(som1,som2)

