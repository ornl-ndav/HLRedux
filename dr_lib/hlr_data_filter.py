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

def data_filter(obj, **kwargs):
    """
    This function takes in an object containing data, scans it for bad data and
    removes that data from the arrays. The criteria is instrument dependent
    and subfunctions will be written that handle the instrument dependent
    criteria. This function will operate in a zeroing mode. This means that
    bins with bad data will have their value and error^2 set to zero. 

    @param obj: Object containing a single spectrum to be cleaned
    @type obj: C{SOM.SOM}

    @param kwargs: A list of keyword arguments that the function accepts:

    @keyword clean_axis: A flag that tells the function to check for I{inf}
    of I{-inf} values (normally at the ends of the axis) and remove those
    bins. The default behavior is I{False}.
    @type clean_axis: C{boolean}

    @keyword axis_index: The index on the axis to check for bad_values. This
    is assumed to be a single value and the default is -1 (last bin)
    @type axis_index: C{int}

    @keyword axis_pos: The position of the axis within the data object. This is
    necessary for greater than 1D spectra. The default value is 0.
    @type axis_pos: C{int}
    

    @return: Object containing a spectrum that has been cleaned of all bad data
    @rtype: C{SOM.SOM}
    

    @raise RuntimeError: The incoming object is not a C{SOM}.

    @raise AttributeError: 1D or 2D data passed is clean_axis is I{True}.

    @raise AttributeError: Axis position not 0 or 1 for 2D data.
    """
    import hlr_utils

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj)    
    o_descr = hlr_utils.get_descr(obj)

    if o_descr != "SOM":
        raise RuntimeError("Must provide a SOM to the function.")
    # Go on
    else:
        pass

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)

    # See if there is extra information present
    try:
        extra_som = result.attr_list["extra_som"]
    except KeyError:
        extra_som = None

    # Get instrument name
    inst_name = obj.attr_list.instrument.get_name()

    # Get dimension of incoming data
    data_dims = obj.getDimension()

    # Check keyword arguments
    try:
        clean_axis = kwargs["clean_axis"]
    except KeyError:
        clean_axis = False
        
    try:
        axis_index = kwargs["axis_index"]
    except KeyError:
        axis_index = -1

    try:
        axis_pos = kwargs["axis_pos"]
    except KeyError:
        axis_pos = 0

    if clean_axis:
        # Can only support 1D and 2D data axis cleaning for now
        if data_dims not in [1, 2]:
            raise AttributeError("Do not know how to clean %d-dimensional "
                                 +"data" % data_dims)

        if data_dims == 2:
            if axis_pos not in [0, 1]:
                raise AttributeError("2D data cannot have axis position %d!" \
                                     % axis_pos)
            if axis_pos:
                other_axis = 0
            else:
                other_axis = 1

            axis_lengths = (len(obj[0].axis[0].val) - 1,
                            len(obj[0].axis[1].val) - 1)

        else:
            axis_lengths = None

        if obj[0].axis[0].var is None:
            with_x_var = False
        else:
            with_x_var = True
    else:
        axis_lengths = None

    import copy
    import itertools

    len_som = hlr_utils.get_length(obj)
    if extra_som is not None:
        # Deal with extra information
        len_extra_som = len(extra_som)
        if len_extra_som == 1 and len_som > 1:
            # If the extra information has only one spectrum and the som
            # data has more than one, we'll need to clone that spectrum
            multiple_extra_som = True
            (res_extra_som, resd_descr) = hlr_utils.empty_result(extra_som)
            res_extra_som = hlr_utils.copy_som_attr(res_extra_som, resd_descr,
                                               extra_som, "SOM")
        else:
            # Everything should be on equal footing with respect to the number
            # of spectra, so we don't have to do anything.
            res_extra_som = extra_som
            multiple_extra_som = False
    else:
        len_extra_som = 0
        res_extra_som = None
        multiple_extra_som = False

    # Parse through the data to find the bad data locations. 
    for i in xrange(len_som):
        so = hlr_utils.get_value(obj, i, o_descr, "all")

        map_so = hlr_utils.get_map_so(obj, None, i)

        y_val = hlr_utils.get_value(obj, i, o_descr, "y")
        y_err2 = hlr_utils.get_err2(obj, i, o_descr, "y")

        y_val_new = copy.deepcopy(y_val)
        y_err2_new = copy.deepcopy(y_err2)

        if extra_som is not None:
            eso = hlr_utils.get_value(extra_som, i, "SOM", "all")
            eso_new = copy.deepcopy(eso)
        else:
            eso_new = None

        if multiple_extra_som:
            if i > 0:
                eso = hlr_utils.get_value(extra_som, 0, resd_descr, "all")
                extra_som.append(copy.deepcopy(eso))

        counter = 0
        for (yval, yerr2) in itertools.izip(so.y, so.var_y):
            to_filter = False

            if inst_name == "BSS":
                to_filter = __filter_sns_bss(yval, yerr2)
            elif inst_name == "REF_L" or inst_name == "REF_M":
                to_filter = __filter_sns_ref(yval, yerr2)
            elif inst_name == "SANS":
                to_filter = __filter_ieee(str(yval), str(yerr2))

            if to_filter:
                y_val_new[counter] = 0.0
                y_err2_new[counter] = 0.0

            counter += 1

        if clean_axis:
            x_val = hlr_utils.get_value(obj, i, o_descr, "x", axis_pos)
            x_err2 = hlr_utils.get_err2(obj, i, o_descr, "x", axis_pos)

            x_val_new = copy.deepcopy(x_val)
            x_err2_new = copy.deepcopy(x_err2)

            (y_val_new, y_err2_new,
             x_val_new, x_err2_new,
             eso_new) = __clean_axis(data_dims, axis_pos, axis_index,
                                     x_val_new, x_err2_new,
                                     y_val_new, y_err2_new,
                                     ext_so=eso_new, axis_len=axis_lengths)

        if extra_som is not None and multiple_extra_som:
            hlr_utils.result_insert(res_extra_som, resd_descr, eso_new, None,
                                    "all")

        if not clean_axis:
            hlr_utils.result_insert(result, res_descr, (y_val_new, y_err2_new),
                                    map_so, "y")
        else:
            if data_dims == 1:
                xvals = [x_val_new, x_err2_new]
                if not with_x_var:
                    del xvals[-1]
                hlr_utils.result_insert(result, res_descr,
                                        (y_val_new, y_err2_new),
                                        map_so, "all", axis_pos,
                                        xvals)
            elif data_dims == 2:
                ox_val = hlr_utils.get_value(obj, i, o_descr, "x", other_axis)
                ox_err2 = hlr_utils.get_err2(obj, i, o_descr, "x", other_axis)

                if axis_pos == 0:
                    xvals = [x_val_new, x_err2_new,
                             copy.deepcopy(ox_val), copy.deepcopy(ox_err2)]
                else:
                    xvals = [copy.deepcopy(ox_val), copy.deepcopy(ox_err2),
                             x_val_new, x_err2_new]

                if not with_x_var:
                    del xvals[1::2]

                hlr_utils.result_insert(result, res_descr,
                                        (y_val_new, y_err2_new),
                                        map_so, "all", axis_pos,
                                        xvals)

    if extra_som is not None:
        result.attr_list["extra_som"] = res_extra_som

    return result

