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

def feff_correct_mon(obj, **kwargs):
    """
    This function takes in a monitor SOM, calculates efficiencies based on
    the montior's wavelength axis and divides the monitor counts by the
    calculated efficiencies. The function is a constant * wavelength.

    Parameters:
    ----------
    -> obj is a SOM or SO containing monitor spectra
    -> kwargs is a list of key word arguments that the function accepts:
           units= a string containing the expected units for this function.
                  The default for this function is Angstroms
                  
    Returns:
    -------
    <- Efficiency corrected monitor SOM or SO
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
        units = "Angstroms"

    # Primary axis for transformation. If a SO is passed, the function, will
    # assume the axis for transformation is at the 0 position
    if o_descr == "SOM":
        axis = hlr_utils.hlr_1D_units(obj, units)
    else:
        axis = 0

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)

    # iterate through the values
    import array_manip
    import nessi_list
    
    constant = 0.00000085 / 1.8 # A^-1
    
    for i in xrange(hlr_utils.get_length(obj)):
        val = hlr_utils.get_value(obj, i, o_descr, "x")
        map_so = hlr_utils.get_map_so(obj, None, i)

        eff = nessi_list.NessiList()

        for j in xrange(len(val)-1):
            bin_center = (val[j+1] + val[j]) / 2.0
            eff.append(constant * bin_center)

        eff_err2 = nessi_list.NessiList(len(eff))

        y_val = hlr_utils.get_value(obj, i, o_descr, "y")
        y_err2 = hlr_utils.get_value(obj, i, o_descr, "y")

        value = array_manip.div_ncerr(y_val, y_err2, eff, eff_err2);

        hlr_utils.result_insert(result, res_descr, value, map_so, "y")

    return result

if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som("histogram", 1, 1)
    som1.setAllAxisUnits(["Angstroms"])

    print "********** SOM1"
    print "* ", som1[0]

    print "********** feff_correct_mon"
    print "* som: ", feff_correct_mon(som1)
