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

def rebin_axis_1D_frac(obj, axis_out):
    """
    This function rebins the primary axis for a C{SOM} or a C{SO} based on the
    given C{NessiList} axis.

    @param obj: Object to be rebinned
    @type obj: C{SOM.SOM} or C{SOM.SO}
    
    @param axis_out: The axis to rebin the C{SOM} or C{SO} to
    @type axis_out: C{NessiList}


    @return: Object that has been rebinned according to the provided axis
    @rtype: C{SOM.SOM} or C{SOM.SO}


    @raise TypeError: The rebinning axis given is not a C{NessiList}
    
    @raise TypeError: The object being rebinned is not a C{SOM} or a C{SO}
    """
    # import the helper functions
    import hlr_utils

    # set up for working through data
    try:
        axis_out.__type__
    except AttributeError:
        raise TypeError("Rebinning axis must be a NessiList!")
        
    o_descr = hlr_utils.get_descr(obj)

    if o_descr == "number" or o_descr == "list":
        raise TypeError("Do not know how to handle given type: %s" % \
                        o_descr)
    else:
        pass
    
    (result, res_descr) = hlr_utils.empty_result(obj)

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)

    # iterate through the values
    import array_manip
    import axis_manip
    import nessi_list
    
    for i in xrange(hlr_utils.get_length(obj)):
        axis_in = hlr_utils.get_value(obj, i, o_descr, "x", 0)
        val = hlr_utils.get_value(obj, i, o_descr)
        err2 = hlr_utils.get_err2(obj, i, o_descr)

        value = axis_manip.rebin_axis_1D_frac(axis_in, val, err2, axis_out)

        frac_err = nessi_list.NessiList(len(value[2]))

        value1 = array_manip.div_ncerr(value[0], value[1], value[2], frac_err)
        
        xvals = []
        xvals.append(axis_out)

        map_so = hlr_utils.get_map_so(obj, None, i)

        #print "A:", map_so.id
        #print "B:", value[0].toNumPy()
        #print "C:", value[2].toNumPy()
        #print "D:", value1[0].toNumPy()
        
        hlr_utils.result_insert(result, res_descr, value1, map_so, "all",
                                0, xvals)

    return result


if __name__ == "__main__":
    import hlr_test
    import nessi_list

    som1 = hlr_test.generate_som()

    axis = nessi_list.NessiList()
    axis.extend(0, 2.5, 5)

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** rebin_axis_1D_frac"
    print "* rebin som:", rebin_axis_1D_frac(som1, axis)
    print "* rebin so :", rebin_axis_1D_frac(som1[0], axis)
