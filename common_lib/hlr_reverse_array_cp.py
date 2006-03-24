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

def reverse_array_cp(obj):
    """
    This function reverses the y and var_y tuples of all the SOs in a SOM or
    an individual SO. This is assuming that there was a previous
    transformation on the x-axis of the SO or SOM.

    Parameters:
    ----------
    -> obj is the SOM or SO that needs to have its y and var_y tuples
       reversed

    Return:
    ------
    <- A SOM or SO containing the results of the reversal process

    Exceptions:
    ----------
    <- TypeError is raised if a tuple is presented to the function
    """

    TITLE      = SOM.som.SOM.TITLE

    def reverse_som(som):
        # create empty result som
        result=SOM.som.SOM()

        copy_attr(som,result)

        # do the reversing
        for so in som:
            result.append(reverse_so(so))

        return result

    def reverse_so(so):
        # set up the result
        result=SOM.so.SO()
        result.id=so.id
        result.x=so.x

        # do the reversing
        result.y = axis_manip.reverse_array_cp(so.y)
        result.var_y = axis_manip.reverse_array_cp(so.var_y)

        return result

    # determine if the obj is a som
    try:
        obj.attr_list[TITLE]
        return reverse_som(obj)
    except AttributeError:
        pass

    # determine if obj is a so
    try:
        obj.id
        return reverse_so(obj)

    except AttributeError:
        raise TypeError, "Do not understand how to reverse given type"

if __name__=="__main__":
    def generate_so(start,stop=0):
        if stop<start:
            stop=start
            start=0

        so=SOM.so.SO()
        if start==stop:
            return so

        so.x.extend(range(stop-start))
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

    print "********** reverse_array_cp"
    print "* rev so :",so_to_str(reverse_array_cp(som1[0]))
    print "* rev som:",reverse_array_cp(som1)
