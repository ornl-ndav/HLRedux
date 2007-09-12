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
    This function takes all the spectra in the given object and sums them
    together. All of the sprectra are assumed to have the same axis scale.
    
    @param obj: Object in which all of the spectra are to be summed together
    @type obj: C{SOM.SOM}
    
    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword rebin_axis: The axis(es) to rebin the spectra onto.
    @type rebin_axis: C{nessi_list.NessiList} or C{list} of
                      C{nessi_list.NessiList}s
                      
    @keyword rebin_axis_dim: Tthe dimension on the spectra being rebinned.
                             The default value is I{1}.
    @type rebin_axis_dim: C{int}
    
    @keyword y_sort: A flag that will sort the spectrum IDs by y. The default
                     behavior is I{False} and this maintains the original x
                     ordering.
    @type y_sort: C{boolean}
    
    @keyword stripe: A flag that will combine spectra in either the x or y
                     direction at a given y or x. The integration direction is
                     based on the setting of y_sort. The default behavior is
                     I{False} and corresponds to summing all spectra into one.
    @type stripe: C{boolean}

    @keyword pix_fix: A single or list of pixel IDs with which to override the
                      summed spectrum pixel ID. The setting of y_sort
                      determines is the x component (y_sort=False) or the y
                      component (y_sort=True) of the pixel ID is overridden.
    @type pix_fix: C{int} or C{list} of C{int}s
    

    @return: Object containing a single spectrum
    @rtype: C{SOM.SOM}
    
    
    @raise TypeError: Anything other than a C{SOM} is given
    
    @raise RuntimeError: An unknown rebinning dimension is given
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

    try:
        y_sort = kwargs["y_sort"]
    except KeyError:
        y_sort = False

    try:
        stripe = kwargs["stripe"]
    except KeyError:
        stripe = False        

    try:
        pix_fix = kwargs["pixel_fix"]
    except KeyError:
        pix_fix = None

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

    # Sort SO IDs by y value
    if y_sort:
        obj1.sort(lambda x, y: cmp(x.id[1][1], y.id[1][1]))
    # SO IDs are already sorted by x value
    else:
        pass

    (result, res_descr) = hlr_utils.empty_result(obj1)

    result = hlr_utils.copy_som_attr(result, res_descr, obj1, o_descr)

    if not stripe:
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
            
        hlr_utils.result_insert(result, res_descr, value, None, "all")
        result.attr_list["Summed IDs"] = so_id_list

        if pix_fix is not None:
            if y_sort:
                fixed_pixel = (so_id_list[0][0], (pix_fix,
                                                  so_id_list[0][1][1]))
            else:
                fixed_pixel = (so_id_list[0][0], (so_id_list[0][1][0],
                                                  pix_fix))
        else:
            fixed_pixel = so_id_list[0]            
            
        result[0].id = fixed_pixel

    else:
        # iterate through the values        
        so_id_list = []
        i_start = 0
        stripe_count = 0
        total_size = hlr_utils.get_length(obj1)
        while i_start < total_size:
            stripe_list = []
            counted = 2
            val1 = hlr_utils.get_value(obj1, i_start, o_descr, "all")
            val2 = hlr_utils.get_value(obj1, i_start+1, o_descr, "all")
            value = common_lib.add_ncerr(val1, val2)
            stripe_list.append(val1.id)
            stripe_list.append(val2.id)

            if y_sort:
                comp_id = val2.id[1][1]
            else:
                comp_id = val2.id[1][0]
            
            for i in xrange(i_start+2, total_size):
                val = hlr_utils.get_value(obj1, i, o_descr, "all")
                if y_sort:
                    new_id = val.id[1][1]
                else:
                    new_id = val.id[1][0]

                if new_id > comp_id:
                    break
                
                value = common_lib.add_ncerr(val, value)
                stripe_list.append(val.id)
                counted += 1

            i_start += counted

            so_id_list.append(stripe_list)
            hlr_utils.result_insert(result, res_descr, value, None, "all")

            if pix_fix is not None:
                try:
                    if y_sort:
                        fixed_pixel = (stripe_list[0][0],
                                       (pix_fix[stripe_count],
                                        stripe_list[0][1][1]))
                    else:
                        fixed_pixel = (stripe_list[0][0],
                                       (stripe_list[0][1][0],
                                        pix_fix[stripe_count]))
                    
                except TypeError:
                    if y_sort:
                        fixed_pixel = (stripe_list[0][0],
                                       (pix_fix,
                                        stripe_list[0][1][1]))
                    else:
                        fixed_pixel = (stripe_list[0][0],
                                       (stripe_list[0][1][0],
                                        pix_fix))
            else:
                fixed_pixel = stripe_list[0]

            result[stripe_count].id = fixed_pixel
            stripe_count += 1

        result.attr_list["summed_ids"] = so_id_list            

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

