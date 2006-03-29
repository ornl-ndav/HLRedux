import axis_manip
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

def rebin_axis_2D(obj,axis1,axis2):
    """
    This function rebins two primary axes for a SOM or a SO based on the
    given NessiList axis1 and axis2.

    Parameters:
    ----------
    -> obj is the SOM or SO to be rebinned
    -> axis1 is a NessiList containing the 1st axis to rebin the SOM or SO to
    -> axis2 is a NessiList containing the 2nd axis to rebin the SOM or SO to

    Returns:
    -------
    <- A SOM or SO that has been rebinned according to the provided axis

    Exceptions:
    ----------
    <- TypeError is raised if the rebinning axis given is not a NessiList
    <- TypeError is raised if object being rebinned is not a SOM or a SO
    """

    TITLE=SOM.som.SOM.TITLE

    def rebin_som(som, axis1, axis2):
        # create empty result som
        result=SOM.som.SOM()

        copy_attr(som,result)

        # do the rebinning
        for so in som:
            result.append(rebin_so(so,axis1,axis2))

        return result

    def rebin_so(so,axis1,axis2):
        # set up the result
        result=SOM.so.SO()
        result.id=so.id
        result.x=axis1

        # do the rebinning
        (result.y, result.var_y)=axis_manip.rebin_axis_2D(so.x,so.x,
                                                          so.y,so.var_y,
                                                          axis1,axis2)

        return result

    # Rebinning axis must be a NessiList. Fail now before getting too far.
    try:
        axis1.__type__
        axis2.__type__
    except AttributeError:
        raise TypeError, "Axes must be NessiLists!"

    # determine if the obj is a som
    try:
        obj.attr_list[TITLE]
        return rebin_som(obj,axis1,axis2)

    except AttributeError:
        pass

    # determine if obj is a so
    try:
        obj.id
        return rebin_so(obj,axis1,axis2)
    except AttributeError:
        raise TypeError, "Do not know how to handle given type"

if __name__=="__main__":
    import nessi_list

    def generate_so(start,stop=0):
        if stop<start:
            stop=start
            start=0

        so=SOM.so.SO()
        if start==stop:
            return so

        so.x.extend(range(stop-start+1))
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

    axis=nessi_list.NessiList()
    axis.extend(0,2.5,5)

    print "********** SOM1"
    print "* ",so_to_str(som1[0])
    print "* ",so_to_str(som1[1])

    print "********** rebin_axis_1D"
    print "* rebin so :",so_to_str(rebin_axis_2D(som1[0],axis1,axis2))
    print "* rebin som:",rebin_axis_2D(som1,axis1,axis2)