def __clean_axis(dims, apos, aidx, *args, **kwargs):
    """
    This function trims the x-axis of choice if is contains a bad value:
    I{inf} or I{-inf}. The corresponding part of the value array is trimmed as
    well. If extra information is present, it must be trimmed as well.

    @param dims: The dimension of the incoming data
    @type dims: C{int}

    @param apos: The position in the spectra of the incoming x-axis. For 1D
    spectra this is always 0.

    @param aidx: The x-axis bin to check for the bad values.
    @type aidx: C{int}

    @param args: List of axes and extra information that need to be cleaned.
    They should be specified in the following order:

                 1. The x-axis to check and clean.
                 2. The squared uncertainties associated with the x-axis to
                    clean.
                 3. The associated y values to clean.
                 4. The squared uncertainties associated with the y values to
                    clean.

    @type args: C{nessi_list.NessiList}s

    @param kwargs: A list of keyword arguments that the function accepts:

    @keyword axis_len: A set of values that describes the lengths of the
    axes for dataset greater than 1D.
    @type axis_len: C{tuple}
    
    @keyword ext_so: The associated extra information to clean.
    @type ext_so: C{SOM.SO}

    
    @return: The possibly cleaned arrays (x_val, x_err2, y_val, y_err2, ext_so)
    @rtype: Five C{nessi_list.NessiList}s


    @raise RuntimeError: The axis length tuple is I{None} when used with 2D
                         data.
    """
    # Setup arguments
    x_val = args[0]
    x_err2 = args[1]
    y_val = args[2]
    y_err2 = args[3]
    
    # Check for keyword arguments
    try:
        axis_len = kwargs["axis_len"]
    except KeyError:
        axis_len = None

    try:
        ext_so = kwargs["ext_so"]
    except KeyError:
        ext_so = None        

    bad_values = ("inf", "-inf")

    if str(x_val[aidx]) in bad_values:
        del x_val[aidx]
        del x_err2[aidx]
        if dims == 1:
            del y_val[aidx]
            del y_err2[aidx]
            if ext_so is not None:
                del ext_so.y[aidx]
                del ext_so.var_y[aidx]
        elif dims == 2:
            if axis_len is None:
                raise RuntimeError("2D data needs to have the axis lengths "\
                                   +"provided.")
            # X-Axis for 2D data
            if apos == 0:
                if aidx == -1:
                    Nx = axis_len[0] - 1
                    end = axis_len[0] * axis_len[1]
                else:
                    Nx = aidx
                    end = axis_len[1]
                start = Nx * axis_len[1]
                del y_val[start:end]
                del y_err2[start:end]
                if ext_so is not None:
                    del ext_so.y[start:end]
                    del ext_so.var_y[start:end]
            # Y-Axis for 2D data                    
            elif apos == 1:
                if aidx == -1:
                    start = axis_len[1] - 1
                else:
                    start = aidx
                stride = axis_len[1]
                offset = 0
                for i in xrange(axis_len[0]):
                    index = (start + (i * stride)) - offset
                    del y_val[index]
                    del y_err2[index]
                    if ext_so is not None:
                        del ext_so.y[index]
                        del ext_so.var_y[index]

                    offset += 1

    return (y_val, y_err2, x_val, x_err2, ext_so)


