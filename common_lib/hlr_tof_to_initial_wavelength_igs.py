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

def tof_to_initial_wavelength_igs(obj,**kwargs):
    """
    This function converts a primary axis of a SOM or SO from time-of-flight
    to initial_wavelength_igs. The time-of-flight axis for a SOM must be in
    units of microseconds. The primary axis of a SO is assumed to be in units
    of microseconds. A tuple of [tof, tof_err2] (assumed to be in units of
    microseconds) can be converted to [initial_wavelength_igs,
    initial_wavelength_igs_err2].

    Parameters:
    ----------
    -> obj is the SOM, SO or tuple to be converted

    Return:
    ------
    <- A SOM or SO with a primary axis in time-of-flight or a tuple converted
       to initial_wavelength_igs

    Exceptions:
    ----------
    <- TypeError is raised if the incoming object is not a type the function
       recognizes
    <- RuntimeError is raised if the SOM x-axis units are not microseconds
    """

    TITLE=SOM.som.SOM.TITLE
    X_UNITS=SOM.som.SOM.X_UNITS

    def t2iwi_som(som):
        if som.attr_list[X_UNITS]!="microseconds":
            raise RuntimeError,"X units are not microseconds"

        # create empty result som
        result=SOM.som.SOM()

        copy_attr(som,result)

        for so in som:
            result.append(t2iwi_so(so))

        return result

    def t2iwi_so(so):
        # BEGIN SNS-FIXME
        import nessi_list
        # dummy placeholder for x variance
        # list is set to zero (I hope)
        so_var_x=nessi_list.NessiList(len(so.x))
        lambda_f = [7.0, 0.1]
        t_0 = [0.1, 0.001]
        L_s = [15.0, 0.1]
        L_d = [1.0, 0.05]
        # END SNS-FIXME

        # set up the result
        result=SOM.so.SO()
        result.id=so.id
        result.y=so.y
        result.var_y=so.var_y

        (result.x,
         var_x_throwaway)\
         =axis_manip.tof_to_initial_wavelength_igs(so.x,
                                                   so_var_x,
                                                   lambda_f[0],
                                                   lambda_f[1],
                                                   t_0[0], t_0[1],
                                                   L_s[0], L_s[1],
                                                   L_d[0], L_d[1])

        return result

    def t2iwi_num(num):
        # do the calculation
        # BEGIN SNS-FIXME
        lambda_f = [7.0, 0.1]
        t_0 = [0.1, 0.001]
        L_s = [15.0, 0.1]
        L_d = [1.0, 0.05]
        # END SNS-FIXME
        (initial_wavelength_igs, \
         initial_wavelength_igs_err2)\
         =axis_manip.tof_to_initial_wavelength_igs(num[0],
                                                   num[1],
                                                   lambda_f[0],
                                                   lambda_f[1],
                                                   t_0[0], t_0[1],
                                                   L_s[0], L_s[1],
                                                   L_d[0], L_d[1])

        return initial_wavelength_igs,initial_wavelength_igs_err2

    # determine if the obj is a som
    try:
        obj.attr_list[TITLE]
        return t2iwi_som(obj)

    except AttributeError: # obj is a so
        pass

    # determine if obj is a so
    try:
        obj.id
        return t2iwi_so(obj)

    except AttributeError:
        pass

    # obj must be a tuple
    return t2iwi_num(obj)

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
    som1.attr_list[X_UNITS]="microseconds"
    count=0
    for i in range(2):
        so=generate_so(count,count+5)
        so.id=i+1
        som1.append(so)
        count+=5

    print "********** SOM1"
    print "* ",so_to_str(som1[0])
    print "* ",so_to_str(som1[1])

    print "********** tof_to_initial_wavelength_igs"
    print "* rebin so :",so_to_str(tof_to_initial_wavelength_igs(som1[0]))
    print "* rebin som:",tof_to_initial_wavelength_igs(som1)


