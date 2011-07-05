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

def sum_spectra_weighted_ave(obj):
    """
    This function takes a set of data and sums the individual bins by weighted
    average. That information is then assembled back into a single spectrum.
    The individual spectra should already have been rebinned.
    
    @param obj: Object containing data spectra
    @type obj: C{SOM.SOM} or C{SOM.SO}


    @return: The summed spectra (one)
    @rtype: C{SOM.SOM}
    """
    
    if obj is None:
        return None

    # import the helper functions
    import hlr_utils

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj)
    o_descr = hlr_utils.get_descr(obj)

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)

    # Get the number of axis channels
    len_axis = len(obj[0])

    import nessi_list
    import SOM
    import utils

    # Empty SO for final spctrum
    so = SOM.SO()

    len_som = hlr_utils.get_length(obj)

    # Slice data, calculate weighted average and repackage spectra
    for i in xrange(len_axis):

        sliced_data = nessi_list.NessiList()
        sliced_data_err2 = nessi_list.NessiList()

        for j in xrange(len_som):
            obj1 = hlr_utils.get_value(obj, j, o_descr, "all")
            if i == 0 and j == 0:
                map_so = hlr_utils.get_map_so(obj, None, j)
                hlr_utils.result_insert(so, "SO", map_so, None, "all")
            
            sliced_data.append(obj1.y[i])
            sliced_data_err2.append(obj1.var_y[i])

        len_fit = len(sliced_data)

        value = utils.weighted_average(sliced_data, sliced_data_err2,
                                       0, len_fit-1)
        so.y[i] = value[0]
        so.var_y[i] = value[1]

    hlr_utils.result_insert(result, res_descr, so, None, "all")

    return result

if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som("histogram", 1, 6)
    som1[0].id = ("bank1", (128, 0))
    som1[1].id = ("bank1", (128, 1))
    som1[2].id = ("bank1", (128, 2))
    som1[3].id = ("bank1", (128, 3))
    som1[4].id = ("bank1", (128, 4))
    som1[5].id = ("bank1", (128, 5))

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]
    print "* ", som1[2]
    print "* ", som1[3]
    print "* ", som1[4]
    print "* ", som1[5]

    print "********** sum_spectra_weighted_ave"
    print "* som: ", sum_spectra_weighted_ave(som1)
