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
    This function takes a SOM or a SO and integrates the given axis. The
    function assumes that the incoming data is in the histogram form.

    Parameters:
    ----------
    -> obj is a SOM or a SO
    -> kwargs is a list of key word arguments that the function accepts:
         start=<index of starting bin>
         end=<index of ending bin> This index is made inclusive by the
             function.
         axis=<y or x> This is the axis one wishes to manipulate. If no
              argument is given the default value is y
         axis_pos=<number> This is position of the axis in the axis array. If
                  no argument is given, the default value is 0

    Returns:
    -------
    <- A tuple containing the integration value and its associated error

    Exceptions:
    ----------
    <- RuntimError is raised if a SOM or SO is not given to the function
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

    integration = 0
    integration_error2 = 0

    for i in xrange(hlr_utils.get_length(obj)):
    
        value = hlr_utils.get_value(obj, i, o_descr, axis, axis_pos)
        error = hlr_utils.get_err2(obj, i, o_descr, axis, axis_pos)

        if end == -1:
            value = value[start:]
            error = error[start:]
        else:
            value = value[start:end]
            error = error[start:end]

        value_len = len(value)

        for i in xrange(value_len):
            integration += value[i]
            integration_error2 += error[i]
            
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
    print "* som      :", integrate_axis(som1)
    print "* som      :", integrate_axis(som2)
    print "* som [2,4]:", integrate_axis(som2, start=2, end=4)
    print "* som  (x) :", integrate_axis(som2, axis="x")
    print "* so       :", integrate_axis(som1[0])
    print "* so  [0,3]:", integrate_axis(som1[0], start=0, end=3)
