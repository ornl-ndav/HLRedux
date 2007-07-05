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

def create_E_vs_Q_igs(som, *args, **kwargs):
    """
    This function starts with the initial IGS wavelength axis and turns this
    into a 2D spectra with E and Q axes.

    @param som: The input object with initial IGS wavelength axis
    @type som: C{SOM.SOM}
    
    @param args: A mandatory list of axes for rebinning. There is a particular
                 order to them. They should be present in the following order:

                 Without errors
                   1. Energy transfer
                   2. Momentum transfer
                 With errors
                   1. Energy transfer
                   2. Energy transfer error^2
                   3. Momentum transfer
                   4. Momentum transfer error ^2
    @type args: C{nessi_list.NessiList}s
       
    @param kwargs: A list of keyword arguments that the function accepts:

    @keyword withXVar: Flag for whether the function should be expecting the
                       associated axes to have errors. The default value will
                       be I{False}.
    @type withXVar: C{boolean}

    @keyword data_type: Name of the data type which can be either I{histogram},
                        I{density} or I{coordinate}. The default value will be
                        I{histogram}
    @type data_type: C{string}
    
    @keyword Q_filter: Flag to turn on or off Q filtering. The default behavior
                       is I{True}.
    @type Q_filter: C{boolean}
    
    @keyword so_id: The identifier represents a number, string, tuple or other
                    object that describes the resulting C{SO}
    @type so_id: C{int}, C{string}, C{tuple}, C{pixel ID}
    
    @keyword y_label: The y axis label
    @type y_label: C{string}
    
    @keyword y_units: The y axis units
    @type y_units: C{string}
    
    @keyword x_labels: This is a list of names that sets the individual x axis
    labels
    @type x_labels: C{list} of C{string}s
    
    @keyword x_units: This is a list of names that sets the individual x axis
    units
    @type x_units: C{list} of C{string}s
    

    @return: Object containing a 2D C{SO} with E and Q axes
    @rtype: C{SOM.SOM}


    @raise RuntimeError: Anything other than a C{SOM} is passed to the function
    
    @raise RuntimeError: An instrument is not contained in the C{SOM}
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

    try:
        Q_filter = kwargs["Q_filter"]
    except KeyError:
        Q_filter = True

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

    inst = som.attr_list.instrument
    lambda_final = som.attr_list["Wavelength_final"]

    import bisect
    import math

    import array_manip
    import utils
    
    for j in xrange(hlr_utils.get_length(som)):
        # Get counts
        counts = hlr_utils.get_value(som, j, "SOM", "y")
        counts_err2 = hlr_utils.get_err2(som, j, "SOM", "y")
        
        # Get mapping SO
        map_so = hlr_utils.get_map_so(som, None, j)

        # Get lambda_i
        l_i = hlr_utils.get_value(som, j, "SOM", "x")
        l_i_err2 = hlr_utils.get_err2(som, j, "SOM", "x")
        
        # Get lambda_f from instrument information
        (l_f, l_f_err2) = hlr_utils.get_special(lambda_final, map_so)

        # Get polar angle from instrument information
        (angle, angle_err2) = hlr_utils.get_parameter("polar", map_so, inst)

        # Calculate E_i
        (E_i, E_i_err2) = axis_manip.wavelength_to_energy(l_i, l_i_err2)

        # Apply Jacobian for lambda_i to E_i
        (counts, counts_err2) = utils.linear_order_jacobian(l_i, E_i,
                                                            counts,
                                                            counts_err2)

        # Scale counts by lambda_f / lambda_i
        (l_i_bc, l_i_bc_err2) = utils.calc_bin_centers(l_i, l_i_err2)

        (ratio, ratio_err2) = array_manip.div_ncerr(l_f, l_f_err2,
                                                    l_i_bc, l_i_bc_err2)

        (counts, counts_err2) = array_manip.mult_ncerr(counts, counts_err2,
                                                       ratio, ratio_err2)
                                                            
        # Calculate E_f
        (E_f, E_f_err2) = axis_manip.wavelength_to_energy(l_f, l_f_err2)

        # Calculate E_t
        (E_t, E_t_err2) = array_manip.sub_ncerr(E_i, E_i_err2, E_f, E_f_err2)

        # Convert E_t from meV to ueV
        (E_t, E_t_err2) = array_manip.mult_ncerr(E_t, E_t_err2, 1000.0, 0.0)
        (counts, counts_err2) = array_manip.mult_ncerr(counts, counts_err2,
                                                       1.0/1000.0, 0.0)

        # Reverse counts and E_t
        E_t = axis_manip.reverse_array_cp(E_t)
        E_t_err2 = axis_manip.reverse_array_cp(E_t_err2)
        counts = axis_manip.reverse_array_cp(counts)
        counts_err2 = axis_manip.reverse_array_cp(counts_err2)

        # Convert lambda_i to k_i
        (k_i, k_i_err2) = axis_manip.wavelength_to_scalar_k(l_i, l_i_err2)

        # Reverse k_i
        k_i = axis_manip.reverse_array_cp(k_i)
        k_i_err2 = axis_manip.reverse_array_cp(k_i_err2)

        # Convert lambda_f to k_f
        (k_f, k_f_err2) = axis_manip.wavelength_to_scalar_k(l_f, l_f_err2)

        if Q_filter:
            k_i_cutoff = k_f * math.cos(angle)
            k_i_cutbin = bisect.bisect(k_i, k_i_cutoff)

        # Convert k_i and k_f to Q
        (Q, Q_err2) = axis_manip.init_scatt_wavevector_to_scalar_Q(k_i,
                                                                   k_i_err2,
                                                                   k_f,
                                                                   k_f_err2,
                                                                   angle,
                                                                   angle_err2)

        # Apply Jacobian for lambda_i to Q
        (counts, counts_err2) = utils.linear_order_jacobian(l_i, Q, counts,
                                                            counts_err2)

        if Q_filter:
            counts.__delslice__(0, k_i_cutbin)
            counts_err2.__delslice__(0, k_i_cutbin)
            Q.__delslice__(0, k_i_cutbin)
            Q_err2.__delslice__(0, k_i_cutbin)
            E_t.__delslice__(0, k_i_cutbin)
            E_t_err2.__delslice__(0, k_i_cutbin)

        # Rebin S_i(Q,E) to final S(Q,E)
        (y_2d, y_2d_err2) = axis_manip.rebin_diagonal(Q, E_t,
                                                      counts, counts_err2,
                                                      so_dim.axis[0].val,
                                                      so_dim.axis[1].val)
        
        # Add in together with previous results
        (so_dim.y, so_dim.var_y) = array_manip.add_ncerr(so_dim.y,
                                                         so_dim.var_y,
                                                         y_2d, y_2d_err2)

    # Check for so_id keyword argument
    if kwargs.has_key("so_id"):
        so_dim.id = kwargs["so_id"]
    else:
        so_dim.id = 0

    comb_som = SOM.SOM()
    comb_som.copyAttributes(som)

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

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]
    print "* ", som1[2]

    print "********** create_E_vs_Q_igs"
    print "* som: ", create_E_vs_Q_igs(som1, som1[0].axis[0].val,
                                       x_axis_err, Q_axis, x_axis_err,
                                       withXVar="True")
