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

def zero_bins(obj, z_bins):
    """
    This function takes spectra and a set of bins and zeros the values in each
    spectrum at the bin location.

    @param obj: The object containing the spectra to be zeroed
    @type obj: C{SOM.SOM}

    @param z_bins: The set of bins from a given spectrum that will be zeroed
    @type z_bins: C{list} of C{int}s
    

    @return: Object containing the spectra with zeroed bins
    @rtype: C{SOM.SOM}


    @raise TypeError: The first argument is not a C{SOM} or C{SO}    
    """
    # Kickout if there are no bins to zero
    if z_bins is None:
        return obj
    
    # import the helper functions
    import hlr_utils

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj)
    o_descr = hlr_utils.get_descr(obj)

    if o_descr == "number" or o_descr == "list":
        raise TypeError("First argument must be a SOM or a SO!")
    # Have a SOM or SO, go on
    else:
        pass

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)

    # iterate through the values
    import nessi_list

    for i in xrange(hlr_utils.get_length(obj)):
        map_so = hlr_utils.get_map_so(obj, None, i)

        # Get information from SOM
        y_val = hlr_utils.get_value(obj, i, o_descr, "y")
        y_err2 = hlr_utils.get_err2(obj, i, o_descr, "y")

        y_new = nessi_list.NessiList()
        var_y_new = nessi_list.NessiList()

        for j in xrange(len(y_val)):
            if j in z_bins:
                y_new.append(0.0)
                var_y_new.append(0.0)            
            else:
                y_new.append(y_val[j])
                var_y_new.append(y_err2[j])

        hlr_utils.result_insert(result, res_descr, (y_new, var_y_new),
                                map_so, "y")

    return result    

if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som("histogram")

    out_range = [1, 3]

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** zero_bins"
    print "* som: ", zero_bins(som1, out_range)
