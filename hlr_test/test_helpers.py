import SOM

def generate_so(type,start,stop=0,dim=1,extra=0):
    """
    This function generates a SO for testing purposes. The SO can be either
    a histogram or density.

    Parameters:
    ----------
    -> type is defined as histogram or density
    -> start is the starting value for number generation
    -> stop (OPTIONAL) is the stopping value for number generation
    -> dim (OPTIONAL) allows for making SOs multi-dimensional

    Returns:
    -------
    <- A SO
    """
    
    if stop<start:
        stop=start
        start=0
        
    so=SOM.SO(dim)
    if start==stop:
        return so

    if type.lower() == "histogram":
        num = stop-start+1
    else:
        num = stop-start

    for i in range(dim):
        so.axis[i].val.extend(range(num))
        size = len(so.axis[i].val)

        if i == 0:
            so.y.extend(range(start+extra,stop+extra))
            so.var_y.extend(range(start+extra,stop+extra))
        else:
            for j in range(size - 2):
                so.y.extend(range(start+extra,stop+extra))
                so.var_y.extend(range(start+extra,stop+extra))

    return so


def generate_som(type="histogram",dim=1):
    """
    This function generates a SOM for testing purposes.

    Parameters:
    ----------
    -> type is defined as histogram or density

    Returns:
    -------
    <- A SOM
    """

    som = SOM.SOM()
    count=0
    for i in range(2):
        so=generate_so(type,count,count+5,dim)
        so.id=i+1
        som.append(so)
        count+=5

    return som
