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

def integrate_axis(obj, **kwargs):
    """
    This function takes a spectrum and integrates the given axis. The function
    assumes that the incoming data is in the histogram form.

    @param obj: Spectrum to be integrated
    @type obj: C{SOM.SOM} or C{SOM.SO}
    
    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword start: Value for the start range of the integration.
    @type start: C{float}
    
    @keyword end: Value for the end range of the integration.
    @type end: C{float}
    
    @keyword width: This is a flag to turn on the multiplication of the
                    individual bin contents with the bins corresponding width.
    @type width: C{boolean}

    @keyword width_pos: This is the position of the x-axis in the axis array
                        from which to calculate the bin widths in support of
                        the width flag. If no argument is given, the default
                        value is I{0}.
    @type width_pos: C{int}

    
    @return: The integration value and its associated error
    @rtype: C{tuple}

    
    @raise RuntimError: A C{SOM} or C{SO} is not given to the function.
    """

    # import the helper functions
    import hlr_utils

    # set up for working through data
    o_descr = hlr_utils.get_descr(obj)

    if o_descr == "number" or o_descr == "list":
        raise RuntimeError("Must provide a SOM of a SO to the function.")
    # Go on
    else:
        pass

    # Check for starting bin
    try:
        start = kwargs["start"]
    except KeyError:
        start = float("inf")

    # Check for ending bin
    try: 
        end = kwargs["end"]
    except KeyError:
        end = float("inf")

    # Check for width keyword argument
    try:
        width = kwargs["width"]
    except KeyError:
        width = False        

    if width:
        # Check for width_pos keyword argument
        try:
            width_pos = kwargs["width_pos"]
        except KeyError:
            width_pos = 0
    else:
        width_pos = 0

    import array_manip
    import utils

    integration = float(0)
    integration_error2 = float(0)
    
    len_obj = hlr_utils.get_length(obj)
    for i in xrange(len_obj): 
        value = hlr_utils.get_value(obj, i, o_descr, "y")
        error = hlr_utils.get_err2(obj, i, o_descr, "y")
        x_axis = hlr_utils.get_value(obj, i, o_descr, "x", width_pos)

        (int_val) = utils.integrate_1D_hist(value, error, x_axis,
                                            width=width,
                                            min_int=start,
                                            max_int=end)
        (integration,
         integration_error2) = array_manip.add_ncerr(int_val[0],
                                                     int_val[1],
                                                     integration,
                                                     integration_error2)

    return (integration, integration_error2)

if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som()
    som2 = hlr_test.generate_som("histogram", 1, 1)

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** SOM2"
    print "* ", som2[0]

    print "********** integrate_axis"
    print "* som        :", integrate_axis(som1)
    print "* som        :", integrate_axis(som2)
    print "* som [2,4]  :", integrate_axis(som2, start=2, end=4)
    print "* som (width):", integrate_axis(som1, width=True)
    print "* so         :", integrate_axis(som1[0])
    print "* so  [0,3]  :", integrate_axis(som1[0], start=0, end=3)
    print "* so (width) :", integrate_axis(som1[0], width=True)
    print
    
    # Test the NaNs

    som2[0].y[2] = float('nan')
    print "********** SOM2"
    print "* ", som2[0]
    
    print "* som        :", integrate_axis(som2)
    print "* som (width) :", integrate_axis(som2, width=True)
