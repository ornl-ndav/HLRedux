import hlr_sumw_ncerr
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

def sum_all_spectra(obj):
    """
    This function takes all the SOs in a SOM and sums them together using the
    summing by weights concept. All of the SOs are assumed to have the same
    axis scale.
    
    Parameters:
    ----------
    -> obj is a SOM in which all of the SOs are to be summed together

    Returns:
    -------
    <- A SOM containing a single spectrum

    Exceptions:
    ----------
    <- TypeError is raised if anything other than a SOM is given 
    """
    
    TITLE      = SOM.som.SOM.TITLE
    
    def sum_all_som(som):
        # create empty result som
        result=SOM.som.SOM()

        copy_attr(som,result)

        temp_so=SOM.so.SO()
        temp_so_id=[]
        
        for i in range(len(som)):
            if i == 0:
                temp_so = hlr_sumw_ncerr.sumw_ncerr(som[i],som[i+1])
                temp_so_id.append(som[i].id)
                temp_so_id.append(som[i+1].id)
            elif i == 1:
                pass
            else:
                temp_so = hlr_sumw_ncerr.sumw_ncerr(som[i],temp_so)
                temp_so_id.append(som[i].id)

        temp_so.id = tuple(temp_so_id)
        result.append(temp_so)

        return result

    try:
        obj.attr_list[TITLE]
        return sum_all_som(obj)
    
    except AttributeError:
        raise TypeError, "Function argument must be a SOM"

if __name__=="__main__":
    def generate_so(start,stop=0,extra=1):
        if stop<start:
            stop=start
            start=0

        so=SOM.so.SO()
        if start==stop:
            return so

        so.x.extend(range(start,stop+1))
        so.y.extend(range(start+extra,stop+extra))
        so.var_y.extend(range(start+extra,stop+extra))
        return so


    som1=SOM.som.SOM()
    so1=generate_so(0,5)
    so1.id=1
    som1.append(so1)
    so2=generate_so(0,5,3)
    so2.id=2
    som1.append(so2)
    so3=generate_so(0,5,2)
    so3.id=3
    som1.append(so3)
    

    print "********** SOM1"
    print "* ",som1

    print "********** sum_all_spectra"
    print "* sum som:",sum_all_spectra(som1)

