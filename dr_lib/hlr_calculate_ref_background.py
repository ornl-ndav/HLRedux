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

def calculate_ref_background(obj, no_bkg, inst, peak_excl, **kwargs):
    """
    This function takes a set of reflectometer data spectra in TOF, slices the
    data along TOF channels, fits a linear function to the slice to determine
    the background and then reassembles the slice back into TOF spectra.

    @param obj: Object containing data spectra
    @type obj: C{SOM.SOM} or C{SOM.SO}

    @param no_bkg: Flag for actually requesting a background calculation
    @type no_bkg: C{boolean}

    @param inst: String containing the reflectometer short name
    @type inst: C{string} (I{REF_L} or I{REF_M})

    @param peak_excl: The bounding pixel IDs for peak exclusion from fit
    @type peak_excl: C{tuple} containging the minimum and maximum pixel ID
    
    @param kwargs: A list of keyword arguments that the function accepts:

    @keyword aobj: An alternate data object containing the sizing information
                   for the constructed background spectra.
    @type aobj: C{SOM.SOM} or C{SOM.SO}
    

    @return: Background spectra
    @rtype: C{SOM.SOM}
    """
    if obj is None:
        return None

    if no_bkg:
        return None

    # import the helper functions
    import hlr_utils

    # Setup instrument specific stuff
    if inst == "REF_L":
        inst_pix_id = 1
    elif inst == "REF_M":
        inst_pix_id = 0
    else:
        raise RuntimeError("Do not know how to deal with instrument %s" % inst)

    # Check keywords
    try:
        aobj = kwargs["aobj"]
    except KeyError:
        aobj = None

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj)
    o_descr = hlr_utils.get_descr(obj)

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)

    # Set spectrum object to obtain background SOs from
    if aobj is None:
        bobj = obj
    else:
        bobj = aobj

    # Get the number of spectra for background calculation
    len_som = len(obj)

    # Get the number of spectra for final background object
    if aobj is None:
        len_bsom = len(obj)
    else:
        len_bsom = len(aobj)
        
    # Get the number of TOF channels
    len_tof = len(obj[0])

    # Create blank SOs for background spectra
    so_list = []

    import nessi_list
    import SOM
    import utils

    # Setup pixel axes
    pix_axis = nessi_list.NessiList()
    if peak_excl is not None:
        pix_axis_no_peak = nessi_list.NessiList()

    # Fill pixel axes and background SOs
    for k in xrange(len_bsom):
        map_so = hlr_utils.get_map_so(bobj, None, k)

        cur_pix_id = map_so.id[1][inst_pix_id]

        pix_axis.append(cur_pix_id)
        if peak_excl is not None:
            if cur_pix_id < peak_excl[0] or cur_pix_id > peak_excl[1]:
                pix_axis_no_peak.append(cur_pix_id)

        so = SOM.SO()
        hlr_utils.result_insert(so, "SO", map_so, None, "all")
        so_list.append(so)

    # Slice data, calculate weighted average and repackage spectra
    for i in xrange(len_tof):

        sliced_data = nessi_list.NessiList()
        sliced_data_err2 = nessi_list.NessiList()

        for j in xrange(len_som):
            obj1 = hlr_utils.get_value(obj, j, o_descr, "all")
            cur_pix_id = obj1.id[1][inst_pix_id]

            if peak_excl is None:
                filter_pixel = False

            if cur_pix_id < peak_excl[0] or cur_pix_id > peak_excl[1]:
                filter_pixel = False
            else:
                filter_pixel = True

            if not filter_pixel:
                if not (utils.compare(obj1.var_y[i], 0.0) == 0 and \
                        utils.compare(obj1.y[i], 0.0) == 0):
                    sliced_data.append(obj1.y[i])
                    sliced_data_err2.append(obj1.var_y[i])

        len_fit = len(sliced_data)

        if not len_fit:
            value = (0.0, 0.0)
        else:
            value = utils.weighted_average(sliced_data, sliced_data_err2,
                                           0, len_fit-1)

        for j in xrange(len_bsom):
            so_list[j].y[i] = value[0]
            so_list[j].var_y[i] = value[1]

    for m in xrange(len_bsom):
        hlr_utils.result_insert(result, res_descr, so_list[m], None, "all")

    return result

if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som("histogram", 1, 6)
    som1[0].id = ("bank1", (128, 0))
    som1[1].id = ("bank1", (128, 1))
    som1[2].id = ("bank1", (128, 2))
    som1[3].id = ("bank1", (128, 3))
    som1[4].id = ("bank1", (128, 4))
    som1[5].id = ("bank1", (128, 5))

    peak_range = (2, 3)

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]
    print "* ", som1[2]
    print "* ", som1[3]
    print "* ", som1[4]
    print "* ", som1[5]

    output = calculate_ref_background(som1, False, "REF_L", peak_range)

    print "********** calculate_ref_background"
    print "* som (REF_L): ", output
    print "* attrs: ", output.attr_list
