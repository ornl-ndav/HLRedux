import hlr_rebin_axis_1D
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

def rebin_efficiency(obj1, obj2):
    """
    This function takes two SOMs or two SOs and rebins the data for obj2 onto
    the axis provided by obj1. The units on the x-axes needs to be Angstroms,
    since this is what the efficiencies will be present as.

    Parameters:
    ----------
    -> obj1 is a SOM or SO that will provide the axis for rebinning
    -> obj2 is a SOM or SO that will be rebinned

    Returns:
    -------
    <- A SOM or SO that has been rebinned

    Exceptions:
    ----------
    <- TypeError is raised if the SOM-SO operation is attempted
    <- TypeError is raised if the SO-SOM operation is attempted
    <- TypeError is raised is obj1 not a SOM or SO
    <- TypeError is raised is obj2 not a SOM or SO
    <- IndexError is raised if the SOMs do not have the same number of SOs
    <- RuntimeError is raised if the SOM x-axis units are not Angstroms
    <- RuntimeError is raised if the x-axis units of the SOMs do not match
    """

    TITLE      = SOM.som.SOM.TITLE
    X_UNITS=SOM.som.SOM.X_UNITS
    
    def rebin_som_som(som1,som2):
        # check that there is the same number of so
        if len(som1)!=len(som2):
            raise IndexError,"Can only add SOMs with same number of spectra"
        # check for wavelength units
        if som2.attr_list[X_UNITS]!="Angstroms":
            raise RuntimeError,"X units are not Angstroms"

        # check that the units match up
        if som1.attr_list[X_UNITS]!=som2.attr_list[X_UNITS]:
            raise RuntimeError,"X units do not match"

        # create empty result som
        result=SOM.som.SOM()

        copy_attr(som2,result)

        for (so1,so2) in map(None,som1,som2):
            result.append(rebin_so_so(so1,so2))

        return result

    def rebin_so_so(so1,so2):
        # do the rebinning
        result=hlr_rebin_axis_1D.rebin_axis_1D(so2, so1.x)
        result.id=so2.id

        return result

    # check to see of obj1 is a SOM
    try:
        obj1.attr_list[TITLE]
        try:
            obj2.attr_list[TITLE]
            return rebin_som_som(obj1,obj2)
        except AttributeError:
            try:
                obj2.id
                raise TypeError, "SOM-SO operation is not supported"
            except AttributeError:
                raise TypeError, "Do not understand type of second argument"
            
    except AttributeError:
        pass

    # check to see of obj1 is a SO
    try:
        obj1.id
        try:
            obj2.attr_list[TITLE]
            raise TypeError, "SO-SOM operation is not supported"
        except AttributeError:
            try:
                obj2.id
                return rebin_so_so(obj1,obj2)
            except AttributeError:
                raise TypeError, "Do not understand type of second argument."
            
    except AttributeError:
        raise TypeError, "Do not understand type of first argument."


if __name__=="__main__":
    X_UNITS=SOM.som.SOM.X_UNITS
    
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

    som1=SOM.som.SOM()
    som1.attr_list[X_UNITS]="Angstroms"
    count=0
    for i in range(2):
        so=generate_so(count,count+5)
        so.id=i+1
        som1.append(so)
        count+=5

    som2=SOM.som.SOM()
    som2.attr_list[X_UNITS]="Angstroms"
    so1=SOM.so.SO()    
    so1.id=1
    so1.x.extend(range(0,7,2))
    so1.y.extend(0.994,0.943,0.932)
    so1.var_y.extend(0.010,0.012,0.013)
    som2.append(so1)
    so2=SOM.so.SO()    
    so2.id=2
    so2.x.extend(range(0,7,2))
    so2.y.extend(0.934,0.986,0.957)
    so2.var_y.extend(0.011,0.010,0.015)
    som2.append(so2)
    
    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1]

    print "********** SOM2"
    print "* ",som2[0]
    print "* ",som2[1]

    print "********** rebin_efficiency"
    print "* so +so  :",rebin_efficiency(som1[0],som2[0])
    print "* som+som :",rebin_efficiency(som1,som2)
    
