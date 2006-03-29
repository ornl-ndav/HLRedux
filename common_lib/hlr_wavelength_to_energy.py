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

def wavelength_to_energy(obj):
    """
    This function converts a primary axis of a SOM or SO from wavelength
    to energy. The wavelength axis for a SOM must be in units of Angstroms.
    The primary axis of a SO is assumed to be in units of Angstroms. A tuple
    of [wavelength, wavelength_err2] (assumed to be in units of Angstroms) can
    be converted to [energy, energy_err2].

    Parameters:
    ----------
    -> obj is the SOM, SO or tuple to be converted

    Return:
    ------
    <- A SOM or SO with a primary axis in energy or a tuple converted to
       energy

    Exceptions:
    ----------
    <- TypeError is raised if the incoming object is not a type the function
       recognizes
    <- RuntimeError is raised if the SOM x-axis units are not Angstroms
    """

    TITLE=SOM.som.SOM.TITLE
    X_UNITS=SOM.som.SOM.X_UNITS

    def w2e_som(som):
        if som.attr_list[X_UNITS]!="Angstroms":
            raise RuntimeError,"X units are not Angstroms"

        # create empty result som
        result=SOM.som.SOM()

        copy_attr(som,result)

        for so in som:
            result.append(w2e_so(so))

        return result

    def w2e_so(so):
        # BEGIN SNS-FIXME
        import nessi_list
        # dummy placeholder for x variance
        # list is set to zero (I hope)
        so_var_x=nessi_list.NessiList(len(so.x))
        # END SNS-FIXME

        # set up the result
        result=SOM.so.SO()
        result.id=so.id
        result.y=so.y
        result.var_y=so.var_y

        (result.x, var_x_throwaway)=axis_manip.wavelength_to_energy(so.x,
                                                                    so_var_x)

        rev_var_y = result.var_y
        rev_y = result.y
        rev_x = result.x

        result.x = axis_manip.reverse_array_cp(rev_x)
        result.y = axis_manip.reverse_array_cp(rev_y)
        result.var_y = axis_manip.reverse_array_cp(rev_var_y)

        return result

    def w2e_num(num):
        # do the calculation
        (energy, energy_err2)=axis_manip.wavelength_to_energy(num[0],num[1])

        return energy,energy_err2

    # determine if the obj is a som
    try:
        obj.attr_list[TITLE]
        return w2e_som(obj)

    except AttributeError: # obj is a so
        pass

    # determine if obj is a so
    try:
        obj.id
        return w2e_so(obj)

    except AttributeError:
        pass

    # obj must be a tuple
    return w2e_num(obj)

    raise TypeError,"Do not know what to do with supplied types"

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

    def so_to_str(so):
        if so==None:
            return None
        else:
            return so.id,so.x,so.y,so.var_y

    som1=SOM.som.SOM()
    som1.attr_list[X_UNITS]="Angstroms"
    count=0
    for i in range(2):
        so=generate_so(count,count+5)
        so.id=i+1
        som1.append(so)
        count+=5

    print "********** SOM1"
    print "* ",so_to_str(som1[0])
    print "* ",so_to_str(som1[1])

    print "********** wavelength_to_energy"
    print "* rebin so :",so_to_str(wavelength_to_energy(som1[0]))
    print "* rebin som:",wavelength_to_energy(som1)

