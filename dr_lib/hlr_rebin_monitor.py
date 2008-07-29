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

def rebin_monitor(obj1, obj2, **kwargs):
    """
    This function takes objects (1st is the monitor, 2nd is the detector data)
    and rebins the data for obj1 onto the axis provided by obj2. The pixel ID
    can be transferred as the pixel ID of the rebinned monitor histogram. A
    prefix is placed on the bank ID to dilineate that this is a rebinned
    monitor spectrum for that pixel.

    @param obj1: Monitor object that will be rebinned
    @type obj1: C{SOM.SOM} or C{SOM.SO}
    
    @param obj2: Detector data object that will provide the axis for rebinning
    @type obj2: C{SOM.SOM} or C{SOM.SO}

    @param kwargs: A list of keyword arguments that the function accepts

    @keyword use_pix_id: A flag that specifies if the pixel ID is to be used
    in the rebinned monitor spectrum. The default is I{False}.
    @type use_pix_id: C{boolean}

    @keyword prefix: Allows one to specify a prefix for the bank ID. The
                     default is I{m}.
    @type prefix: C{string}

    @keyword interpolate: A flag to use linear interpolation during rebinning.
                          The default is I{False}.
    @type interpolate: C{boolean}

    
    @return: Object that has been rebinned
    @rtype: C{SOM.SOM} or C{SOM.SO}


    @raise TypeError: The C{SOM}-C{SO} operation is attempted
    
    @raise TypeError: The C{SO}-C{SOM} operation is attempted
    
    @raise TypeError: obj1 not a C{SOM} or C{SO}
    
    @raise TypeError: obj2 not a C{SOM} or C{SO}
    """

    # import the helper functions
    import hlr_utils

    # Kickout if monitor object is None
    if obj1 is None:
        return obj1
    
    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj1, obj2)
    (o1_descr, o2_descr) = hlr_utils.get_descr(obj1, obj2)
    
    # error checking for types
    if o1_descr == "SOM" and o2_descr == "SO":
        raise TypeError, "SOM-SO operation not supported"
    elif o1_descr == "SO" and o2_descr == "SOM":
        raise TypeError("SO-SOM operation not supported")
    # Have the right object combination, go on
    else:
        pass

    # Check for keywords
    try:
        prefix = kwargs["prefix"]
    except KeyError:
        prefix = "m"

    try: 
        use_pix_id = kwargs["use_pix_id"]
    except KeyError:
        use_pix_id = False

    try: 
        interpolate = kwargs["interpolate"]
    except KeyError:
        interpolate = False        

    result = hlr_utils.copy_som_attr(result, res_descr, obj1, o1_descr)

    # iterate through the values
    import common_lib

    val1 = hlr_utils.get_value(obj1, 0, o1_descr, "all")

    for i in xrange(hlr_utils.get_length(obj2)):
        val2 = hlr_utils.get_value(obj2, i, o2_descr, "x")

        if interpolate:
            value = common_lib.rebin_axis_1D_linint(val1, val2)
        else:
            value = common_lib.rebin_axis_1D(val1, val2)
        if use_pix_id:
            # Set the pixel ID to the spectrum with modified bank ID
            try:
                value.id = (prefix+obj2[i].id[0],
                            (obj2[i].id[1][0], obj2[i].id[1][1]))
            except TypeError:
                value.id = prefix+str(obj2[i].id)
        
        hlr_utils.result_insert(result, res_descr, value, None, "all")

    return result
    
if __name__ == "__main__":
    import hlr_test
    import SOM

    som1 = SOM.SOM()
    som1.setAllAxisUnits(["Angstroms"])
    so1 = SOM.SO(construct=True)    
    so1.id = 1
    so1.axis[0].val.extend(range(0, 7, 2))
    so1.y.extend(0.994, 0.943, 0.932)
    so1.var_y.extend(0.010, 0.012, 0.013)
    som1.append(so1)

    som2 = hlr_test.generate_som()
    som2.setAllAxisUnits(["Angstroms"])

    
    print "********** SOM1"
    print "* ", som1[0]

    print "********** SOM2"
    print "* ", som2[0]
    print "* ", som2[1]

    print "********** rebin_monitor"
    print "* som+som :", rebin_monitor(som1, som2)
    print "* so +so  :", rebin_monitor(som1[0], som2[0], interpolate=True)

    
