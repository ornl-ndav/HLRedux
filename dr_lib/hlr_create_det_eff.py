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

def create_det_eff(obj):
    """
    This function creates detector efficiency spectra based on the wavelength
    spectra from the given object. The efficiency spectra are created based on
    the following formalism: Ci*exp(-di*lambda) where i represents the
    constants for a given detector pixel.

    @param obj: Object containing spectra that will create the detector
                efficiency spectra.
    @type obj: C{SOM.SOM} or C{SOM.SO}


    @return: Object containing the detector efficiency spectra
    @rtype: C{SOM.SOM} or C{SOM.SO}


    @raise TypeError: Incoming object is not a C{SOM} or a C{SO}
    @raise RuntimeError: The C{SOM} x-axis units are not I{Angstroms}
    """
    # import the helper functions
    import hlr_utils

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj)
    o_descr = hlr_utils.get_descr(obj)

    if o_descr != "SOM" and o_descr != "SO":
        raise TypeError("Only SOM or SO objects permitted to create "\
                        +"efficiency spectra!")

    # Check units on SOM, SO is assumed to be correct
    if o_descr == "SOM":
        if not obj.hasAxisUnits("Angstroms"):
            raise RuntimeError("Incoming object must has a wavelength axis "\
                               +"with units of Angstroms!")

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)

    # iterate through the values
    import phys_corr
    import utils

    # Get object length
    len_obj = hlr_utils.get_length(obj)
    for i in xrange(len_obj):
        map_so = hlr_utils.get_map_so(obj, None, i)
        axis = hlr_utils.get_value(obj, i, o_descr, "x", 0)

        axis_bc = utils.calc_bin_centers(axis)

        (eff, eff_err2) = phys_corr.exp_detector_eff(axis_bc[0], 1.0, 0.0, 1.0)
        
        hlr_utils.result_insert(result, res_descr, (eff, eff_err2), map_so)
    
    return result

if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som("histogram", 1, 1)
    som1.setAllAxisUnits(["Angstroms"])

    print "********** SOM1"
    print "* ", som1[0]

    print "********** create_det_eff"
    print "* som: ", create_det_eff(som1)
