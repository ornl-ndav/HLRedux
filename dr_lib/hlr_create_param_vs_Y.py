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

def create_param_vs_Y(som, param, param_func, param_axis, **kwargs):
    """
    This function takes a group of single spectrum with any given axes
    (wavelength, energy etc.). The function can optionally rebin those axes to
    a given axis. It then creates a 2D spectrum by using a parameter,
    parameter functiona and a given axis for the lookup locations and places
    each original spectrum in the found location.
    
    @param som: The input object with arbitrary (but same) axis spectra
    @type som: C{SOM.SOM}

    @param param: The parameter that will be used for creating the lookups.
    @type param: C{string}

    @param param_func: The function that will convert the parameter into the
                       values for lookups.
    @type param_func: C{string}

    @param param_axis: The axis that will be searched for the lookup values.
    @type param_axis: C{nessi_list.NessiList}

    @param kwargs: A list of keyword arguments that the function accepts:

    @keyword rebin_axis: An axis to rebin the given spectra to.
    @type rebin_axis: C{nessi_list.NessiList}

    @keyword data_type: The name of the data type which can be either
                        I{histogram}, I{density} or I{coordinate}. The default
                        value will be I{histogram}.
    @type data_type: C{string}

    @keyword pixnorm: A flag to track the number of pixels that contribute to
                      a bin and then normalize the bin by that number.
    @type pixnorm: C{boolean}

    @keyword so_id: The identifier represents a number, string, tuple or other
                    object that describes the resulting C{SO}.
    @type so_id: C{int}, C{string}, C{tuple}, C{pixel ID}
    
    @keyword y_label: The dependent axis label
    @type y_label: C{string}
    
    @keyword y_units: The dependent axis units
    @type y_units: C{string}
    
    @keyword x_labels: The two independent axis labels
    @type x_labels: C{list} of C{string}s
    
    @keyword x_units: The two independent axis units
    @type x_units: C{list} of C{string}s


    @return: A two dimensional spectrum with the parameter as the x-axis and
             the given spectra axes as the y-axis.
    @rtype: C{SOM.SOM}
    """
    import array_manip
    import common_lib
    import hlr_utils
    import nessi_list
    import SOM
    import utils

    # Check for rebinning axis
    try:
        rebin_axis = kwargs["rebin_axis"]
    except KeyError:
        rebin_axis = None

    # Check for pixnorm flag
    try:
        pixnorm = kwargs["pixnorm"]
    except KeyError:
        pixnorm = False

    # Check dataType keyword argument. An offset will be set to 1 for the
    # histogram type and 0 for either density or coordinate
    try:
        data_type = kwargs["data_type"]
        if data_type.lower() == "histogram":
            offset = 1
        elif data_type.lower() == "density" or \
                 data_type.lower() == "coordinate":
            offset = 0
        else:
            raise RuntimeError("Do not understand data type given: %s" % \
                               data_type)
    # Default is offset for histogram
    except KeyError:
        offset = 1

    # Setup some variables 
    dim = 2
    N_tot = 1

    # Create 2D spectrum object
    so_dim = SOM.SO(dim)

    # Set the axis locations
    param_axis_loc = 0    
    arb_axis_loc = 1

    # Rebin original data to rebin_axis if necessary
    if rebin_axis is not None:
        som1 = common_lib.rebin_axis_1D_frac(som, rebin_axis)
        len_arb_axis = len(rebin_axis) - offset
        so_dim.axis[arb_axis_loc].val = rebin_axis
    else:
        som1 = som
        len_arb_axis = len(som[0].axis[0].val) - offset
        so_dim.axis[arb_axis_loc].val = som[0].axis[0].val

    del som

    # Get parameter axis information
    len_param_axis = len(param_axis) - offset
    so_dim.axis[param_axis_loc].val = param_axis

    if pixnorm:
        pixarr = nessi_list.NessiList(len_param_axis)

    # Get the parameter lookup array
    pfunc = hlr_utils.__getattribute__(param_func)
    lookup_array = pfunc(som1, param)

    # Create y and var_y lists from total 2D size
    N_tot = len_param_axis * len_arb_axis
    so_dim.y = nessi_list.NessiList(N_tot)
    so_dim.var_y = nessi_list.NessiList(N_tot)

    # Loop through data and create 2D spectrum
    len_som = hlr_utils.get_length(som1)
    for i in xrange(len_som):
        val = hlr_utils.get_value(som1, i, "SOM", "y")
        err2 = hlr_utils.get_err2(som1, i, "SOM", "y")

        bin_index = utils.bisect_helper(param_axis, lookup_array[i])
        start = bin_index * len_arb_axis

        if pixnorm:
            pixarr[bin_index] += 1

        (so_dim.y, so_dim.var_y) = array_manip.add_ncerr(so_dim.y,
                                                         so_dim.var_y,
                                                         val,
                                                         err2,
                                                         a_start=start)        

    # If pixel normalization tracking enabled, divided slices by pixel counts
    if pixnorm:
        tmp_y = nessi_list.NessiList(Ntot)
        tmp_var_y = nessi_list.NessiList(Ntot)

        for i in range(len_param_axis):
            start = i * len_arb_axis
            end = (i + 1) * len_arb_axis

            slice_y = so_dim.y[start:end]
            slice_var_y = so_dim.var_y[start:end]

            (dslice_y, dslice_var_y) = array_manip.div_ncerr(slice_y,
                                                             slice_var_y,
                                                             pixarr[i],
                                                             0.0)

            (tmp_y, tmp_var_y) = array_manip.add_ncerr(tmp_y,
                                                       tmp_var_y,
                                                       dslice_y,
                                                       dslice_var_y,
                                                       a_start=start)

        so_dim.y = tmp_y
        so_dim.var_y = tmp_var_y
    
    # Create final 2D spectrum object container
    comb_som = SOM.SOM()
    comb_som.copyAttributes(som1)

    del som1

    # Check for so_id keyword argument
    try:
        so_dim.id = kwargs["so_id"]
    except KeyError:
        so_dim.id = 0

    # Check for y_label keyword argument
    try:
        comb_som.setYLabel(kwargs["y_label"])
    except KeyError:        
        comb_som.setYLabel("Counts")

    # Check for y_units keyword argument
    try:
        comb_som.setYUnits(kwargs["y_units"])
    except KeyError:
        comb_som.setYUnits("Counts / Arb")

    # Check for x_label keyword argument
    try:
        comb_som.setAllAxisLabels(kwargs["x_labels"])
    except KeyError:
        comb_som.setAllAxisLabels(["Parameter", "Arbitrary"])

    # Check for x_units keyword argument
    try:
        comb_som.setAllAxisUnits(kwargs["x_units"])
    except KeyError:
        comb_som.setAllAxisUnits(["Arb", "Arb"])

    comb_som.append(so_dim)

    del so_dim

    return comb_som
