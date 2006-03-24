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

def rebin_axis_1D(obj,axis):
    """
    This function rebins the primary axis for a SOM or a SO based on the
    given NessiList axis.

    Parameters:
    ----------
    -> obj is the SOM or SO to be rebinned
    -> axis is a NessiList containing the axis to rebin the SOM or SO to

    Returns:
    -------
    <- A SOM or SO that has been rebinned according to the provided axis

    Exceptions:
    ----------
    <- TypeError is raised if the rebinning axis given is not a NessiList
    <- TypeError is raised if object being rebinned is not a SOM or a SO
    """

    TITLE=SOM.som.SOM.TITLE

    def rebin_som(som, axis):
        # create empty result som
        result=SOM.som.SOM()

        copy_attr(som,result)

        # do the rebinning
        for so in som:
            result.append(rebin_so(so,axis))

        return result

    def rebin_so(so,axis):
        # set up the result
        result=SOM.so.SO()
        result.id=so.id
        result.x=axis

        # do the rebinning
        (result.y, result.var_y)=axis_manip.rebin_axis_1D(so.x,so.y,so.var_y,
                                                          axis)

        return result

    # Rebinning axis must be a NessiList. Fail now before getting too far.
    try:
        axis.__type__
    except AttributeError:
        raise TypeError, "Axis must be a NessiList!"

    # determine if the obj is a som
    try:
        obj.attr_list[TITLE]
        return rebin_som(obj,axis)

    except AttributeError:
        pass

    # determine if obj is a so
    try:
        obj.id
        return rebin_so(obj,axis)
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
    print "* rebin so :",so_to_str(rebin_axis_1D(som1[0],axis))
    print "* rebin som:",rebin_axis_1D(som1,axis)
