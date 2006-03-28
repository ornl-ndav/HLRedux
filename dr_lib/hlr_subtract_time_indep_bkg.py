import hlr_sub_ncerr
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

def subtract_time_indep_bkg(obj, B_list):
    """
    This function takes a SOM or a SO and a list of time-independent background
    tuples and subtracts the numbers from the appropriate SO in the SOM or the
    given SO. The list of tuples (could be just one tuple in the case of the
    SO) is assumed to be in the same order as the SOs in the SOM.

    Parameters:
    ----------
    -> obj is a SOM or SO from which to subtract the individual Bs from the
       B_list
    -> B_list are the time-independent backgrounds to subtract from the SOs in
       the SOM or a SO

    Return:
    -------
    <- A SOM or SO with the time-independent backgrounds subtracted

    Exceptions:
    ----------
    <- IndexError is raised if the B_list object is empty
    <- TypeError is raised if the first argument is not a SOM
    <- RuntimeError is raised if the SOM and list are not the same length
    """

    TITLE      = SOM.som.SOM.TITLE

    def sub_tib_som_num(som,num):
        # create empty result som
        result=SOM.som.SOM()

        # attributes from som
        copy_attr(som,result)

        for so in som:
            result.append(sub_tib_so_num(so,num))

        return result

    def sub_tib_som_list(som,list):
        if len(som) != len(list):
            raise RuntimeError, "SOM and list must be the same length!"
        
        # create empty result som
        result=SOM.som.SOM()

        # attributes from som
        copy_attr(som,result)

        for (so,num) in map(None,som,list):
            result.append(sub_tib_so_num(so,num))

        return result 

    def sub_tib_so_num(so,num):
        print num
        # do the math
        result=hlr_sub_ncerr.sub_ncerr(so,num)

        return result

    if len(B_list) <= 0:
        raise IndexError, "List of time-independent background cannot be empty"

    # check to see of obj is a SOM
    try:
        obj.attr_list[TITLE]
        if len(B_list) > 1:
            return sub_tib_som_list(obj, B_list)
        else:
            return sub_tib_som_num(obj, B_list[0])

    except AttributeError:
        pass

    # check to see if obj is a SO
    try:
        obj.id
        return sub_tib_so_num(obj, B_list[0])
            
    except AttributeError:
        raise TypeError, "First argument must be a SOM or a SO!"

if __name__=="__main__":
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

    print "********** SOM1"
    print "* ",so_to_str(som1[0])
    print "* ",so_to_str(som1[1])

    print "********** subtract_time_indep_bkg"
    print "* so  -scal   :",so_to_str(subtract_time_indep_bkg(som1[0],[(1,1)]))
    print "* som -l(scal):",subtract_time_indep_bkg(som1,[(1,1), (2,1)])
    print "* som -scal   :",subtract_time_indep_bkg(som1,[(3,1)])
