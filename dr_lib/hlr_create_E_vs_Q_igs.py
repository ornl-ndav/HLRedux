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

import axis_manip
import hlr_utils
import SOM

def create_E_vs_Q_igs(E_t_som, *args, **kwargs):
    """
    This functions takes a SOM with an energy transfer axis and turns the SOs
    contained in the SOM to 2D a SO with E and Q axes.

    Parameters:
    ----------
    -> E_t_som is the input SOM with energy transfer axis
    -> *args is a mandatory list of axes for rebinning.  There is a particular
       order to them. They should be present in the following order:
       Without errors
       1. Energy transfer
       2. Momentum transfer
       With errors
       1. Energy transfer
       2. Energy transfer error^2
       3. Momentum transfer
       4. Momentum transfer error ^2
       
    -> **kwargs is a dictionary of optional keywords that pass information to
       the function. Here are the currently accepted keywords:
       - withXVar=<string>. The string will either be True or False. If the
                  keyword is not present, the default value will be False
       - fast=<boolean> Turn on the use of the diagonal rebinning. This will
                        the default operation
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
    <- A SOM containing a 2D SO with E and Q axes

    Exceptions:
    ----------
    <- RuntimeError is raised if anything other than a SOM is passed to the
       function
    <- RuntimeError is raised if an instrument is not contained in the SOM
    """
    import nessi_list

    # Setup some variables 
    dim = 2
    N_y = []
    N_tot = 1
    N_args = len(args)

    # Check withXVar keyword argument and also check number of given args.
    # Set xvar to the appropriate value
    try:
        value = kwargs["withXVar"]
        if value.lower() == "true":
            if N_args != 4:
                raise RuntimeError("Since you have requested x errors, 4 x "\
                                   +"axes must be provided.")
            else:
                xvar = True
        elif value.lower() == "false":
            if N_args != 2:
                raise RuntimeError("Since you did not requested x errors, 2 "\
                                   +"x axes must be provided.")
            else:
                xvar = False
        else:
            raise RuntimeError("Do not understand given parameter %s" % \
                               value)
    except KeyError:
        if N_args != 2:
            raise RuntimeError("Since you did not requested x errors, 2 "\
                               +"x axes must be provided.")
        else:
            xvar = False

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

    try:
        run_fast = kwargs["fast"]
    except KeyError:
        run_fast = True

    so_dim = SOM.SO(dim)


    for i in range(dim):
        # Set the x-axis arguments from the *args list into the new SO
        if not xvar:
            # Axis positions are 1 (Q) and 0 (E)
            position = dim - i - 1
            so_dim.axis[i].val = args[position]
        else:
            # Axis positions are 2 (Q), 3 (eQ), 0 (E), 1 (eE)
            position = dim - 2 * i
            so_dim.axis[i].val = args[position]
            so_dim.axis[i].var = args[position + 1]

        # Set individual value axis sizes (not x-axis size)
        N_y.append(len(args[position]) - offset)

        # Calculate total 2D array size
        N_tot = N_tot * N_y[-1]

    # Create y and var_y lists from total 2D size
    so_dim.y = nessi_list.NessiList(N_tot)
    so_dim.var_y = nessi_list.NessiList(N_tot)

    inst = E_t_som.attr_list.instrument
    lambda_final = E_t_som.attr_list["Wavelength_final"]

    import array_manip
    import utils
    
    # Length of 2D data block
    y_len = len(E_t_som[0])
    y2d_len = y_len * y_len

    for j in xrange(hlr_utils.get_length(E_t_som)):
        # Get lambda_f from instrument information
        map_so = hlr_utils.get_map_so(E_t_som, None, j)

        (angle, angle_err2) = hlr_utils.get_parameter("polar", map_so, inst)

        l_f = hlr_utils.get_special(lambda_final, map_so)

        E_f = axis_manip.wavelength_to_energy(l_f[0], l_f[1])

        # Get E_t axis
        E_t = hlr_utils.get_value(E_t_som, j, "SOM", "x")
        E_t_err2 = hlr_utils.get_err2(E_t_som, j, "SOM", "x")

        E_i = array_manip.add_ncerr(E_t, E_t_err2,
                                    E_f[0]*1000.0, E_f[1]*1000.0)

        E_i = array_manip.mult_ncerr(E_i[0], E_i[1], 1.0/1000.0, 0.0)
        # Get lambda_i
        l_i = axis_manip.energy_to_wavelength(E_i[0], E_i[1])

        # Convert lambda_i to k_i
        k_i = axis_manip.wavelength_to_scalar_k(l_i[0], l_i[1])

        # Convert lambda_f to k_f
        k_f = axis_manip.wavelength_to_scalar_k(l_f[0], l_f[1])

        # Convert k_i and k_f to Q
        Q = axis_manip.init_scatt_wavevector_to_scalar_Q(k_i[0], k_i[1],
                                                         k_f[0], k_f[1],
                                                         angle, angle_err2)

        yval = hlr_utils.get_value(E_t_som, j, "SOM", "y")
        yerr2 = hlr_utils.get_err2(E_t_som, j, "SOM", "y")

        (yval, yerr2) = utils.linear_order_jacobian(l_i[0], Q[0],
                                                    yval, yerr2)

        if run_fast:
            y_2d = axis_manip.rebin_diagonal(Q[0], E_t, yval, yerr2,
                                             so_dim.axis[0].val,
                                             so_dim.axis[1].val)
            
            (so_dim.y, so_dim.var_y) = array_manip.add_ncerr(so_dim.y,
                                                             so_dim.var_y,
                                                             y_2d[0],
                                                             y_2d[1])
            
        else:
            y_2d = nessi_list.NessiList(y2d_len)
            var_y_2d = nessi_list.NessiList(y2d_len)
            
            for m in xrange(y_len):
                y_2d[m * (y_len + 1)] = yval[m]
                var_y_2d[m * (y_len + 1)] = yerr2[m]
                
            # Rebin both axes
            y_2d_new = axis_manip.rebin_axis_2D(Q[0], E_t,
                                                y_2d, var_y_2d,
                                                so_dim.axis[0].val,
                                                so_dim.axis[1].val)
            del y_2d, var_y_2d
            
            # Add data
                
            (so_dim.y, so_dim.var_y) = array_manip.add_ncerr(so_dim.y,
                                                             so_dim.var_y,
                                                             y_2d_new[0],
                                                             y_2d_new[1])

    # Check for so_id keyword argument
    if kwargs.has_key("so_id"):
        so_dim.id = kwargs["so_id"]
    else:
        so_dim.id = 0

    comb_som = SOM.SOM()
    comb_som.copyAttributes(E_t_som)

    # Check for y_label keyword argument
    if kwargs.has_key("y_label"):
        comb_som.setYLabel(kwargs["y_label"])
    else:
        comb_som.setYLabel("Counts")

    # Check for y_units keyword argument
    if kwargs.has_key("y_units"):
        comb_som.setYUnits(kwargs["y_units"])
    else:
        comb_som.setYUnits("Counts / ueV A^-1")

    # Check for x_labels keyword argument
    if kwargs.has_key("x_labels"):
        comb_som.setAllAxisLabels(kwargs["x_labels"])
    else:
        comb_som.setAllAxisLabels(["Momentum transfer", "Energy transfer"])

    # Check for x_units keyword argument
    if kwargs.has_key("x_units"):
        comb_som.setAllAxisUnits(kwargs["x_units"])
    else:
        comb_som.setAllAxisUnits(["A^-1", "ueV"])

    comb_som.append(so_dim)

    del so_dim

    return comb_som

if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som("histogram", 1, 3)
    som1.attr_list["Wavelength_final"] = (1, 1)
    som1.attr_list.instrument = SOM.ASG_Instrument()

    Q_axis = hlr_utils.make_axis(4, 5, 0.25)
    x_axis_err = hlr_utils.make_axis(0, 1, 0.25)

    som2 = hlr_test.generate_som("histogram", 1, 3)
    som2[0].axis[0].val = axis_manip.reverse_array_nc(som2[0].axis[0].val)
    som2[1].axis[0].val = axis_manip.reverse_array_nc(som2[1].axis[0].val)
    som2[2].axis[0].val = axis_manip.reverse_array_nc(som2[2].axis[0].val)
    som2.attr_list.instrument = SOM.ASG_Instrument()

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]
    print "* ", som1[2]

    print "********** SOM2"
    print "* ", som2[0]
    print "* ", som2[1]
    print "* ", som2[2]    

    print "********** create_E_vs_Q_igs"
    print "* som: ", create_E_vs_Q_igs(som1, som1[0].axis[0].val,
                                       x_axis_err, Q_axis, x_axis_err,
                                       withXVar="True", fast=False)
