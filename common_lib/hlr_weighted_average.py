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

def weighted_average(obj, **kwargs):
    """
    This function takes a C{SOM} or C{SO} and calculates the weighted average
    for the primary axis.

    @param obj: Object that will have the weighted average calculated from it
    @type obj: C{SOM.SOM} or C{SOM.SO}

    @param kwargs: A list of keyword arguments that the function accepts:    

    @keyword start: The index of starting bin
    @type start: C{int}

    @keyword end: The index of ending bin
    @type end: C{int}    
    
    
    @return: Object containing the weighted average and the uncertainty
             squared associated with the weighted average
    @rtype: C{tuple} (for a C{SO}) or a C{list} of C{tuple}s (for a C{SOM})


    @raise TypeError: A C{tuple} or another construct (besides a C{SOM} or
                      C{SO}) is passed to the function
    """

    # import the helper functions
    import hlr_utils

    # set up for working through data
    # This time highest object in the hierarchy is NOT what we need
    result = []
    if(hlr_utils.get_length(obj) > 1):
        res_descr = "list"
    else:
        res_descr = "number"

    o_descr = hlr_utils.get_descr(obj)

    if(kwargs.has_key("start")):
        start = int(kwargs["start"])
    else:
        start = 0

    if(kwargs.has_key("end")):
        end = int(kwargs["end"])
    else:
        end = hlr_utils.get_length(obj) - 1
            
    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)

    # iterate through the values
    import utils
    
    for i in xrange(hlr_utils.get_length(obj)):
        val = hlr_utils.get_value(obj, i, o_descr, "y")
        err2 = hlr_utils.get_err2(obj, i, o_descr, "y")

        value = utils.weighted_average(val, err2, start, end)

        hlr_utils.result_insert(result, res_descr, value, None, "all")

    import copy
    return copy.deepcopy(result)


if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som()

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** weighted_average"
    print "* som      :", weighted_average(som1)
    print "* som [0,2]:", weighted_average(som1, start=0, end=2)
    print "* so       :", weighted_average(som1[0])
    print "* so  [1,3]:", weighted_average(som1[0], start=1, end=3)



