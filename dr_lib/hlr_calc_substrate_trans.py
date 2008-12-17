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

def calc_substrate_trans(obj, subtrans_coeff, substrate_thick):
    """
    This function calculates substrate transmission via the following formula:
    T = exp[-(A + B * wavelength) * t] where A is a constant with units of
    cm^-1, B is a constant with units of cm^-2 and t is the substrate
    thickness in units of cm.

    @param obj: The data object that contains the TOF axes to calculate the
                transmission from.
    @type obj: C{SOM.SOM}

    @param subtrans_coeff: The two coefficients for substrate transmission
           calculation.
    @type subtrans_coeff: C{tuple} of two C{float}s

    @param substrate_thick: The thickness of the substrate.
    @type substrate_thick: C{float}
    """
    # import the helper functions
    import hlr_utils

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj)
    o_descr = hlr_utils.get_descr(obj)
    
    if o_descr == "SOM":
        try:
            obj.attr_list.instrument.get_primary()
            inst = obj.attr_list.instrument
        except RuntimeError:
            raise RuntimeError("A detector was not provided")

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)
    if res_descr == "SOM":
        result.setYLabel("Transmission")
        
    # iterate through the values
    import array_manip
    import axis_manip
    import nessi_list
    import utils

    import math
    
    len_obj = hlr_utils.get_length(obj)
    for i in xrange(len_obj):
        val = hlr_utils.get_value(obj, i, o_descr, "x", axis)
        err2 = hlr_utils.get_err2(obj, i, o_descr, "x", axis)
        
        map_so = hlr_utils.get_map_so(obj, None, i)

        (pl, pl_err2) = hlr_utils.get_parameter("pathlength", map_so, inst)

        value = axis_manip.tof_to_wavelength(val, err2, pl, pl_err2)

        value1 = utils.calc_bin_centers(value[0])
        del value

        # Convert Angstroms to centimeters
        value2 = array_manip.mult_ncerr(value1[0], value1[1],
                                        subtrans_coeff[1]*1.0e-8, 0.0)
        del value1

        # Calculate the exponential
        value3 = array_manip.add_ncerr(value2[0], value2[1],
                                       subtrans_coeff[0], 0.0)
        del value2

        value4 = array_manip.mult_ncerr(value3[0], value3[1],
                                        -1.0*substrate_thick, 0.0)
        del value3

        # Calculate transmission
        trans = nessi_list.NessiList()
        len_trans = len(value4[0])
        for j in xrange(len_trans):
            trans.append(math.exp(value4[0][j]))

        trans_err2 = nessi_list.NessiList(len(trans))

        hlr_utils.result_insert(result, res_descr, (trans, trans_err2), map_so)

    return result
