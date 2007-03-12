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

def integrate_spectra(obj, **kwargs):
    """
    This function takes a SOM or SO and calculates the integration for the
    primary axis.

    Parameters:
    ----------
    -> obj is a SOM or SO that will have the integration calculated from it
    -> kwargs is a list of key word arguments that the function accepts:
          start=<index of starting bin>
          end=<index of ending bin>
    
    Return:
    ------
    <- A tuple (for a SO) or a list of tuples (for a SOM) containing the
       integration and the uncertainty squared associated with the integration

    Exceptions:
    ----------
    <- TypeError is raised if a tuple or another construct (besides a SOM or
       SO) is passed to the function
    """

    # import the helper functions
    import hlr_utils

    if obj is None:
        return obj

    # set up for working through data
    # This time highest object in the hierarchy is NOT what we need
    result = []
    if(hlr_utils.get_length(obj) > 1):
        res_descr = "list"
    else:
        res_descr = "number"

    o_descr = hlr_utils.get_descr(obj)

    # If the integration start bound is not given, assume the 1st bin
    try:
        i_start = kwargs["start"]
    except KeyError:
        i_start = 0

    # If the integration end bound is not given, assume the last bin
    try:
        i_end = kwargs["end"]
    except KeyError:
        i_end = -1
    
    # iterate through the values
    import bisect
    
    import dr_lib
    
    for i in xrange(hlr_utils.get_length(obj)):
        obj1 = hlr_utils.get_value(obj, i, o_descr, "all")

        # Find the bin in the y values corresponding to the start bound
        if i_start > 0:
            b_start = bisect.bisect(obj1.axis[0].val, i_start) - 1
        else:
            b_start = i_start

        # Find the bin in the y values corresponding to the end bound
        if i_end != -1:
            b_end = bisect.bisect(obj1.axis[0].val, i_end) - 1
        else:
            b_end = i_end
            
        value = dr_lib.integrate_axis(obj1, start=b_start, end=b_end)

        hlr_utils.result_insert(result, res_descr, value, None, "all")

    import copy
    return copy.deepcopy(result)

if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som()

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** integrate_spectra"
    print "som            :", integrate_spectra(som1)
    print "som (1.5, 3.5) :", integrate_spectra(som1, start=1.5, end=3.5)
    print "som (0.5, 2.75):", integrate_spectra(som1, start=0.5, end=2.75)