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
    This function takes two SOMs, a SO and a SOM, two SOs, a tuple and a SOM,
    a tuple and a SO, and two tuples and calculates the energy transfer in
    units of THz. The SOM principle axes must be in units of meV. The SO and
    tuples are assumed to be in units of meV.

    Parameters:
    ----------
    -> left is a SOM, SO or tuple on the left side of the subtraction
    -> right is a SOM, SO or tuple on the right side of the subtraction

    Return:
    ------
    <- A SOM, SO or tuple based on left - right in units of THz

    Exceptions:
    ----------
    <- IndexError is raised if the two SOMs do not contain the same number
       of spectra
    <- RuntimeError is raised if the x-axis units of the SOMs do not match
    <- RuntimeError is raised if the x-axis units are not meV
    <- RuntimeError is raised if the y-axis units of the SOMs do not match
    <- RuntimeError is raised if the x-axes of the two SOs are not equal

    """

    TITLE=SOM.som.SOM.TITLE
    X_UNITS=SOM.som.SOM.X_UNITS
    Y_UNITS=SOM.som.SOM.Y_UNITS

    def et_som_som(som1,som2):
        # check that there is the same number of so
        if len(som1)!=len(som2):
            raise IndexError,"Can only add SOMs with same number of spectra"
        #check that the units match up
        if som1.attr_list[X_UNITS]!=som2.attr_list[X_UNITS]:
            raise RuntimeError,"X units do not match"
        if som1.attr_list[X_UNITS]!="meV":
            raise RuntimeError,"X units must be meV"
        if som1.attr_list[Y_UNITS]!=som2.attr_list[Y_UNITS]:
            raise RuntimeError,"Y units do not match"

        # create empty result som
        result=SOM.som.SOM()

        # attributes from som1 clobber those from som2
        copy_attr(som2,result)
        copy_attr(som1,result)

        # do the calculation
        for (so1,so2) in map(None,som1,som2):
            result.append(et_so_so(so1,so2))

        return result

    def et_som_so(som,so):
        # create empty result som
        result=SOM.som.SOM()

        # copy attributes from som
        copy_attr(som,result)

        # do the calculation
        for it in som:
            result.append(et_so_so(it,so))

        return result

    def et_so_som(so,som):
        # create empty result som
        result=SOM.som.SOM()

        # copy attributes from som
        copy_attr(som,result)

        # do the calculation
        for it in som:
            result.append(et_so_so(so,it))

        return result

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

    def et_so_so(so1,so2):
        if so1.x!=so2.x:
            raise RunTimeError,"x axes must be equal"

        # set up the result
        result=SOM.so.SO()
        result.id=so1.id
        result.x=so1.x

        # do the calculation
        (result.y,result.var_y)=axis_manip.energy_transfer(so1.y,so1.var_y,
                                                           so2.y,so2.var_y)

        return result

    def et_so_num(so,num):
        # set up the result
        result=SOM.so.SO()
        result.id=so.id
        result.x=so.x

        # do the calculation
        (result.y,result.var_y)=axis_manip.energy_transfer(so.y,so.var_y,
                                                           num[0],num[1])

        return result

    def et_num_so(num,so):
        # set up the result
        result=SOM.so.SO()
        result.id=so.id
        result.x=so.x

        # do the calculation
        (result.y,result.var_y)=axis_manip.energy_transfer(num[0],num[1],
                                                           so.y,so.var_y)

        return result

    def et_num_num(num1,num2):

        #do the calculation
        return axis_manip.energy_transfer(num1[0],num1[1],num2[0],num2[1])

    # determine if the left is a som
    try:
        left.attr_list[TITLE]
        try:
            right.attr_list[TITLE]
            return et_som_som(left,right)
        except AttributeError:
            try:
                right.id
                return et_som_so(left,right)
            except AttributeError:
                return et_som_num(left,right)
    except AttributeError: # left is a so
        pass

    # determine if left is a so
    try:
        left.id
        try:
            right.attr_list[TITLE]
            return et_so_som(left,right)
        except AttributeError:
            try:
                right.id
                return et_so_so(left,right)
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
    print "* so  -so  :",so_to_str(energy_transfer(som1[0],som1[1]))
    print "* som -scal:",energy_transfer(som1,(1,1))
    print "* scal-som :",energy_transfer((1,1),som1)
    print "* som -so  :",energy_transfer(som1,som1[0])
    print "* so  -som :",energy_transfer(som1[0],som1)
    print "* som -som :",energy_transfer(som1,som2)




