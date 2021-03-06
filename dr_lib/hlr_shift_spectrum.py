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

def shift_spectrum(obj, shift_point, min_ext, max_ext, scale_const=None):
    """
    This function takes a given spectrum and a central value and creates
    a spectrum that is shifted about that point. Values greater than the point
    are moved to the beginning of the new spectrum and values less than the
    point are move towards the end of the new spectrum.
    
    @param obj: Monitor object that will be shifted
    @type obj: C{SOM.SOM} or C{SOM.SO}

    @param shift_point: The point in the spectrum about which to shift the
    data.
    @type shift_point: C{list} of C{floats}

    @param min_ext: The minimum extent of the axis to shift.
    @type min_ext: C{list} of C{floats}

    @param max_ext: The maximum extent of the axis to shift.
    @type max_ext: C{list} of C{floats}
    
    @param scale_const: A scaling constant to apply (multiply) to the newly
                        shifted spectrum. The default is I{None}.
    @type scale_const: C{float}


    @return: Monitor spectrum that have been shifted
    @rtype: C{SOM.SOM} or C{SOM.SO}
    """
    # import the helper functions
    import hlr_utils

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj)
    o_descr = hlr_utils.get_descr(obj)
    s_descr = hlr_utils.get_descr(shift_point)
    ie_descr = hlr_utils.get_descr(min_ext)
    ae_descr = hlr_utils.get_descr(max_ext)

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)

    import array_manip
    import utils

    len_obj = hlr_utils.get_length(obj)
    for i in xrange(len_obj):
        val = hlr_utils.get_value(obj, i, o_descr, "y")
        err2 = hlr_utils.get_err2(obj, i, o_descr, "y")
        x_axis = hlr_utils.get_value(obj, i, o_descr, "x", 0)
        x_err2 = hlr_utils.get_err2(obj, i, o_descr, "x", 0)
        map_so = hlr_utils.get_map_so(obj, None, i)

        bin_center = utils.calc_bin_centers(x_axis, x_err2)

        # Get shift point and extents
        sp = hlr_utils.get_value(shift_point, i, s_descr, "y")
        ie = hlr_utils.get_value(min_ext, i, ie_descr, "y")
        ae = hlr_utils.get_value(max_ext, i, ae_descr, "y")

        # Make shifted spectrum
        value0 = utils.shift_spectrum(val, err2, x_axis, bin_center[0],
                                      sp, ie, ae)

        # Scale spectrum if necessary
        if scale_const is not None:
            value1 = array_manip.mult_ncerr(value0[0], value0[1],
                                            scale_const, 0.0)
        else:
            value1 = value0

        hlr_utils.result_insert(result, res_descr, value1, map_so, "y")

    return result
