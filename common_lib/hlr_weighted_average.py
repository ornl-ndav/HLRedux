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
    ->
    
    Return:
    ------
    <-

    Exceptions:
    ----------
    <- 
    """
    
    TITLE=SOM.som.SOM.TITLE

    def weighted_average_som(obj,**kwargs):

        w_averages = []

        for so in som:
            w_averages.append(weighted_average_so(so,kwargs))

        return w_averages

    def weighted_average_so(obj,**kwargs):

        

    # determine if the obj is a som
    try:
        obj.attr_list[TITLE]
        return weighted_average_som(obj)

    except AttributeError:
        pass

    # determine if obj is a so
    try:
        obj.id
        return weighted_average_so(obj)
    except AttributeError:
        raise TypeError, "Do not know how to handle given type"



