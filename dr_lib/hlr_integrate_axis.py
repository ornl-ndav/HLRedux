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
    
    @keyword start: Index of the starting bin
    @type start: C{int}
    
    @keyword end: Index of the ending bin. This index is made inclusive by the
                  function.
    @type end: C{int}
    
    @keyword axis: This is the axis one wishes to manipulate. If no argument is
                   given the default value is I{y}.
    @type axis: C{string}=<y or x>
    
    @keyword axis_pos: This is position of the axis in the axis array. If no
    argument is given, the default value is I{0}.
    @type axis_pos: C{int}
    
    @keyword avg: This allows the function to calculate a geometrical average.
    The default value is I{False}.
    @type avg: C{boolean}

    @keyword width: This is a flag to turn on the multiplication of the
                    individual bin contents with the bins corresponding width.
    @type width: C{boolean}

    @keyword width_pos: This is position of the x-axis in the axis array from
                        which to calculate the bin widths in support of the
                        width flag. If no argument is given, the default value
                        is I{0}.
    @type width_pos: C{int}

    
    @return: The integration value and its associated error
    @rtype: C{tuple}

    
    @raise RuntimError: A C{SOM} or C{SO} is not given to the function.

    @raise RuntimeError: The width keyword is used with x-axis integration.
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
        start = 0

    # Check for ending bin
    try: 
        end = kwargs["end"]
        if end != -1:
            end += 1
        else:
            pass
    except KeyError:
        end = -1

    # Check for axis keyword argument
    try:
        axis = kwargs["axis"]
    except KeyError:
        axis = "y"
        
    # Check for axis_pos keyword argument
    try:
        axis_pos = kwargs["axis_pos"]
    except KeyError:
        axis_pos = 0

    # Check for avg keyword argument
    try:
        avg = kwargs["avg"]
    except KeyError:
        avg = False

    # Check for width keyword argument
    try:
        width = kwargs["width"]
    except KeyError:
        width = False        

    # Check for width_pos keyword argument
    try:
        width_pos = kwargs["width_pos"]
    except KeyError:
        width_pos = 0       
        
    integration = float(0)
    integration_error2 = float(0)

    import itertools
    if width:
        import utils

    bad_values = ["nan", "inf", "-inf"]

    for i in xrange(hlr_utils.get_length(obj)): 
        counter = 0  

        value = hlr_utils.get_value(obj, i, o_descr, axis, axis_pos)
        error = hlr_utils.get_err2(obj, i, o_descr, axis, axis_pos)

        if end == -1:
            value = value[start:]
            error = error[start:]
        else:
            value = value[start:end]
            error = error[start:end]
            
        if not width:
            for val, err2 in itertools.izip(value, error):
                if str(val) in bad_values or str(err2) in bad_values:
                    continue
                else:
                    integration += val
                    integration_error2 += err2
                    counter += 1
        else:
            if axis == "y":
                x_axis = hlr_utils.get_value(obj, i, o_descr, "x", width_pos)
                x_err2 = hlr_utils.get_err2(obj, i, o_descr, "x", width_pos)
            elif axis == "x":
                raise RuntimeError("Cannot use width flag with x-axis "\
                                   +"integration")

            bin_widths = utils.calc_bin_widths(x_axis, x_err2)

            for val, err2, delta in itertools.izip(value, error,
                                                   bin_widths[0]):
                if str(val) in bad_values or str(err2) in bad_values:
                    continue
                else:
                    integration += (delta * val)
                    integration_error2 += (delta * delta * err2)
                    counter += 1
        
    if avg:
        return (integration / float(counter),
                integration_error2 / float(counter))
    else:
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
    print "* som (avg)  :", integrate_axis(som2, avg=True)
    print "* som [2,4]  :", integrate_axis(som2, start=2, end=4)
    print "* som  (x)   :", integrate_axis(som2, axis="x")
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