def __filter_sns_bss(y, var2_y):
    """
    This function filters data for the SNS-BSS (aka SNS-BASIS) instrument. The
    only filtration requests are

      - IEEE bad values

    @param y: The value to check for filtering
    @type y: C{float} or C{int}

    @param var2_y: The error^2 to check for filtering
    @type var2_y: C{float} or C{int}


    @return: The determination if the value and error^2 need to be filtered
    @rtype: C{boolean}
    """
    return __filter_ieee(str(y), str(var2_y))

def __filter_sns_ref(y, var2_y):
    """
    This function filters data for the SNS REF instruments. The filtration
    requests are
    
      - IEEE bad values
      - y < 0
      - var2_y >= y^2 

    @param y: The value to check for filtering
    @type y: C{float} or C{int}

    @param var2_y: The error^2 to check for filtering
    @type var2_y: C{float} or C{int}


    @return: The determination if the value and error^2 need to be filtered
    @rtype: C{boolean}
    """
    import utils
    
    ieee_filter = __filter_ieee(str(y), str(var2_y))

    to_filter = False

    y2 = y * y

    if y < 0:
        to_filter = True
        
    if utils.compare(var2_y, y2) >= 0:
        to_filter = True

    return ieee_filter or to_filter

def __filter_ieee(syval, syerr2):
    """
    This function filters data looking for IEEE bad values like nan, inf and
    -inf.

    @param syval: The value to check for filtering
    @type syval: C{string}

    @param syerr2: The error^2 to check for filtering
    @type syerr2: C{string}


    @return: The determination if the value and error^2 need to be filtered
    @rtype: C{boolean}
    """    
    to_filter = False

    bad_values = ["nan", "inf", "-inf"]
    
    if syval in bad_values:
        to_filter = True
        
    if syerr2 in bad_values:
        to_filter = True

    return to_filter

