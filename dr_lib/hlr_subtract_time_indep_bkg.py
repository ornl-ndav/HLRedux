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

def subtract_time_indep_bkg(obj, B_list):
    """
    This function takes spectrum object(s) and time-independent background
    value(s) and subtracts the numbers from the appropriate spectrum. The
    time-independent background number(s) are assumed to be in the same order
    as the spectrum object(s).

    @param obj: Object from which to subtract the individual background numbers
    @type obj: C{SOM.SOM} or C{SOM.SO}
    
    @param B_list: The time-independent backgrounds to subtract from the
    individual spectra.
    @type B_list: C{list} of C{tuple}s or C{tuple}

    
    @return: Object with the time-independent backgrounds subtracted
    @rtype: C{SOM.SOM} or C{SOM.SO}
    

    @raise IndexError: The B_list object is empty
    
    @raise TypeError: The first argument is not a C{SOM} or C{SO}
    
    @raise RuntimeError: The C{SOM} and list are not the same length
    """

    if len(B_list) <= 0:
        raise IndexError("List of time-independent background cannot be empty")
    # List is correct size, go on
    else:
        pass

    # import the helper functions
    import hlr_utils

    (o_descr, l_descr) = hlr_utils.get_descr(obj, B_list)

    if o_descr == "number" or o_descr == "list":
        raise TypeError("First argument must be a SOM or a SO!")
    # Have a SOM or SO, go on
    else:
        pass

    (result, res_descr) = hlr_utils.empty_result(obj)

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)

    import common_lib

    # iterate through the values
    for i in xrange(hlr_utils.get_length(obj)):
        val1 = hlr_utils.get_value(obj, i, o_descr, "all")
        val2 = hlr_utils.get_value(B_list, i, l_descr, "all")
        value = common_lib.sub_ncerr(val1, val2)

        hlr_utils.result_insert(result, res_descr, value, None, "all")

    return result

if __name__ == "__main__":
    import hlr_test
    
    som1 = hlr_test.generate_som()
        
    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** subtract_time_indep_bkg"
    print "* som -scal   :", subtract_time_indep_bkg(som1, (3, 1))
    print "* som -l(scal):", subtract_time_indep_bkg(som1, [(1, 1), (2, 1)])
    print "* so  -scal   :", subtract_time_indep_bkg(som1[0], (1, 1))


