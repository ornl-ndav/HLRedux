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

def create_2D_dist(som,*args,**kwargs):
    """
    This function takes a SOM of single spectrum with energy transfer axes and
    rebins those axes to a given axis and converts the spectra into a single
    I(Q,E) spectrum.

    Parameters:
    ----------
    -> som is the input SOM with energy transfer axis SOs
    -> *args is a list of axes for rebinning.  There is a particulare order
       to them. They should be present in the following order:
       Without errors
       1. Energy transfer
       2. Momentum transfer
       With errors
       1. Energy transfer
       2. Energy transfer error^2
       3. Momentum transfer
       4. Momentum transfer error ^2
       
    -> **kwargs is a dictionary of keywords that pass information to the
       function. Here are the currently accepted keywords:
       - withXVar=<string>. The string will either be True or False. If the
                  keyword is not present, the default value will be False
       - data_type=<string> The string can be either histogram, density or
                   coordinate. If the keyword is not present, the default
                   value will be histogram
       - so_id=<identifier> The identifier represents a number, string, tuple
               or other object that describes the resulting SO
       - y_label=<string> This is a string that sets the y axis label
       - y_units=<string> This is a string that sets the y axis units
       - x_labels=<list of strings> This is a list of strings that sets the
                  individual x axes labels
       - x_units=<list of string> This is a list of strings that sets the
                 individual x axes units

    Returns:
    -------
    <- A SOM with a single 2D SO with E and Q axes

    Exceptions:
    ----------
    <- RuntimeError is raised if the parameter given to the keyword argument
       withXVar is not True or False
    <- RuntimeError is raised if the parameter given to the keyword argument
       data_type is not histogram or density or coordinate
    <- RuntimeError is raised is the number of given arguments (x-axes) is not
       either 2 (no errors) or 4 (with errors)
    """

    import common_lib
    import hlr_utils
    import nessi_list
    import SOM

    # Setup some variables 
    dim = 2
    N_y = []
    N_tot = 1
    N_args = len(args)

    # Check withXVar keyword argument and also check number of given args.
    # Set xvar and Q_pos (position of the momentum transfer axis in the args
    # list) to the appropriate values
    try:
        value = kwargs["withXVar"]
        if value.lower() == "true":
            if N_args != 4:
                raise RuntimeError, "Since you have requested x errors, 4 x "\
                      +"axes must be provided."
            else:
                xvar = True
                Q_pos = 2
        elif value.lower() == "false":
            if N_args != 2:
                raise RuntimeError, "Since you did not requested x errors, 2 "\
                      +"x axes must be provided."
            else:
                xvar = False
                Q_pos = 1
        else:
            raise RuntimeError, "Do not understand given parameter %s" % \
                  value
    except KeyError:
        if N_args != 2:
            raise RuntimeError, "Since you did not requested x errors, 2 "\
                  +"x axes must be provided."
        else:
            xvar = False
            Q_pos = 1

    # Check dataType keyword argument. An offset will be set to 1 for the
    # histogram type and 0 for either density or coordinate
    try:
        type = kwargs["data_type"]
        if type.lower() == "histogram":
            offset = 1
        elif type.lower() == "density" or type.lower() == "coordinate":
            offset = 0
        else:
            raise RuntimeError, "Do not understand data type given: %s" % \
                  type
    # Default is offset for histogram
    except KeyError:
        offset = 1

    so_dim = SOM.SO(dim)

    for i in range(dim):
        # Set the x-axis arguments from the *args list into the new SO
        if not xvar:
            # Axis positions are 1 (Q) and 0 (E)
            position = dim-i-1
            so_dim.axis[i].val = args[position]
        else:
            # Axis positions are 2 (Q), 3 (eQ), 0 (E), 1 (eE)
            position = dim-2*i
            so_dim.axis[i].val = args[position]
            so_dim.axis[i].var = args[position+1]

        # Set individual value axis sizes (not x-axis size)
        N_y.append(len(args[position]) - offset)

        # Calculate total 2D array size
        N_tot = N_tot * N_y[-1]

    # Create y and var_y lists from total 2D size
    so_dim.y = nessi_list.NessiList(N_tot)
    so_dim.var_y = nessi_list.NessiList(N_tot)

    # Rebin data to E axis
    som1 = common_lib.rebin_axis_1D(som, args[0])

    som = None
    del som

    inst = som1.attr_list.instrument
    lambda_final = som1.attr_list["Wavelength_final"]

    import axis_manip
    
    for i in range(hlr_utils.get_length(som1)):
        # Find Q for pixel
        so = hlr_utils.get_value(som1,i,"SOM","all")
        (angle,angle_err2) = hlr_utils.get_parameter("polar",so,inst)
        
        (Q,Q_err2) = axis_manip.wavelength_to_scalar_Q(lambda_final[0],
                                                       lambda_final[1],
                                                       angle/2.0,
                                                       angle_err2/2.0)

        # Find Q value in given momentum transfer axis
        index = -1
        for j in range(N_y[0]):
            if Q >= args[Q_pos][j] and Q < args[Q_pos][j+1]:
                index = j
                break

        if index != -1:
            start = index * N_y[1]
            finish = (index + 1) * N_y[1]

            # Grab slice of 2D array
            so_temp = SOM.SO()
            so_temp.y.extend(so_dim.y[start:finish])
            so_temp.var_y.extend(so_dim.var_y[start:finish])

            # Add data values into slice
            so_temp = common_lib.add_ncerr(so, so_temp)

            # Put slice back into 2D array
            for k in range(start,finish):
                so_dim.y[k] = so_temp.y[k-start]
                so_dim.var_y[k] = so_temp.var_y[k-start]

        # If the Q value is not found in the given axis, do nothing and
        # continue
        else:
            pass

    # Check for so_id keyword argument
    if kwargs.has_key("so_id"):
        so_dim.id = kwargs["so_id"]
    else:
        so_dim.id = 0

    comb_som = SOM.SOM()
    comb_som.copyAttributes(som1)

    # Check for y_label keyword argument
    if kwargs.has_key("y_label"):
        comb_som.setYLabel(kwargs["y_label"])
    else:
        comb_som.setYLabel("Counts")

    # Check for y_units keyword argument
    if kwargs.has_key("y_units"):
        comb_som.setYUnits(kwargs["y_units"])
    else:
        comb_som.setYUnits("Counts / THz A^-1")

    # Check for x_labels keyword argument
    if kwargs.has_key("x_labels"):
        comb_som.setAllAxisLabels(kwargs["x_labels"])
    else:
        comb_som.setAllAxisLabels(["Momentum transfer","Energy transfer"])

    # Check for x_units keyword argument
    if kwargs.has_key("x_units"):
        comb_som.setAllAxisUnits(kwargs["x_units"])
    else:
        comb_som.setAllAxisUnits(["A^-1","THz"])

    comb_som.append(so_dim)

    return comb_som


if __name__=="__main__":
    import hlr_test
    import hlr_utils
    import SOM

    som1 = hlr_test.generate_som("histogram",1,3)
    som1.attr_list["Wavelength_final"] = (1,1)
    som1.attr_list.instrument = SOM.ASG_Instrument()

    axis = hlr_utils.make_axis(4,5,0.25)
    axis_err = hlr_utils.make_axis(0,1,0.25)

    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1]
    print "* ",som1[2]

    print "********** create_2D"
    print " som :",create_2D_dist(som1,som1[0].axis[0].val,axis_err,axis,axis_err,withXVar="True")
