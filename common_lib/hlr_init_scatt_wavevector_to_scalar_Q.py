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

def init_scatt_wavevector_to_scalar_Q(initk,scattk):
    """
    This function takes an initial wavevector and a scattered wavevector as a
    tuple and a SOM, a tuple and a SO  or two tuples and calculates the
    quantity scalar_Q units of 1/Angstroms. The SOM principle axis must be in
    units of 1/Angstroms. The tuple(s) is(are) assumed to be in units of
    1/Angstroms.

    Parameters:
    ----------
    -> initk is a SOM, SO or tuple of the initial wavevector
    -> scattk is a SOM, SO or tuple of the scattered wavevector

    Return:
    ------
    <- A SOM, SO or tuple calculated for scalar_Q

    Exceptions:
    ----------
    <- TypeError is raised if the SOM-SOM operation is attempted
    <- TypeError is raised if the SOM-SO operation is attempted
    <- TypeError is raised if the SO-SOM operation is attempted
    <- TypeError is raised if the SO-SO operation is attempted
    <- RuntimeError is raised if the SOM x-axis units are not 1/Angstroms
    """

    TITLE=SOM.som.SOM.TITLE
    X_UNITS=SOM.som.SOM.X_UNITS

    def isk2sQ_som_num(som,num):
        if som.attr_list[X_UNITS]!="1/Angstroms":
            raise RuntimeError,"X units are not 1/Angstroms"

        # create empty result som
        result=SOM.som.SOM()

        # copy attributes from som
        copy_attr(som,result)

        # do the calculation
        for it in som:
            result.append(isk2sQ_so_num(it,num))

        return result

    def isk2sQ_num_som(num,som):
        if som.attr_list[X_UNITS]!="1/Angstroms":
            raise RuntimeError,"X units are not 1/Angstroms"

        # create empty result som
        result=SOM.som.SOM()

        # copy attributes from som
        copy_attr(som,result)

        # do the calculation
        for it in som:
            result.append(isk2sQ_num_so(num,it))

        return result

    def isk2sQ_so_num(so,num):
        # BEGIN SNS-FIXME
        import nessi_list
        # dummy placeholder for x variance
        # list is set to zero (I hope)
        so_var_x=nessi_list.NessiList(len(so.x))
        polar = [0.785398163, 0.01]
        # END SNS-FIXME

        # set up the result
        result=SOM.so.SO()
        result.id=so.id
        result.y=so.y
        result.var_y=so.var_y

        (result.x,\
         var_x_throwaway)\
         =axis_manip.init_scatt_wavevector_to_scalar_Q(so.x,
                                                       so_var_x,
                                                       num[0],
                                                       num[1],
                                                       polar[0],
                                                       polar[1])

        return result

    def isk2sQ_num_so(num,so):
        # BEGIN SNS-FIXME
        import nessi_list
        # dummy placeholder for x variance
        # list is set to zero (I hope)
        so_var_x=nessi_list.NessiList(len(so.x))
        polar = [0.785398163, 0.01]
        # END SNS-FIXME

        # set up the result
        result=SOM.so.SO()
        result.id=so.id
        result.y=so.y
        result.var_y=so.var_y

        (result.x,\
         var_x_throwaway)\
         =axis_manip.init_scatt_wavevector_to_scalar_Q(num[0],
                                                       num[1],
                                                       so.x,
                                                       so_var_x,
                                                       polar[0],
                                                       polar[1])

        return result

    def isk2sQ_num_num(num1,num2):
        # BEGIN SNS-FIXME
        polar = [0.785398163, 0.01]
        # END SNS-FIXME

        (scalar_Q,\
         scalar_Q_err2)\
         =axis_manip.init_scatt_wavevector_to_scalar_Q(num1[0], num1[1],
                                                       num2[0], num2[1],
                                                       polar[0], polar[1])

        return scalar_Q,scalar_Q_err2

    # determine if the initk is a som
    try:
        initk.attr_list[TITLE]
        try:
            scattk.attr_list[TITLE]
            raise TypeError, "SOM-SOM operation not supported"
        except AttributeError:
            try:
                scattk.id
                raise TypeError, "SOM-SO operation not supported"
            except AttributeError:
                return isk2sQ_som_num(initk,scattk)
    except AttributeError: # initk is a so
        pass

    # determine if initk is a so
    try:
        initk.id
        try:
            scattk.attr_list[TITLE]
            raise TypeError, "SO-SOM operation not supported"
        except AttributeError:
            try:
                scattk.id
                raise TypeError, "SO-SO operation not supported"
            except AttributeError:
                return isk2sQ_so_num(initk,scattk)
    except AttributeError: # initk is a tuple
        pass

    # initk must be a tuple
    try:
        scattk.attr_list[TITLE]
        return isk2sQ_num_som(initk,scattk)
    except AttributeError:
        try:
            scattk.id
            return isk2sQ_num_so(initk,scattk)
        except AttributeError:
            return isk2sQ_num_num(initk,scattk)

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
    som1.attr_list[X_UNITS]="1/Angstroms"
    count=0
    for i in range(2):
        so=generate_so(count,count+5)
        so.id=i+1
        som1.append(so)
        count+=5

    print "********** SOM1"
    print "* ",so_to_str(som1[0])
    print "* ",so_to_str(som1[1])

    print "********** init_scatt_wavevector_to_scalar_Q"
    print "* scal-scal:",init_scatt_wavevector_to_scalar_Q((2,1),(1,1))
    print "* so  -scal:",so_to_str(init_scatt_wavevector_to_scalar_Q(som1[0],\
                                                                     (1,1)))
    print "* scal-so  :",so_to_str(init_scatt_wavevector_to_scalar_Q((1,1),\
                                                                     som1[0]))
    print "* som -scal:",init_scatt_wavevector_to_scalar_Q(som1,(1,1))
    print "* scal-som :",init_scatt_wavevector_to_scalar_Q((1,1),som1)




