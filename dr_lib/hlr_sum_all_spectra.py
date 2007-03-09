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

import hlr_utils

def sum_all_spectra(obj, **kwargs):
    """
    This function takes all the SOs in a SOM and sums them together using the
    summing by weights concept. All of the SOs are assumed to have the same
    axis scale.
    
    Parameters:
    ----------
    -> obj is a SOM in which all of the SOs are to be summed together
    -> kwargs is a list of keyword arguments that the function accepts
       rebin_axis=<object> is a NessiList or a list of NessiLists containing
                           the axes to rebin the spectra onto.
       rebin_axis_dim=<int> is the dimension on the spectra being rebinned.
                            The default value is 1.

    Returns:
    -------
    <- A SOM containing a single spectrum

    Exceptions:
    ----------
    <- TypeError is raised if anything other than a SOM is given
    <- RuntimeError is raised if an unknown rebinning dimension is given
    """

    o_descr = hlr_utils.get_descr(obj)

    if o_descr != "SOM":
        raise TypeError("Function argument must be a SOM")
    # Have a SOM, go on
    else:
        pass

    # If there is only one SO, why run
    if len(obj) == 1:
        return obj
    # OK, we need to sum 
    else:
        pass

    try:
        rebin_axis = kwargs["rebin_axis"]
    except KeyError:
        rebin_axis = None

    try:
        rebin_axis_dim = kwargs["rebin_axis_dim"]
    except KeyError:
        rebin_axis_dim = 1

    import common_lib

    if rebin_axis is not None:
        if rebin_axis_dim == 1:
            obj1 = common_lib.rebin_axis_1D(obj, rebin_axis)
        elif rebin_axis_dim == 2:
            obj1 = common_lib.rebin_axis_2D(obj, rebin_axis[0], rebin_axis[1])
        else:
            raise RuntimeError("Do not have rebinning method for %dD." % \
                               rebin_axis_dim)
    else:
        obj1 = obj

    del obj

    (result, res_descr) = hlr_utils.empty_result(obj1)

    result = hlr_utils.copy_som_attr(result, res_descr, obj1, o_descr)

    # iterate through the values
    so_id_list = []

    val1 = hlr_utils.get_value(obj1, 0, o_descr, "all")
    val2 = hlr_utils.get_value(obj1, 1, o_descr, "all")
    value = common_lib.add_ncerr(val1, val2)
    so_id_list.append(val1.id)
    so_id_list.append(val2.id)

    for i in xrange(2, hlr_utils.get_length(obj1)):
        val = hlr_utils.get_value(obj1, i, o_descr, "all")
        value = common_lib.add_ncerr(val, value)
        so_id_list.append(val.id)

    hlr_utils.result_insert( result, res_descr, value, None, "all")
    result.attr_list["Summed IDs"] = so_id_list
    result[0].id = so_id_list[0]
            
    return result

if __name__ == "__main__":
    import hlr_test
    import SOM
    
    som1 = SOM.SOM()
    so1 = hlr_test.generate_so("histogram", 0, 5, 1, 1)
    so1.id = 1
    som1.append(so1)
    so2 = hlr_test.generate_so("histogram", 0, 5, 1, 3)
    so2.id = 2
    som1.append(so2)
    so3 = hlr_test.generate_so("histogram", 0, 5, 1, 2)
    so3.id = 3
    som1.append(so3)

    axis_new = hlr_utils.make_axis(0, 5, 2.5)

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]
    print "* ", som1[2]

    print "********** sum_all_spectra"
    print "* som:", sum_all_spectra(som1)
    print "* som (rebin):", sum_all_spectra(som1, rebin_axis=axis_new)

