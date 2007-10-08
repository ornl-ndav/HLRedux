#                  High-Level Reduction Functions
#           A part of the SNS Analysis Software Suite.
#
#                  Spallation Neutron Source
#          Oak Ridge National Laboratory, Oak Ridge TN.
#
#
#                             NOTICE
#
# For this software and its associated documentation, permission is granted
# to reproduce, prepare derivative works, and distribute copies to the public
# for any purpose and without fee.
#
# This material was prepared as an account of work sponsored by an agency of
# the United States Government.  Neither the United States Government nor the
# United States Department of Energy, nor any of their employees, makes any
# warranty, express or implied, or assumes any legal liability or
# responsibility for the accuracy, completeness, or usefulness of any
# information, apparatus, product, or process disclosed, or represents that
# its use would not infringe privately owned rights.
#

# $Id$

def subtract_bkg_from_data(data_som, bkg_som, **kwargs):
    """
    This function subtracts one data set from another. 

    @param data_som: Object containing the data to subtract from
    @type data_som: C{SOM.SOM} or C{SOM.SO}
    
    @param bkg_som: Object containing the data to be subtracted
    @type bkg_som: C{SOM.SOM} or C{SOM.SO}
    
    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword dataset1: The type name of the first dataset. Default is
                       I{dataset1}.
    @type dataset1: C{string}
    
    @keyword dataset2: The type name of the second dataset. Default is
                       I{dataset2}.

    @keyword scale: The constant by which to scale the background spectra
    @type scale: L{hlr_utils.DrParameter}
                       
    @keyword verbose: A flag for turning on information from the function.
    @type verbose: C{boolean}

    @keyword timer: Timing object so the function can perform timing
    @type timer: C{sns_timer.DiffTime}    
 

    @return: The data subtracted by the background
    @rtype: C{SOM.SOM} or C{SOM.SO}


    @raise TypeError: Both objects are not C{SOM}s, a C{SO} and a C{SOM} or
                      a C{SOM} and a C{SO}
    """

    # Kickout if data object is NoneType
    if data_som is None:
        return None

    # Kickout if background object is NoneType
    if bkg_som is None:
        return data_som

    # import the helper functions
    import hlr_utils

    (data_descr, bkg_descr) = hlr_utils.get_descr(data_som, bkg_som)

    if data_descr == "SOM" and bkg_descr == "SOM":
        hlr_utils.math_compatible(data_som, data_descr, bkg_som, bkg_descr)
    elif data_descr == "SOM" and bkg_descr == "SO" or \
         data_descr == "SO" and bkg_descr == "SOM":
        # You have SO-SOM or SOM-SO, so assume everything is OK
        pass        
    else:
        raise TypeError("The object combinations must be SOM-SOM, SO-SOM "\
                        +"or SOM-SO. You provided a %s and a %s" % \
                        (data_descr, bkg_descr))

    # Check for keywords
    try:
        verbose = kwargs["verbose"]
    except KeyError:
        verbose = False

    try:
        t = kwargs["timer"]
    except KeyError:
        t = None

    try:
        dataset1 = kwargs["dataset1"]
    except KeyError:
        dataset1 = "dataset1"

    try:
        dataset2 = kwargs["dataset2"]
    except KeyError:
        dataset2 = "dataset2"

    try:
        scale = kwargs["scale"]
    except KeyError:
        scale = None

    import common_lib

    if scale is not None:
        if verbose:
            print "Scaling %s for %s" % (dataset2, dataset1)
        
        bkg_som2 = common_lib.mult_ncerr(bkg_som, scale.toValErrTuple())
        
        if t is not None:
            t.getTime(msg="After scaling %s for %s " % (dataset2, dataset1))
    else:
        bkg_som2 = bkg_som

    del bkg_som

    if verbose:
        print "Subtracting %s from %s" % (dataset2, dataset1)
        
    data_som2 = common_lib.sub_ncerr(data_som, bkg_som2)

    if t is not None:
        t.getTime(msg="After subtracting %s from %s " % (dataset2, dataset1))

    return data_som2

if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som()
    som2 = hlr_test.generate_som()

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** SOM2"
    print "* ", som2[0]
    print "* ", som2[1]

    print "********** subtract_bkg_from_data"
    print "* som-som:", subtract_bkg_from_data(som1, som2)
    print "* som-so :", subtract_bkg_from_data(som1, som2[0])
    print "* so-som :", subtract_bkg_from_data(som1[0], som2)

    
    
