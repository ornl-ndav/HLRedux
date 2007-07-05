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

def frequency_to_energy(obj, **kwargs):
    """
    This function converts a primary axis of a C{SOM} or C{SO} from frequency
    to energy. The frequency axis for a C{SOM} must be in units of I{THz}.
    The primary axis of a C{SO} is assumed to be in units of I{THz}. A C{tuple}
    of C{(frequency, frequency_err2)} (assumed to be in units of I{THz}) can be
    converted to C{(energy, energy_err2)}.

    @param obj: Object to be converted
    @type obj: C{SOM.SOM}, C{SOM.SO} or C{tuple}
    
    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword units: The expected units for this function. The default for this
                    function is I{THz}.
    @type units: C{string}


    @return: Object with primary axis in frequency converted to energy
    @rtype: C{SOM.SOM}, C{SOM.SO} or C{tuple}


    @raise TypeError: The incoming object is not a type the function recognizes
    
    @raise RuntimeError: The C{SOM} x-axis units are not I{THz}
    """

    # import the helper functions
    import hlr_utils

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj)
    o_descr = hlr_utils.get_descr(obj)

    # Setup keyword arguments
    try:
        units = kwargs["units"]
    except KeyError:
        units = "THz"

    # Primary axis for transformation. If a SO is passed, the function, will
    # assume the axis for transformation is at the 0 position
    if o_descr == "SOM":
        axis = hlr_utils.one_d_units(obj, units)
    else:
        axis = 0

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)
    if o_descr == "SOM":
        result = hlr_utils.force_units(result, "meV", axis)
        result.setAxisLabel(axis, "energy transfer")
        result.setYUnits("Counts/meV")
        result.setYLabel("Intensity")
    else:
        pass

    # iterate through the values
    import axis_manip
    
    for i in xrange(hlr_utils.get_length(obj)):
        val = hlr_utils.get_value(obj, i, o_descr, "x", axis)
        err2 = hlr_utils.get_err2(obj, i, o_descr, "x", axis)

        value = axis_manip.frequency_to_energy(val, err2)

        map_so = hlr_utils.get_map_so(obj, None, i)
        hlr_utils.result_insert(result, res_descr, value, map_so, "x", axis)

    return result


if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som()
    som1.setAllAxisUnits(["THz"])

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** frequency_to_energy"
    print "* frequency_to_energy som  :", frequency_to_energy(som1)
    print "* frequency_to_energy so   :", frequency_to_energy(som1[0])
    print "* frequency_to_energy scal :", frequency_to_energy([1, 1])



