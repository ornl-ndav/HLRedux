import utils
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

def weighted_average(obj,**kwargs):
    """
    This function takes a SOM or SO and calculates the weighted average for
    the primary axis.

    Parameters:
    ----------
    -> obj is a SOM or SO that will have the weighted average calculated from
       it
    -> kwargs is a list of key word arguments that the function accepts:
          start=<index of starting bin>
          end=<index of ending bin>
    
    Return:
    ------
    <- A tuple (for a SO) or a list of tuples (for a SOM) containing the
       weighted average and the uncertainty squared associated with the
       weighted average

    Exceptions:
    ----------
    <- TypeError is raised if a tuple or another construct (besides a SOM or
       SO) is passed to the function
    """
    
    TITLE=SOM.som.SOM.TITLE

    if(kwargs.has_key("start")):
        start=kwargs["start"]
    else:
        start=0
        
    def weighted_average_som(som,start,end):

        w_averages = []

        for so in som:
            w_averages.append(weighted_average_so(so,start,end))

        return w_averages

    def weighted_average_so(so,start,end):

        (w_ave, w_ave_err2)=utils.weighted_average(so.y, so.var_y, start, end)

        return (w_ave,w_ave_err2)

    # determine if the obj is a som
    try:
        obj.attr_list[TITLE]
        if(kwargs.has_key("end")):
            end=kwargs["end"]
        else:
            end=len(obj[0])-1
            
        return weighted_average_som(obj, start, end)
    except AttributeError:
        pass

    # determine if obj is a so
    try:
        obj.id
        if(kwargs.has_key("end")):
            end=kwargs["end"]
        else:
            end=len(obj)-1

        return weighted_average_so(obj, start, end)
    except AttributeError:
        raise TypeError, "Do not know how to handle given type"

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
    count=1
    for i in range(2):
        so=generate_so(count,count+5)
        so.id=i+1
        som1.append(so)
        count+=5

    print "********** SOM1"
    print "* ",so_to_str(som1[0])
    print "* ",so_to_str(som1[1])

    print "********** weighted_average"
    print "* rebin so       :",weighted_average(som1[0])
    print "* rebin so [1,3] :",weighted_average(som1[0],start=1,end=3)
    print "* rebin som      :",weighted_average(som1)
    print "* rebin som [0,2]:",weighted_average(som1,start=0,end=2)