if __name__ == "__main__":
    import nessi_list
    import SOM

    som = SOM.SOM()
    som.attr_list["instrument_name"] = "BSS"
    som.setAllAxisLabels(["wavelength"])

    so1 = SOM.SO()
    so1.id = 0

    # 1D data
    x_axis = nessi_list.NessiList()
    y_axis = nessi_list.NessiList()
    y_axis_err2 = nessi_list.NessiList()

    x_axis.extend(0, 1, 2, float("inf"))
    y_axis.extend(10, float("nan"), 12)
    y_axis_err2.extend(1, 1, 1)

    so1.y = y_axis
    so1.var_y = y_axis_err2
    so1.axis[0].val = x_axis

    som.append(so1)

    print "************ SOM (1D)"
    print "* ", som

    print "************ Filter 1D data"
    print "* som: ", data_filter(som)

    print "************ Filter 1D data with axis clean"
    print "* som: ", data_filter(som, clean_axis=True)

    so2 = SOM.SO(2, 0)

    som.setAxisLabel(0, "Q")
    som.setAxisLabel(1, "E_t")
    del som[0]

    # 2D data
    x1_axis = nessi_list.NessiList()
    x2_axis = nessi_list.NessiList()
    y_axis = nessi_list.NessiList()
    y_axis_err2 = nessi_list.NessiList()

    x1_axis.extend(float("-inf"), 1, 2, 3)
    x2_axis.extend(0, 1, float("inf"))
    y_axis.extend(10, 11, float("nan"), 13, 14, float("inf"))
    y_axis_err2.extend(float("inf"), 1, 1, 1, 1, 1)

    so2.y = y_axis
    so2.var_y = y_axis_err2
    so2.axis[0].val = x1_axis
    so2.axis[1].val = x2_axis

    som.append(so2)

    print
    print "************ SOM (2D)"
    print "* ", som

    print "************ Filter 2D data"
    print "* som: ", data_filter(som)

    y2_axis = nessi_list.NessiList()
    y2_err2 = nessi_list.NessiList()
    y2_axis.extend(10, 11, 12, 13, 14, 15)
    y2_err2.extend(1, 1, 1, 1, 1, 1)

    som[0].y = y2_axis
    som[0].var_y = y2_err2

    print
    print "************ SOM (2D)"
    print "* ", som

    print "************ Filter 2D data with axis clean (0)"
    print "* som: ", data_filter(som, clean_axis=True, axis_index=0)

    print "************ Filter 2D data with axis clean (1)"
    print "* som: ", data_filter(som, clean_axis=True, axis_pos=1)    

    x1_2_axis = nessi_list.NessiList()
    x2_2_axis = nessi_list.NessiList()
    x1_2_axis.extend(0, 1, 2, float("inf"))
    x2_2_axis.extend(float("-inf"), 1, 2)

    som[0].axis[0].val = x1_2_axis
    som[0].axis[1].val = x2_2_axis

    print
    print "************ SOM (2D)"
    print "* ", som

    print "************ Filter 2D data with axis clean (0)"
    print "* som: ", data_filter(som, clean_axis=True)

    print "************ Filter 2D data with axis clean (1)"
    print "* som: ", data_filter(som, clean_axis=True, axis_pos=1,
                                 axis_index=0)    
