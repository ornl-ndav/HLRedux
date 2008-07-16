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

def cut_spectra(obj, low_cut, high_cut):
    """
    This function takes spectra and a given set of axis cutoff values and
    produces spectra that is smaller than the original by removing information
    outside the cut range.
    
    @param obj: The object containing the spectra to be zeroed
    @type obj: C{SOM.SOM}

    @param low_cut: The low-side axis cutoff. All values less than this will
                    be discarded.
    @type low_cut: C{float}

    @param high_cut: The high-side axis cutoff. All values greater than this
                     will be discarded.
    @type high_cut: C{float}    


    @return: Object containing the zeroed spectra
    @rtype: C{SOM.SOM}

    """
    # Kickout if both cuts are None
    if low_cut is None and high_cut is None:
        return obj

    # import the helper functions
    import hlr_utils

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj)
    o_descr = hlr_utils.get_descr(obj)

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)

    # iterate through the values
    import utils

    # Get object length
    len_obj = hlr_utils.get_length(obj)
    for i in xrange(len_obj):
        map_so = hlr_utils.get_map_so(obj, None, i)
        axis = hlr_utils.get_value(obj, i, o_descr, "x", 0)
        
        if low_cut is None:
            low_bin = 0
        else:
            low_bin = utils.bisect_helper(axis, low_cut)

        if high_cut is None:
            high_bin = len(axis)
        else:
            high_bin = utils.bisect_helper(axis, high_cut)

        y_new = map_so.y[low_bin:high_bin]
        var_y_new = map_so.var_y[low_bin:high_bin]
        axis_new = axis[low_bin:high_bin]
        
        hlr_utils.result_insert(result, res_descr, (y_new, var_y_new),
                                map_so, "all", 0, [axis_new])

    return result

if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som("histogram")

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** cut_spectra"
    print "* som: ", cut_spectra(som1, None, None)
    print "* som: ", cut_spectra(som1, 1.5, None)
    print "* som: ", cut_spectra(som1, None, 3.75)
    print "* som: ", cut_spectra(som1, 0.6, 2.7)
