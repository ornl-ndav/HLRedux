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
    
    @keyword start: Index of the starting bin
    @type start: C{int}
    
    @keyword end: Index of the ending bin. This index is made inclusive by the
                  function.
    @type end: C{int}
    
    @keyword axis_pos: This is position of the axis in the axis array. If no
    argument is given, the default value is I{0}.
    @type axis_pos: C{int}

    @keyword bin_index: This is a flag to say that the values in the start and
    end keyword arguments are either bin indicies (I{True}) or bounds
    (I{False}). The default value is I{False}.
    @type bin_index: C{boolean}

    @keyword norm: This is a flag to turn on the division of the individual
                   spectrum integrations by the sum of the integrations from
                   all spectra. This also activates the multiplication of the
                   individual spectrum bin values by their corresponding bin
                   width via the I{width} flag in L{integrate_axis}. The
                   default value of the flag is I{False}.
    @type norm: C{boolean}
    
    
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

    # Create temporary object to access axis
    if o_descr == "SOM":
        aobj = obj[0]
    elif o_descr == "SO":
        aobj = obj

    # Check for axis_pos keyword argument
    try:
        axis_pos = kwargs["axis_pos"]
    except KeyError:
        axis_pos = 0

    # Check for bin_index keyword argument
    try:
        bin_index = kwargs["bin_index"]
    except KeyError:
        bin_index = False

    # Check for norm keyword argument
    try:
        norm = kwargs["norm"]
        if norm:
            if o_descr == "SO":
                raise RuntimeError("Cannot use norm keyword with SO!")
            
            width = True
            num_pixels = len(obj)
            inst = obj.attr_list.instrument
        else:
            width = False
    except KeyError:
        norm = False
        width = False

    # If the integration start bound is not given, assume the 1st bin
    try:
        i_start = kwargs["start"]
    except KeyError:
        if bin_index:
            i_start = 0
        else:
            i_start = aobj.axis[axis_pos].val[0]

    # If the integration end bound is not given, assume the last bin
    try:
        i_end = kwargs["end"]
    except KeyError:
        if bin_index:
            i_end = -1
        else:
            i_end = aobj.axis[axis_pos].val[-1]
    
    # iterate through the values
    import bisect

    import dr_lib

    for i in xrange(hlr_utils.get_length(obj)):
        obj1 = hlr_utils.get_value(obj, i, o_descr, "all")

        # Find the bin in the y values corresponding to the start bound
        if not bin_index:
            b_start = bisect.bisect(obj1.axis[axis_pos].val, i_start) - 1
        else:
            b_start = i_start

        # Find the bin in the y values corresponding to the end bound
        if not bin_index:
            b_end = bisect.bisect(obj1.axis[axis_pos].val, i_end) - 1
        else:
            b_end = i_end

        try:
            value = dr_lib.integrate_axis(obj1, start=b_start, end=b_end,
                                          width=width)
        except IndexError:
            print "Range not found:", obj1.id, b_start, b_end, len(obj1)
            value = (float('nan'), float('nan'))

        if norm:
            if inst.get_name() == "BSS":
                map_so = hlr_utils.get_map_so(obj, None, i)
                dOmega = dr_lib.calc_BSS_solid_angle(map_so, inst)
        
                value1 = (value[0] / dOmega, value[1] / (dOmega * dOmega))
        else:
            value1 = value

        hlr_utils.result_insert(result, res_descr, value1, obj1, "yonly")

    if not norm:
        return result
    else:
        # Sum all integration counts
        total_counts = 0
        total_err2 = 0

        for j in xrange(hlr_utils.get_length(result)):
            total_counts += hlr_utils.get_value(result, j, res_descr, "y")
            total_err2 += hlr_utils.get_err2(result, j, res_descr, "y")

        total_counts /= num_pixels
        total_err2 /= (num_pixels * num_pixels)

        # Create new result object
        (result2, res2_descr) = hlr_utils.empty_result(result)

        result2 = hlr_utils.copy_som_attr(result2, res2_descr,
                                          result, res_descr)

        # Normalize integration counts
        for k in xrange(hlr_utils.get_length(result)):
            res1 = hlr_utils.get_value(result, k, res_descr, "all")
            
            counts =  hlr_utils.get_value(result, k, res_descr, "y")
            counts_err2 =  hlr_utils.get_err2(result, k, res_descr, "y")

            norm_counts = counts / total_counts
            total_counts2 = total_counts * total_counts
            norm_counts_err2 = ((norm_counts * total_err2) / total_counts)
            norm_counts_err2 += counts_err2
            norm_counts_err2 /= total_counts2

            hlr_utils.result_insert(result2, res2_descr,
                                    (norm_counts, norm_counts_err2),
                                    res1, "yonly")

        del result

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
    print "som (norm)     :", integrate_spectra(som1, norm=True)
