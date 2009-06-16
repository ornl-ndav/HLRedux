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

def determine_time_indep_bkg(obj, tof_vals, **kwargs):
    """
    This functions calculates the average counts at four given TOF channels
    for determining the time-independent background. 

    @param obj: Object used for determining the time-independent background
    @type obj: C{SOM.SOM} or C{SOM.SO}
    
    @param tof_vals: The four TOF channels from which the average counts will
                     be determined
    @type tof_vals: C{list}

    @param kwargs: A list of keyword arguments that the function accepts:

    @keyword is_range: A flag that tells the function that tof_vals is a range
                       from which to determine the time-independent
                       background. The default is I{False}.
    @type is_range: C{bool}

       
    @return: Object containing the time-independent background and the
             associated error
    @rtype: C{list} of C{tuple}s
    

    @raise TypeError: The incoming object is not a C{SOM} or C{SO}.
    """

    # Kickout if tof_vals is NoneType
    if tof_vals is None:
        return None

    # import the helper functions
    import hlr_utils

    # Get keyword arguments
    is_range = kwargs.get("is_range", False)

    o_descr = hlr_utils.get_descr(obj)

    if o_descr != "SOM" and o_descr != "SO":
        raise TypeError("Incoming object must be a SOM or a SO")
    # Have a SOM or SO
    else:
        pass
    
    # set up for working through data
    # This time highest object in the hierarchy is NOT what we need
    result = []
    if(hlr_utils.get_length(obj) > 1):
        res_descr = "list"
    else:
        res_descr = "number"

    if not is_range:
        num_tof_vals = float(len(tof_vals))
        import bisect
    else:
        num_tof_vals = tof_vals[1] - tof_vals[0]
        import dr_lib

    # iterate through the values
    len_obj = hlr_utils.get_length(obj)
    for i in xrange(len_obj):
        obj1 = hlr_utils.get_value(obj, i, o_descr, "all")

        if not is_range:
            average = 0.0
            ave_err2 = 0.0
            for tof in tof_vals:
                index = bisect.bisect(obj1.axis[0].val, float(tof)) - 1
                average += obj1.y[index]
                ave_err2 += obj1.var_y[index]
        else:
            (average, ave_err2) = dr_lib.integrate_axis(obj1, width=True,
                                                        start=tof_vals[0],
                                                        end=tof_vals[1])
            
        average /= num_tof_vals
        ave_err2 /= num_tof_vals

        hlr_utils.result_insert(result, res_descr, (average, ave_err2), None,
                                "all")

    import copy
    return copy.deepcopy(result)

if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som()

    tof_channels = [1.5, 3.0]
 
    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** determine_time_indep_bkg"
    print "* ", determine_time_indep_bkg(som1, tof_channels)
    print "* ", determine_time_indep_bkg(som1, tof_channels, is_range=True)
    
