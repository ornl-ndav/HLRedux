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
    primary axis. If the integration range for a pixel cannot be found, an
    error report will be generated with the following information:
       Range not found: pixel ID, start bin, end bin, length of data array
    A failing pixel will have the integration tuple set to (nan, nan).

    Parameters:
    ----------
    -> obj is a SOM or SO that will have the integration calculated from it
    -> kwargs is a list of key word arguments that the function accepts:
          start=<index of starting bin>
          end=<index of ending bin>
    
    Return:
    ------
    <- SOM or a SO containing the integration and the uncertainty squared
       associated with the integration
    """

    # import the helper functions
    import hlr_utils

    if obj is None:
        return obj

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj)

    o_descr = hlr_utils.get_descr(obj)
    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)
    
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

        try:
            value = dr_lib.integrate_axis(obj1, start=b_start, end=b_end)
        except IndexError:
            print "Range not found:", obj1.id, b_start, b_end, len(obj1)
            value = (float('nan'), float('nan'))

        hlr_utils.result_insert(result, res_descr, value, obj1, "yonly")

    return result

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
