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

def integrate_spectra(obj, **kwargs):
    """
    This function takes a set of spectra and calculates the integration for the
    primary axis. If the integration range for a spectrum cannot be found, an
    error report will be generated with the following information:

    Range not found: pixel ID, start bin, end bin, length of data array
       
    A failing pixel will have the integration tuple set to C{(nan, nan)}.

    @param obj: Object containing spectra that will have the integration
                calculated from them.
    @type obj: C{SOM.SOM} or C{SOM.SO}
    
    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword start: The start range for the integration.
    @type start: C{int}
    
    @keyword end: The end range for the integration. 
                  function.
    @type end: C{int}
    
    @keyword axis_pos: This is position of the axis in the axis array. If no
                       argument is given, the default value is I{0}.
    @type axis_pos: C{int}

    @keyword norm: This is a flag to turn on the division of the individual
                   spectrum integrations by the solid angle of the
                   corresponding pixel. This also activates the multiplication
                   of the individual spectrum bin values by their
                   corresponding bin width via the I{width} flag in
                   L{integrate_axis}. The default value of the flag is
                   I{False}.
    @type norm: C{boolean}

    @keyword total: This is a flag to turn on the summation of all individual
                    spectrum integrations. The default value of the flag is
                    I{False}.
    @type total: C{boolean}

    @keyword width: This is a flag to turn on the removal of the individual bin
                    width in the L{integrate_axis} function while doing the
                    integrations. The default value of the flag is I{False}. 
    @type width: C{boolean}
    
    
    @return: Object containing the integration and the uncertainty squared
             associated with the integration
    @rtype: C{SOM.SOM} or C{SOM.SO}
    """

    # import the helper functions
    import hlr_utils

    if obj is None:
        return obj

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj)

    o_descr = hlr_utils.get_descr(obj)
    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)

    # Check for axis_pos keyword argument
    try:
        axis_pos = kwargs["axis_pos"]
    except KeyError:
        axis_pos = 0

    # Check for norm keyword argument
    try:
        norm = kwargs["norm"]
        if norm:
            if o_descr == "SO":
                raise RuntimeError("Cannot use norm keyword with SO!")
            
            width = True
            inst = obj.attr_list.instrument
        else:
            width = False
    except KeyError:
        norm = False
        width = False

    # Check for total keyword argument
    try:
        total = kwargs["total"]
    except KeyError:
        total = False

    # Check for width keyword argument only if norm isn't present
    if not norm:
        try:
            width = kwargs["width"]
        except KeyError:
            width = False

    # If the integration start bound is not given, set to infinity
    try:
        i_start = kwargs["start"]
    except KeyError:
        i_start = float("inf")

    # If the integration end bound is not given, set to infinity
    try:
        i_end = kwargs["end"]
    except KeyError:
        i_end = float("inf")
    
    # iterate through the values
    import dr_lib

    len_obj = hlr_utils.get_length(obj)
    for i in xrange(len_obj):
        obj1 = hlr_utils.get_value(obj, i, o_descr, "all")

        # If there's a NaN at the front and back, there are NaN's everywhere
        if str(obj1.axis[axis_pos].val[0]) == "nan" and \
               str(obj1.axis[axis_pos].val[-1]) == "nan":
            print "Range not found:", obj1.id, i_start, i_end, len(obj1)
            value = (float('nan'), float('nan'))
        else:
            value = dr_lib.integrate_axis(obj1, start=i_start, end=i_end,
                                          width=width)
        if norm:
            if inst.get_name() == "BSS":
                map_so = hlr_utils.get_map_so(obj, None, i)
                dOmega = dr_lib.calc_BSS_solid_angle(map_so, inst)
        
                value1 = (value[0] / dOmega, value[1] / (dOmega * dOmega))
            else:
                raise RuntimeError("Do not know how to get solid angle from "\
                                   +"%s" % inst.get_name())
        else:
            value1 = value

        hlr_utils.result_insert(result, res_descr, value1, obj1, "yonly")

    if not total:
        return result
    else:
        # Sum all integration counts
        total_counts = 0
        total_err2 = 0

        for j in xrange(hlr_utils.get_length(result)):
            total_counts += hlr_utils.get_value(result, j, res_descr, "y")
            total_err2 += hlr_utils.get_err2(result, j, res_descr, "y")

        # Create new result object
        (result2, res2_descr) = hlr_utils.empty_result(result)

        result2 = hlr_utils.copy_som_attr(result2, res2_descr,
                                          result, res_descr)

        res1 = hlr_utils.get_value(result, 0, res_descr, "all")
        hlr_utils.result_insert(result2, res2_descr,
                                (total_counts, total_err2),
                                res1, "yonly")
        return result2

if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som()

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** integrate_spectra"
    print "som            :", integrate_spectra(som1)
    print "som (1.5, 3.5) :", integrate_spectra(som1, start=1.5, end=3.5)
    print "som (0.5, 2.75):", integrate_spectra(som1, start=0.5, end=2.75)
    print "som (total)    :", integrate_spectra(som1, total=True)
