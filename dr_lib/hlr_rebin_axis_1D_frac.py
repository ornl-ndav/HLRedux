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

def rebin_axis_1D_frac(obj, axis_out):
    """
    This function rebins the primary axis for a C{SOM} or a C{SO} based on the
    given C{NessiList} axis.

    @param obj: Object to be rebinned
    @type obj: C{SOM.SOM} or C{SOM.SO}

    @param axis_out: The axis to rebin the C{SOM} or C{SO} to
    @type axis_out: C{NessiList}


    @return: Two objects that have been rebinned according to the provided
             axis. The first object contains the rebinned counts and the second
             contains the fractional area.
    @rtype: C{tuple} of two C{SOM.SOM}s or C{SOM.SO}s


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

    (result1, res1_descr) = hlr_utils.empty_result(obj)
    result1 = hlr_utils.copy_som_attr(result1, res1_descr, obj, o_descr)

    (result2, res2_descr) = hlr_utils.empty_result(obj)
    result2 = hlr_utils.copy_som_attr(result2, res2_descr, obj, o_descr)

    # iterate through the values
    import axis_manip

    len_obj = hlr_utils.get_length(obj)
    for i in xrange(len_obj):
        axis_in = hlr_utils.get_value(obj, i, o_descr, "x", 0)
        val = hlr_utils.get_value(obj, i, o_descr)
        err2 = hlr_utils.get_err2(obj, i, o_descr)

        value = axis_manip.rebin_axis_1D_frac(axis_in, val, err2, axis_out)

        frac_err = nessi_list.NessiList(len(value[2]))

        xvals = []
        xvals.append(axis_out)

        map_so = hlr_utils.get_map_so(obj, None, i)

        hlr_utils.result_insert(result1, res1_descr, (value[0], value[1]),
                                map_so, "all", 0, xvals)
        hlr_utils.result_insert(result2, res2_descr, (value[2], frac_err),
                                map_so, "all", 0, xvals)        

    return (result1, result2)

if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som()

    axis = nessi_list.NessiList()
    axis.extend(0, 2.5, 5)

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** rebin_axis_1D_frac"
    print "* rebin som:", rebin_axis_1D_frac(som1, axis)
    print "* rebin so :", rebin_axis_1D_frac(som1[0], axis)
