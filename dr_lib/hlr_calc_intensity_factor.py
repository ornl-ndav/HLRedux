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

def calc_intensity_factor(obj):
    """
    This function calculates an intensity factor for each pixel. This is
    accomplished by summing all the data in the incoming object and then
    dividing that into the sum of each pixel individually. Each individual
    factor is also multiplied by the total number of pixels present.

    @param obj: Object containing spectra that will have the intensity factor
                calculated from them.
    @type obj: C{SOM.SOM} or C{SOM.SO}

    
    @return: Object containing the intensity factor
    @rtype: C{SOM.SOM} or C{SOM.SO}
    """
    # import the helper functions
    import hlr_utils

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj)

    o_descr = hlr_utils.get_descr(obj)
    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)

    import dr_lib
    
    # Get the total sum for the entire data object
    sum_total = dr_lib.integrate_spectra(obj, total=True, width=True)
    
    # iterate through the values
    len_obj = hlr_utils.get_length(obj)
    for i in xrange(len_obj):
        obj1 = hlr_utils.get_value(obj, i, o_descr, "all")

        pix_sum = dr_lib.integrate_axis(obj1, width=True)

        intensity_factor = (len_obj * pix_sum[0]) / sum_total[0].y
        
        hlr_utils.result_insert(result, res_descr, (intensity_factor, 0.0),
                                obj1, "yonly")
         
    return result

if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som()

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** calc_intensity_factor"
    print "som            :", calc_intensity_factor(som1)
