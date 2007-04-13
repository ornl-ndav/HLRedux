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
    This function subtracts one data set from another. The data sets must be
    either two SOMs, a SO and a SOM or a SOM and a SO.

    Parameters:
    ----------
    -> data_som is a SOM or a SO containing the data to subtract from
    -> bkg_som is a SOM or a SO containing the data to be subtracted
    -> kwargs is a list of key word arguments that the function accepts:
         dataset1=<string> is a the type name of the first dataset. Default is
                           dataset1
         dataset2=<string> is a the type name of the second dataset. Default is
                           dataset2
         verbose=<boolean> is a flag for turning on information from the
                           function
         timer=<DiffTime> provides a DiffTime object so the function can
                          perform timing estimates
    Returns:
    -------
    <- The data subtracted by the background 

    Exceptions:
    ----------
    <- TypeError is raised if both objects are not SOMs, a SO and a SOM or
       a SOM and a SO
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
        hlr_utils.hlr_math_compatible(data_som, data_descr, bkg_som, bkg_descr)
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

    if verbose:
        print "Subtracting %s from %s" % (dataset2, dataset1)

    import common_lib
    
    data_som2 = common_lib.sub_ncerr(data_som, bkg_som)

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

    
    
