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
    <- A SOM containing the results of the weighted sum

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

    def sumw_som_som(som1,som2):
        # check that there is the same number of so
        if len(som1)!=len(som2):
            raise IndexError,"Can only sumw SOMs with same number of spectra"
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
            result.append(sumw_so_so(so1,so2))
        return result

    def sumw_som_so(som,so):
        # create empty result som
        result=SOM.som.SOM()

        # copy attributes from som
        copy_attr(som,result)

        # do the calculation
        for it in som:
            result.append(sumw_so_so(it,so))
        return result

    def sumw_so_so(so1,so2):
        if so1.x!=so2.x:
            raise RunTimeError,"x axis must be equal to sumw spectra"

        # set up the result
        result=SOM.so.SO()
        result.id=so1.id
        result.x=so1.x

        # do the math
        (result.y,result.var_y)=array_manip.sumw_ncerr(so1.y,so1.var_y,
                                                       so2.y,so2.var_y)

        return result

    # determine if the obj1 is a som
    try:
        obj1.attr_list[TITLE]
        try:
            obj2.attr_list[TITLE]
            return sumw_som_som(obj1,obj2)
        except AttributeError:
            try:
                obj2.id
                return sumw_som_so(obj1,obj2)
            except AttributeError:
                raise TypeError, "Do not know what to do with supplied types"

    except AttributeError: # obj1 is a so
        pass

    # determine if obj1 is a so
    try:
        obj1.id
        try:
            obj2.attr_list[TITLE]
            return sumw_som_so(obj2,obj1)
        except AttributeError:
            try:
                obj2.id
                return sumw_so_so(obj1,obj2)
            except AttributeError:
                raise TypeError, "Do not know what to do with supplied types"
    except AttributeError:
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

    print "********** sumw_ncerr"
    print "* so +so  :",so_to_str(sumw_ncerr(som1[0],som2[1]))
    print "* som+so  :",sumw_ncerr(som1,som2[0])
    print "* som+som :",sumw_ncerr(som1,som2)




