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

def fix_bin_contents(obj, **kwargs):
    """
    This function takes a SOM or SO and goes through the individual spectra
    adjusting the bin contents by dividing by the bin widths taken from the
    individual spectra.

    @param obj: The data object to be scaled
    @type obj: C{SOM.SOM} or C{SOM.SO}

    @param kwargs: A list of keyword arguments that the function accepts:

    @keyword units: The expected units for this function. The default for this
                    function is I{microsecond}.
    @type units: C{string}


    @return: The object with the individual spectrum scaled
    @rtype: C{SOM.SOM} or C{SOM.SO}
    """
    import hlr_utils

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj)
    o_descr = hlr_utils.get_descr(obj)

    # Setup keyword arguments
    try:
        units = kwargs["units"]
    except KeyError:
        units = "microsecond"

    # Primary axis for transformation. If a SO is passed, the function, will
    # assume the axis for transformation is at the 0 position
    if o_descr == "SOM":
        axis_pos = hlr_utils.one_d_units(obj, units)
    else:
        axis_pos = 0

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)
        
    # iterate through the values
    import array_manip
    import utils

    for i in xrange(hlr_utils.get_length(obj)):
        val = hlr_utils.get_value(obj, i, o_descr, "y")
        err2 = hlr_utils.get_err2(obj, i, o_descr, "y")
        axis = hlr_utils.get_value(obj, i, o_descr, "x", axis_pos)
        axis_err2 = hlr_utils.get_err2(obj, i, o_descr, "x", axis_pos)
        
        map_so = hlr_utils.get_map_so(obj, None, i)

        (bin_width, bin_width_err2) = utils.calc_bin_widths(axis, axis_err2)

        value = array_manip.div_ncerr(val, err2, bin_width, bin_width_err2)

        hlr_utils.result_insert(result, res_descr, value, map_so, "y")

    return result

if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som("histogram", 1, 1)
    som1.setAllAxisUnits(["microsecond"])

    print "********** SOM1"
    print "* ", som1[0]

    print "********** fix_bin_contents"
    print "* som: ", fix_bin_contents(som1)

    
