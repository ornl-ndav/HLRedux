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

def energy_transfer(left,right):
    """
    This function takes a tuple and a SOM, a tuple and a SO or two tuples and
    calculates the energy transfer in units of THz. The SOM principle axis
    must be in units of meV. The SO and tuples are assumed to be in units of
    meV.

    Parameters:
    ----------
    -> left is a SOM, SO or tuple on the left side of the subtraction
    -> right is a SOM, SO or tuple on the right side of the subtraction

    Return:
    ------
    <- A SOM, SO or tuple based on left - right in units of THz

    Exceptions:
    ----------

    <- RuntimeError is raised if the x-axis units are not meV
    """

    TITLE=SOM.som.SOM.TITLE
    X_UNITS=SOM.som.SOM.X_UNITS

    def et_som_num(som,num):
        # create empty result som
        result=SOM.som.SOM()

        # copy attributes from som
        copy_attr(som,result)

        # do the calculation
        for it in som:
            result.append(et_so_num(it,num))

        return result

    def et_num_som(num,som):
        # create empty result som
        result=SOM.som.SOM()

        # copy attributes from som
        copy_attr(som,result)

        # do the calculation
        for it in som:
            result.append(et_num_so(num,it))

        return result

    def et_so_num(so,num):
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

        # do the calculation
        (result.x,var_x_throwaway)=axis_manip.energy_transfer(so.x,so_var_x,
                                                              num[0],num[1])

        return result

    def et_num_so(num,so):
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

        # do the calculation
        (result.x,var_x_throwaway)=axis_manip.energy_transfer(num[0],num[1],
                                                              so.x,so_var_x)

        return result

    def et_num_num(num1,num2):

        #do the calculation
        return axis_manip.energy_transfer(num1[0],num1[1],num2[0],num2[1])

    # determine if the left is a som
    try:
        left.attr_list[TITLE]
        try:
            right.attr_list[TITLE]
            raise TypeError, "SOM-SOM operation not supported"
        except AttributeError:
            try:
                right.id
                raise TypeError, "SOM-SO operation not supported"
            except AttributeError:
                return et_som_num(left,right)
    except AttributeError: # left is a so
        pass

    # determine if left is a so
    try:
        left.id
        try:
            right.attr_list[TITLE]
            raise TypeError, "SO-SOM operation not supported"
        except AttributeError:
            try:
                right.id
                raise TypeError, "SO-SO operation not supported"
            except AttributeError:
                return et_so_num(left,right)
    except AttributeError: # left is a tuple
        pass

    # left must be a tuple
    try:
        right.attr_list[TITLE]
        return et_num_som(left,right)
    except AttributeError:
        try:
            right.id
            return et_num_so(left,right)
        except AttributeError:
            return et_num_num(left,right)

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
    som1.attr_list[X_UNITS]="meV"
    count=0
    for i in range(2):
        so=generate_so(count,count+5)
        so.id=i+1
        som1.append(so)
        count+=5

    som2=SOM.som.SOM()
    som2.attr_list[X_UNITS]="meV"
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

    print "********** energy_transfer"
    print "* scal-scal:",energy_transfer((2,1),(1,1))
    print "* so  -scal:",so_to_str(energy_transfer(som1[0],(1,1)))
    print "* scal-so  :",so_to_str(energy_transfer((1,1),som1[0]))
    print "* som -scal:",energy_transfer(som1,(1,1))
    print "* scal-som :",energy_transfer((1,1),som1)




