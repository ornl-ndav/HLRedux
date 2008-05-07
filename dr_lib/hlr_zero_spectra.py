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

def zero_spectra(obj, nz_range):
    """
    This function takes spectra and a corrsponding range and zeros the values
    in the spectra outside the given range.

    @param obj: The object containing the spectra to be zeroed
    @type obj: C{SOM.SOM}

    @param nz_range: Range pairs where the spectra will not be zeroed
    @type nz_range: C{list} of C{tuple}s


    @return: Object containing the zeroed spectra
    @rtype: C{SOM.SOM}


    @raise RuntimeError: If I{obj} and I{nz_range} do not have the same length
    """
    # import the helper functions
    import hlr_utils

    # Kickout if incoming object is NoneType
    if obj is None:
        return obj

    # Length cross-check
    if len(obj) != len(nz_range):
        raise RuntimeError("The SOM and the range pair list must be the same "\
                           +"length")

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj)
    o_descr = hlr_utils.get_descr(obj)

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)

    # iterate through the values
    import bisect

    import nessi_list

    for i in xrange(hlr_utils.get_length(obj)):
        map_so = hlr_utils.get_map_so(obj, None, i)

        # Get information from SOM
        y_val = hlr_utils.get_value(obj, i, o_descr, "y")
        y_err2 = hlr_utils.get_err2(obj, i, o_descr, "y")
        x_axis = hlr_utils.get_value(obj, i, o_descr, "x", 0)
        
        y_new = nessi_list.NessiList(len(y_val))
        var_y_new = nessi_list.NessiList(len(y_err2))

        # Find the bins for the range to not zero
        i_start = bisect.bisect(x_axis, nz_range[i][0]) - 1
        i_end = bisect.bisect(x_axis, nz_range[i][1]) - 1
        
        for j in xrange(i_start, i_end+1):
            try:
                y_new[j] = y_val[j]
                var_y_new[j] = y_err2[j]
            except IndexError:
                continue

        hlr_utils.result_insert(result, res_descr, (y_new, var_y_new),
                                map_so, "y")

    return result

if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som("histogram")

    out_range = []
    out_range.append((1.5, 3.2))
    out_range.append((0.2, 2.1))

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** zero_spectra"
    print "* som: ", zero_spectra(som1, out_range)
