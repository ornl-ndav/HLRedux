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

def subtract_axis_dep_bkg(obj, coeffs):
    """
    This function takes spectrum object(s) and a set of coefficients and
    subtracts an axis dependent background based on a polynomial. The order
    of the polynomial is based on the number of coefficients provided.

    @param obj: Object from which to subtract the individual background numbers
    @type obj: C{SOM.SOM} or C{SOM.SO}

    @param coeffs: The set of coefficients for the polynomial representation
                   of the background to be subtracted.
    @type coeffs: C{list} of C{floats}


    @return: Object with the axis dependent background subtracted
    @rtype: C{SOM.SOM} or C{SOM.SO}


    @raise TypeError: The first argument is not a C{SOM} or C{SO}    
    """
    # Kickout is coeffs is None, or length is zero
    if coeffs is None:
        return obj

    poly_len = len(coeffs)    
    if poly_len == 0:
        return obj

    # Reverse coefficients for __eval_poly function
    coeffs.reverse()

    # import the helper functions
    import hlr_utils

    o_descr = hlr_utils.get_descr(obj)

    if o_descr != "SOM" and o_descr != "SO":
        raise TypeError("Incoming object must be a SOM or a SO")
    # Have a SOM or SO
    else:
        pass

    (result, res_descr) = hlr_utils.empty_result(obj)

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)

    obj_len = hlr_utils.get_length(obj)

    import array_manip
    import utils
    
    # iterate through the values
    for i in xrange(obj_len):
        axis   = hlr_utils.get_value(obj, i, o_descr, "x", 0)
        val    = hlr_utils.get_value(obj, i, o_descr, "y")
        err2   = hlr_utils.get_err2 (obj, i, o_descr, "y")
        map_so = hlr_utils.get_map_so(obj, None, i)

        axis_centers = utils.calc_bin_centers(axis)

        for j in xrange(len(val)):
            val[j] -= __eval_poly(axis_centers[0][j], coeffs, poly_len)

        value = (val, err2)

        hlr_utils.result_insert(result, res_descr, value, map_so, "y")

    return result

def __eval_poly(x, coeffs, poly_length):
    """
    This function evaluates the polynomial from the given coefficients and x
    value.

    @param x: The value to evaluate the polynomial from
    @type x: C{float}

    @param coeffs: The polynomial coefficients
    @type coeffs: C{list}

    @param poly_length: The order of the polynomial
    @type poly_length: C{int}


    @return: The evaluation of the polynomial
    @rtype: C{float}
    """
    value = float(coeffs[0])
    for i in xrange(1, poly_length):
        value = float(coeffs[i]) + value * x

    return value

if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som()

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** subtract_axis_dep_bkg"
    print "* som - scal :", subtract_axis_dep_bkg(som1, [-0.5, 1.0])
