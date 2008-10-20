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

def dimensionless_mon(obj, min_ext, max_ext, **kwargs):
    """
    This function takes monitor spectra and converts them to dimensionless
    spectra by dividing each spectrum by the total number of counts within the
    range [min_ext, max_ext]. Then, each spectrum is multiplied by the quantity
    max_ext - min_ext. The units of min_ext and max_ext are assumed to be the
    same as the monitor spectra axis.

    @param obj: Object containing monitor spectra
    @type obj: C{SOM.SOM} or C{SOM.SO}

    @param min_ext: Minimium range and associated error^2 for integrating total
                    counts.
    @type min_ext: C{tuple}

    @param max_ext: Maximium range and associated error^2 for integrating total
                    counts.
    @type max_ext: C{tuple}

    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword units: The expected units for this function. The default for this
                    function is I{Angstroms}.
    @type units: C{string}


    @return: Dimensionless monitor spectra
    @rtype: C{SOM.SOM} or C{SOM.SO}
    """
    
    # import the helper functions
    import hlr_utils

    if obj is None:
        return obj

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj)
    o_descr = hlr_utils.get_descr(obj)

    # Setup keyword arguments
    try:
        units = kwargs["units"]
    except KeyError:
        units = "Angstroms"

    # Primary axis for transformation. If a SO is passed, the function, will
    # assume the axis for transformation is at the 0 position
    if o_descr == "SOM":
        axis = hlr_utils.one_d_units(obj, units)
    else:
        axis = 0

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)

    import array_manip
    import dr_lib
    import utils

    for i in xrange(hlr_utils.get_length(obj)):
        val = hlr_utils.get_value(obj, i, o_descr, "y")
        err2 = hlr_utils.get_err2(obj, i, o_descr, "y")
        x_axis = hlr_utils.get_value(obj, i, o_descr, "x", axis)
        x_err2 = hlr_utils.get_err2(obj, i, o_descr, "x", axis)
        map_so = hlr_utils.get_map_so(obj, None, i)

        bin_widths = utils.calc_bin_widths(x_axis, x_err2)

        # Scale bin contents by bin width
        value0 = array_manip.mult_ncerr(val, err2,
                                        bin_widths[0], bin_widths[1])

        # Find bin range for extents
        min_index = utils.bisect_helper(x_axis, min_ext[0])
        max_index = utils.bisect_helper(x_axis, max_ext[0])

        # Integrate axis using bin width multiplication
        (asum, asum_err2) = dr_lib.integrate_axis_py(map_so, start=min_index,
                                                     end=max_index, width=True)

        # Get the number of bins in the integration range
        num_bins = max_index - min_index + 1

        asum /= num_bins
        asum_err2 /= (num_bins * num_bins)

        # Divide by sum
        value1 = array_manip.div_ncerr(value0[0], value0[1], asum, asum_err2)

        hlr_utils.result_insert(result, res_descr, value1, map_so, "y")

    return result

if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som("histogram", 1, 1)
    som1.setAllAxisUnits(["Angstroms"])

    minimum_extent = (1.5, 0.0)
    maximum_extent = (3.5, 0.0)

    print "********** SOM1"
    print "* ", som1[0]

    print "********** dimensionless_mon"
    print "* som: ", dimensionless_mon(som1, minimum_extent, maximum_extent)
