import SOM

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

if __name__=="__main__":
    import hlr_test
    
    som1=SOM.SOM()
    so1=hlr_test.generate_so("histogram",0,5,1,1)
    so1.id=1
    som1.append(so1)
    so2=hlr_test.generate_so("histogram",0,5,1,3)
    so2.id=2
    som1.append(so2)
    so3=hlr_test.generate_so("histogram",0,5,1,2)
    so3.id=3
    som1.append(so3)

    print "********** SOM1"
    print "* ",som1

    print "********** sum_all_spectra"
    print "* som:",sum_all_spectra(som1)

