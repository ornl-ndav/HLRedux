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

    # import the helper functions
    import hlr_utils

    # set up for working through data
    # This time highest object in the hierarchy is NOT what we need
    result = []
    res_descr = "number"
    (o_descr,d_descr)=hlr_utils.get_descr(obj)

    if(kwargs.has_key("start")):
        start=int(kwargs["start"])
    else:
        start=0

    if(kwargs.has_key("end")):
        end=int(kwargs["end"])
    else:
        end=hlr_utils.get_length(obj)-1
            
    result=hlr_utils.copy_som_attr(result,res_descr,obj,o_descr)

    # iterate through the values
    import utils
    
    for i in range(hlr_utils.get_length(obj)):
        val = hlr_utils.get_value(obj,i,o_descr,"y")
        err2 = hlr_utils.get_err2(obj,i,o_descr,"y")

        value=utils.weighted_average(val, err2, start, end)

        hlr_utils.result_insert(result,res_descr,value,None,"all")

    import copy
    return copy.deepcopy(result)


if __name__=="__main__":
    import hlr_test

    som1=hlr_test.generate_som()

    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1]

    print "********** weighted_average"
    print "* som      :",weighted_average(som1)
    print "* som [0,2]:",weighted_average(som1,start=0,end=2)
    print "* so       :",weighted_average(som1[0])
    print "* so  [1,3]:",weighted_average(som1[0],start=1,end=3)



