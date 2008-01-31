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

import nessi_list

def rebin_axis_1D_linint(obj, axis_out):
    """
    This function rebins the primary axis for a C{SOM} or a C{SO} based on the
    given C{NessiList} axis using a linear interpolation scheme.

    @param obj: Object to be rebinned
    @type obj: C{SOM.SOM} or C{SOM.SO}

    @param axis_out: The axis to rebin the C{SOM} or C{SO} to
    @type axis_out: C{NessiList}


    @return: Object that has been rebinned according to the provided axis
    @rtype: C{SOM.SOM} or C{SOM.SO}


    @raise TypeError: The rebinning axis given is not a C{NessiList}

    @raise TypeError: The object being rebinned is not a C{SOM} or a C{SO}
    """

    # import the helper functions
    import hlr_utils

    # set up for working through data
    try:
        axis_out.__type__
    except AttributeError:
        raise TypeError("Rebinning axis must be a NessiList!")

    o_descr = hlr_utils.get_descr(obj)

    if o_descr == "number" or o_descr == "list":
        raise TypeError("Do not know how to handle given type: %s" % \
                        o_descr)
    else:
        pass

    (result, res_descr) = hlr_utils.empty_result(obj)

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)

    # Axis out never changes
    xvals = []
    xvals.append(axis_out)

    # Need a vector of zeros for the next function call
    len_axis_out = len(axis_out)
    zero_vec = nessi_list.NessiList(len_axis_out)

    import utils
    bin_centers = utils.calc_bin_centers(axis_out, zero_vec)

    # iterate through the values
    
    for i in xrange(hlr_utils.get_length(obj)):
        axis_in = hlr_utils.get_value(obj, i, o_descr, "x", 0)
        axis_in_err2 = hlr_utils.get_err2(obj, i, o_descr, "x", 0)

        axis_in_bc = utils.calc_bin_centers(axis_in, axis_in_err2)

        val = hlr_utils.get_value(obj, i, o_descr)
        err2 = hlr_utils.get_err2(obj, i, o_descr)

        map_so = hlr_utils.get_map_so(obj, None, i)

        # Set zero errors to 1 for linear fit
        for j in xrange(len(err2)):
            if utils.compare(err2[j], 0.0) == 0 and \
                   utils.compare(val[j], 0.0) == 0:
                err2[j] = 1.0

        # Create new NessiLists for rebinned values
        rebin_val = nessi_list.NessiList()
        rebin_err2 = nessi_list.NessiList()

        for k in xrange(len_axis_out-1):
            index_pair = hlr_utils.bisect_helper(axis_in, axis_out[k],
                                                 axis_out[k+1])

            # Requested range is outside axis boundaries
            if index_pair[0] == -1 and index_pair[1] == -1:
                rebin_val.append(0.0)
                rebin_err2.append(0.0)
                continue

            # If there is only one value, just use it directly
            if index_pair[0] == index_pair[1]:
                rebin_val.append(val[index_pair[0]])
                rebin_err2.append(err2[index_pair[0]])
            else:
                # Do linear interpolation
                fit_params = utils.fit_linear_background(axis_in_bc[0],
                                                         val, err2,
                                                         index_pair[0],
                                                         index_pair[1])

                # Evaluate the interpolation at the rebin axis bin center
                eval_out = utils.eval_linear_fit(bin_centers[0][k:k+1],
                                                 bin_centers[1][k:k+1],
                                                 fit_params["slope"][0],
                                                 fit_params["slope"][1],
                                                 fit_params["intercept"][0],
                                                 fit_params["intercept"][1])

                rebin_val.append(eval_out[0][0])

                # Use a geometric average for the error bars
                new_err2 = 0.0
                count = 0
                for m in xrange(index_pair[0], index_pair[1]+1):
                    if utils.compare(val[m], 0.0) == 0:
                        continue
                    else:
                        new_err2 += err2[m]
                        count += 1

                if count:
                    new_err2 /= float(count)
                rebin_err2.append(new_err2)

        # Do one last clean up
        for n in xrange(len(rebin_val)):
            if utils.compare(rebin_val[n], 0.0) == 0:
                rebin_err2[n] = 0.0
        
        hlr_utils.result_insert(result, res_descr, (rebin_val, rebin_err2),
                                map_so, "all", 0, xvals)

    return result

if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som()

    axis = nessi_list.NessiList()
    axis.extend(0, 2.5, 5)

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** rebin_axis_1D_linint"
    print "* rebin som:", rebin_axis_1D_linint(som1, axis)
    print "* rebin so :", rebin_axis_1D_linint(som1[0], axis)
