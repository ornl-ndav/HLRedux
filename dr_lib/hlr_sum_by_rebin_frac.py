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

import nessi_list
    
def sum_by_rebin_frac(obj, axis_out, **kwargs):
    """
    This function uses the C{axis_manip.rebin_axis_1D_frac} function from the
    SCL to perform the rebinning. The function tracks the counts and fractional
    area from all spectra separately. The counts and fractional area are
    divided after all spectra have been parsed. 
    
    @param obj: Object to be rebinned and summed
    @type obj: C{SOM.SOM} or C{SOM.SO}
    
    @param axis_out: The axis to rebin the C{SOM} or C{SO} to
    @type axis_out: C{NessiList}

    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword configure: This is the object containing the driver configuration.
                        This will signal the function to write out the counts
                        and fractional area to files.
    @type configure: C{Configure}


    @return: Object that has been rebinned and summed according to the
             provided axis
    @rtype: C{SOM.SOM} or C{SOM.SO}


    @raise TypeError: The rebinning axis given is not a C{NessiList}
    @raise TypeError: The object being rebinned is not a C{SOM} or a C{SO}
    @raise TypeError: The dimension of the input object is not 1D
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

    try:
        if obj.getDimension() != 1:
            raise TypeError("The input object must be 1D!. This one is "\
                            +"%dD." % obj.getDimension())
    except AttributeError:
        # obj is a SO
        if obj.dim() != 1:
            raise TypeError("The input object must be 1D!. This one is "\
                            +"%dD." % obj.dim())

    # Check for keywords
    try:
        config = kwargs["configure"]
    except KeyError:
        config = None

    (result, res_descr) = hlr_utils.empty_result(obj)

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)

    import array_manip
    import axis_manip

    len_data = len(axis_out) - 1

    counts = nessi_list.NessiList(len_data)
    counts_err2 = nessi_list.NessiList(len_data)
    frac_area = nessi_list.NessiList(len_data)
    frac_area_err2 = nessi_list.NessiList(len_data)

    for i in xrange(hlr_utils.get_length(obj)):
        axis_in = hlr_utils.get_value(obj, i, o_descr, "x", 0)
        val = hlr_utils.get_value(obj, i, o_descr)
        err2 = hlr_utils.get_err2(obj, i, o_descr)
        
        value = axis_manip.rebin_axis_1D_frac(axis_in, val, err2, axis_out)

        (counts, counts_err2) = array_manip.add_ncerr(counts, counts_err2,
                                                      value[0], value[1])
        
        (frac_area, frac_area_err2) = array_manip.add_ncerr(frac_area,
                                                            frac_area_err2,
                                                            value[2],
                                                            frac_area_err2)

    # Divide the total counts by the total fractional area
    value1 = array_manip.div_ncerr(counts, counts_err2, frac_area,
                                   frac_area_err2)
    xvals = []
    xvals.append(axis_out)
    
    map_so = hlr_utils.get_map_so(obj, None, 0)
        
    hlr_utils.result_insert(result, res_descr, value1, map_so, "all",
                            0, xvals)

    if config is not None:
        if o_descr == "SOM":
            import SOM
            o_som = SOM.SOM()
            o_som.copyAttributes(obj)

            so = hlr_utils.get_map_so(obj, None, 0)
            so.axis[0].val = axis_out
            so.y = counts
            so.var_y = counts_err2
            o_som.append(so)

            # Write out summed counts into file
            hlr_utils.write_file(config.output, "text/Spec", o_som,
                                 output_ext="cnt",
                                 verbose=config.verbose,
                                 data_ext=config.ext_replacement,         
                                 path_replacement=config.path_replacement,
                                 message="summed counts")
            
            # Replace counts data with fractional area. The axes remain the
            # same
            o_som[0].y = frac_area
            o_som[0].var_y = frac_area_err2
            
            # Write out summed fractional area into file
            hlr_utils.write_file(config.output, "text/Spec", o_som,
                                 output_ext="fra",
                                 verbose=config.verbose,
                                 data_ext=config.ext_replacement,         
                                 path_replacement=config.path_replacement,
                                 message="fractional area")

    return result

if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som()

    axis = nessi_list.NessiList()
    axis.extend(0, 2.5, 5)

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** sum_by_rebin_frac"
    print "* rebin som:", sum_by_rebin_frac(som1, axis)
    print "* rebin so :", sum_by_rebin_frac(som1[0], axis)
