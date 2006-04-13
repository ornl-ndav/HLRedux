import SOM

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
    


if __name__=="__main__":
    import hlr_test
    
    som1=hlr_test.generate_som()
        
    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1]

    print "********** subtract_time_indep_bkg"
    print "* som -scal   :",subtract_time_indep_bkg(som1,[(3,1)])
    print "* som -l(scal):",subtract_time_indep_bkg(som1,[(1,1), (2,1)])
    print "* so  -scal   :",subtract_time_indep_bkg(som1[0],[(1,1)])


