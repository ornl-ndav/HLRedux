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

def filter_ref_data(som, **kwargs):
    """
    This function takes in an object containing reflectometer data, scans it
    for bad data and removes that data from the arrays. The following criteria
    are what is considered bad data:

              - R or dR^2 is nan, inf, -inf
              - R < 0
              - dR^2 >= R^2

    @param som: Object containing a single spectrum to be cleaned
    @type som: C{SOM.SOM}


    @return: Object containing a spectrum that has been cleaned of all bad data
    @rtype: C{SOM.SOM}

    @raise RuntimeError: The incoming object is not a C{SOM}.
    """
    import hlr_utils

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(som)    
    o_descr = hlr_utils.get_descr(som)

    if o_descr != "SOM":
        raise RuntimeError("Must provide a SOM to the function.")
    # Go on
    else:
        pass

    result = hlr_utils.copy_som_attr(result, res_descr, som, o_descr)

    try:
        dtot = result.attr_list["extra_som"]
    except KeyError:
        dtot = None

    import copy
    import itertools

    import utils
    
    index_map = {}

    len_som = hlr_utils.get_length(som)
    if dtot is not None:
        # Deal with delta t / t information
        len_dtot = len(dtot)
        if len_dtot == 1 and len_som > 1:
            # If the delta t / t information has only one spectrum and the som
            # data has more than one, we'll need to clone that delta t / t
            # spectrum
            multiple_dtot = True
            (res_dtot, resd_descr) = hlr_utils.empty_result(dtot)
            res_dtot = hlr_utils.copy_som_attr(res_dtot, resd_descr,
                                               dtot, "SOM")
        else:
            # Everything should be on equal footing with respect to the number
            # of spectra, so we don't have to do anything.
            res_dtot = dtot
            multiple_dtot = False
    else:
        len_dtot = 0
        res_dtot = None
        multiple_dtot = False

    # Parse through the data to find the bad data locations. 
    for i in xrange(len_som):
        counter = 0
        indicies = []
        so = hlr_utils.get_value(som, i, o_descr, "all")

        if multiple_dtot:
            if i > 0:
                dso = hlr_utils.get_value(dtot, 0, resd_descr, "all")
                dtot.append(copy.deepcopy(dso))

        for (yval, yerr2) in itertools.izip(so.y, so.var_y):
            tofilter = False

            yval2 = yval * yval
            syval = str(yval)
            syerr2 = str(yerr2)

            if syval == "nan" or syval == "inf" or syval == "-inf":
                tofilter = True

            if syerr2 == "nan" or syerr2 == "inf" or syerr2 == "-inf":
                tofilter = True

            if yval < 0:
                tofilter = True
                
            if yerr2 > yval2 or not utils.compare(yerr2, yval2):
                tofilter = True

            if tofilter:
                indicies.append(counter)

            counter += 1

        index_map[so.id] = indicies

    # Parse through data to remove bad data at requested indicies
    for j in xrange(len_som):
        map_so = hlr_utils.get_map_so(som, None, j)

        y_val = hlr_utils.get_value(som, j, o_descr, "y")
        y_err2 = hlr_utils.get_err2(som, j, o_descr, "y")

        x_val = hlr_utils.get_value(som, j, o_descr, "x", 0)
        x_err2 = hlr_utils.get_err2(som, j, o_descr, "x", 0)        

        if dtot is not None:
            dso = hlr_utils.get_value(dtot, j, "SOM", "all")

        offset = 0
        for index in index_map[map_so.id]:
            # Index arithmetic since list length get shorter with every
            # element deleted
            dindex = index - offset
            del y_val[dindex]
            del y_err2[dindex]
            del x_val[dindex]
            del x_err2[dindex]
            if dtot is not None:
                del dso.y[dindex]

            offset += 1

        if dtot is not None and multiple_dtot:
            hlr_utils.result_insert(res_dtot, resd_descr, dso, None, "all")

        hlr_utils.result_insert(result, res_descr, (y_val, y_err2), map_so,
                                "all", 0, [x_val])

    if dtot is not None:
        result.attr_list["extra_som"] = res_dtot

    return result

