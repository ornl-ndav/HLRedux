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

import array_manip
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

    import utils

    arr_len = 0
    #: Vector of zeros for function calculations
    zero_vec = None
    
    for j in xrange(hlr_utils.get_length(som)):
        # Get counts
        counts = hlr_utils.get_value(som, j, "SOM", "y")
        counts_err2 = hlr_utils.get_err2(som, j, "SOM", "y")

        arr_len = len(counts)
        zero_vec = nessi_list.NessiList(arr_len)

        # Get mapping SO
        map_so = hlr_utils.get_map_so(som, None, j)

        # Get lambda_i
        l_i = hlr_utils.get_value(som, j, "SOM", "x")
        l_i_err2 = hlr_utils.get_err2(som, j, "SOM", "x")
        
        # Get lambda_f from instrument information
        (l_f, l_f_err2, l_f_units) = hlr_utils.get_special(lambda_final,
                                                           map_so)

        # Get source to sample distance
        (L_s, L_s_err2) = hlr_utils.get_parameter("primary", map_so, inst)

        # Get sample to detector distance
        (L_d, L_d_err2) = hlr_utils.get_parameter("secondary", map_so, inst)

        # Get polar angle from instrument information
        (angle, angle_err2) = hlr_utils.get_parameter("polar", map_so, inst)

        # FIXME: Replace with correct calls, these are just place holders
        #(dlf_dh, dlf_dh_err2) = hlr_utils.get_parameter("dlf_dh", map_so,
        #                                                inst)
        #(dphi_dh, dphi_dh_err2) = hlr_utils.get_parameter("dphi_dh", map_so,
        #                                                inst)
        #(dpol_dh, dpol_dh_err2) = hlr_utils.get_parameter("dpol_dh", map_so,
        #                                                inst)
        #(dpol_dpolD, dpol_dpolD_err2) = hlr_utils.get_parameter("dpol_dpolD",
        #map_so,
        #                                                inst)
        #(dphi_dpolD, dphi_dpolD_err2) = hlr_utils.get_parameter("dphi_dpolD",
        #map_so,
        #                                                inst)
        #(dh, dh_err2) = hlr_utils.get_parameter("dh", map_so,
        #                                                inst)        

        dlf_dh = 0.1
        dphi_dh = 0.1
        dpol_dh = 0.1
        dpol_dpolD = 0.1
        dphi_dpolD = 0.1
        dh = 0.1

        # Calculate T_i
        (T_i, T_i_err2) = axis_manip.wavelength_to_tof(l_i, l_i_err2, 
                                                       L_s, L_s_err2)

        # Scale counts by lambda_f / lambda_i
        (l_i_bc, l_i_bc_err2) = utils.calc_bin_centers(l_i, l_i_err2)

        (ratio, ratio_err2) = array_manip.div_ncerr(l_f, l_f_err2,
                                                    l_i_bc, l_i_bc_err2)

        (counts, counts_err2) = array_manip.mult_ncerr(counts, counts_err2,
                                                       ratio, ratio_err2)

        # Calculate E_i
        (E_i, E_i_err2) = axis_manip.wavelength_to_energy(l_i, l_i_err2)

        # Calculate E_f
        (E_f, E_f_err2) = axis_manip.wavelength_to_energy(l_f, l_f_err2)

        # Calculate E_t
        (E_t, E_t_err2) = array_manip.sub_ncerr(E_i, E_i_err2, E_f, E_f_err2)

        # Convert E_t from meV to ueV
        (E_t, E_t_err2) = array_manip.mult_ncerr(E_t, E_t_err2, 1000.0, 0.0)
        (counts, counts_err2) = array_manip.mult_ncerr(counts, counts_err2,
                                                       1.0/1000.0, 0.0)

        # Convert lambda_i to k_i
        (k_i, k_i_err2) = axis_manip.wavelength_to_scalar_k(l_i, l_i_err2)

        # Convert lambda_f to k_f
        (k_f, k_f_err2) = axis_manip.wavelength_to_scalar_k(l_f, l_f_err2)

        # Convert k_i and k_f to Q
        (Q, Q_err2) = axis_manip.init_scatt_wavevector_to_scalar_Q(k_i,
                                                                   k_i_err2,
                                                                   k_f,
                                                                   k_f_err2,
                                                                   angle,
                                                                   angle_err2)

        # Calculate bin centric values
        (E_i_bc, E_i_bc_err2) = utils.calc_bin_centers(E_i, E_i_err2)
        (k_i_bc, k_i_bc_err2) = utils.calc_bin_centers(k_i, k_i_err2)
        (Q_bc, Q_bc_err2) = utils.calc_bin_centers(Q, Q_err2)
        (T_i_bc, T_i_bc_err2) = utils.calc_bin_centers(T_i, T_i_err2)

        # Get numeric values
        sin_polar = math.sin(angle)
        cos_polar = math.cos(angle)
        length_ratio = L_d / L_s
        lambda_const = ((2.0 * math.pi) / (l_f * l_f)) * dlf_dh
        kf_cos_pol = k_f * cos_polar
        kf_sin_pol = k_f * sin_polar

        # Calculate coefficients
        (x_1, x_1_err2) = __calc_x1(k_i_bc, Q_bc, length_ratio, k_f,
                                    kf_cos_pol, kf_sin_pol, lambda_const,
                                    dphi_dh, dpol_dh, dpol_dpolD, dphi_dpolD,
                                    math.cos(angle), zero_vec)
        (x_2, x_2_err2) = __calc_x2(k_i_bc, Q_bc, T_i_bc, kf_cos_pol, zero_vec)
        (x_3, x_3_err2) = __calc_x3(k_i_bc, E_i_bc, length_ratio, E_f, k_f,
                                    lambda_const, zero_vec)
        (x_4, x_4_err2) = __calc_x4(E_i_bc, T_i_bc, zero_vec)

        # Calculate dT
        (dT, dT_err2) = utils.calc_bin_widths(T_i, T_i_err2)

        # Calculate Jacobian
        (A, A_err2) = __calc_EQ_Jacobian(x_1, x_2, x_3, x_4, dT, dh, zero_vec)

        # Apply Jacobian
        (counts, counts_err2) = array_manip.div_ncerr(counts, counts_err2,
                                                      A, zero_vec)
        
        # Reverse counts, E_t, k_i and Q
        E_t = axis_manip.reverse_array_cp(E_t)
        E_t_err2 = axis_manip.reverse_array_cp(E_t_err2)
        Q = axis_manip.reverse_array_cp(Q)
        Q_err2 = axis_manip.reverse_array_cp(Q_err2)        
        counts = axis_manip.reverse_array_cp(counts)
        counts_err2 = axis_manip.reverse_array_cp(counts_err2)
        k_i = axis_manip.reverse_array_cp(k_i)

        if Q_filter:
            k_i_cutoff = k_f * math.cos(angle)
            k_i_cutbin = bisect.bisect(k_i, k_i_cutoff)
            
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

def __calc_x1(*args):
    """
    This function calculates the x1 coeffiecient to the S(Q,E) Jacobian

    @param args: A list of parameters used to calculate the x1 coeffiecient

    The following is a list of the arguments needed in there expected order
      1. Initial Wavevector
      2. Momentum Transfer
      3. Length Ratio (L_f / L_i)
      4. Final Wavevector
      5. Wavevector Final x Cos(polar)
      6. Wavevector Final x Sin(polar)
      7. Lambda Constant (2*pi/l_f^2)(dlf/dh)
      8. Derivative dphi_dh
      9. Derivative dpol_dh
      10. Derivative dpol_dpolD
      11. Derivative dphi_dpolD
      12. Cos(polar)
      13. Vector of Zeros
    @type args: C{list}

    
    @return: The calculated x1 coefficient
    @rtype: (C{nessi_list.NessiList}, C{nessi_list.NessiList})
    """
    # (L_f / L_i) * (1 / k_f)^2
    const1 = args[2] / (args[4] * args[4])
    # k_f * sin(pol) * (dpol/dh - (dpol/dpolD dphi/dh / dphi/dpolD))
    const2 = (args[8] - ((args[9] * args[7]) / args[10])) * args[5]

    # k_i^2
    temp1 = array_manip.mult_ncerr(args[0], args[12], args[0], args[12])
    # (L_f / L_i) * (k_i / k_f)^2
    temp2 = array_manip.mult_ncerr(temp1[0], temp1[1], const1, 0.0)
    # k_i - k_f * cos(pol)
    temp3 = array_manip.sub_ncerr(args[0], args[12], args[4], 0.0)
    # (k_i - k_f * cos(pol)) * (L_f / L_i) * (k_i / k_f)^2
    temp4 = array_manip.mult_ncerr(temp2[0], temp2[1], temp3[0], temp3[1])

    # k_i * cos(pol)
    temp5 = array_manip.mult_ncerr(args[0], args[12], args[11], 0.0)
    # k_f - k_i * cos(pol)
    temp6 = array_manip.sub_ncerr(args[3], 0.0, temp5[0], temp5[1])

    # (k_i - k_f * cos(pol)) * (L_f / L_i) * (k_i / k_f)^2 -
    # (k_f - k_i * cos(pol))
    temp7 = array_manip.sub_ncerr(temp4[0], temp4[1], temp6[0], temp6[1])
    # ((k_i - k_f * cos(pol)) * (L_f / L_i) * (k_i / k_f)^2 -
    # (k_f - k_i * cos(pol))) * (2 * pi / l_f^2) * dlf/dh
    temp8 = array_manip.mult_ncerr(temp7[0], temp7[1], args[6], 0.0)

    # k_i * k_f * sin(pol) * (dpol/dh - (dpol/dpolD dphi/dh / dphi/dpolD))
    temp9 = array_manip.mult_ncerr(args[0], args[12], const2, 0.0)

    # ((k_i - k_f * cos(pol)) * (L_f / L_i) * (k_i / k_f)^2 -
    # (k_f - k_i * cos(pol))) * (2 * pi / l_f^2) * dlf/dh + 
    # k_i * k_f * sin(pol) * (dpol/dh - (dpol/dpolD dphi/dh / dphi/dpolD))
    temp10 = array_manip.add_ncerr(temp8[0], temp8[1], temp9[0], temp9[1])

    # (((k_i - k_f * cos(pol)) * (L_f / L_i) * (k_i / k_f)^2 -
    # (k_f - k_i * cos(pol))) * (2 * pi / l_f^2) * dlf/dh + 
    # k_i * k_f * sin(pol) * (dpol/dh - (dpol/dpolD dphi/dh / dphi/dpolD))) / Q
    return array_manip.div_ncerr(temp10[0], temp10[1], args[1], args[12])

def __calc_x2(*args):
    """
    This function calculates the x2 coeffiecient to the S(Q,E) Jacobian

    @param args: A list of parameters used to calculate the x2 coeffiecient

    The following is a list of the arguments needed in there expected order
      1. Initial Wavevector
      2. Momentum Transfer
      3. Initial Time-of-Flight
      4. Wavevector Final x Cos(polar)
      5. Vector of Zeros
    @type args: C{list}

    
    @return: The calculated x2 coefficient
    @rtype: (C{nessi_list.NessiList}, C{nessi_list.NessiList})
    """
    # k_f * cos(pol) - k_i
    temp1 = array_manip.sub_ncerr(args[3], 0.0, args[0], args[4])
    # (k_f * cos(pol) - k_i) / Q
    temp2 = array_manip.div_ncerr(temp1[0], temp1[1], args[1], args[4])
    # k_i / T_i
    temp3 = array_manip.div_ncerr(args[0], args[4], args[2], args[4])
    # (k_i / T_i) * ((k_f * cos(pol) - k_i) / Q)
    return array_manip.mult_ncerr(temp2[0], temp2[1], temp3[0], temp3[1])

def __calc_x3(*args):
    """
    This function calculates the x3 coeffiecient to the S(Q,E) Jacobian

    @param args: A list of parameters used to calculate the x3 coeffiecient

    The following is a list of the arguments needed in there expected order
      1. Initial Wavevector
      2. Initial Energy
      3. Length Ratio (L_f / L_i)
      4. Final Energy
      5. Final Wavevector
      6. Lambda Constant (2*pi/l_f^2)(dlf/dh)
      7. Vector of Zeros
    @type args: C{list}

    
    @return: The calculated x3 coefficient
    @rtype: (C{nessi_list.NessiList}, C{nessi_list.NessiList})
    """
    # E_f / k_f
    const1 = args[3] / args[4]
    # (L_f / L_i) * (1 / k_f)^2
    const2 = args[2] / (args[4] * args[4])
    # (4 * pi / l_f^2) * dlf/dh
    const3 = 2.0 * args[5]
    # E_i * k_i
    temp1 = array_manip.mult_ncerr(args[0], args[6], args[1], args[6])
    # E_i * k_i * (L_f / L_i) * (1 / k_f)^2
    temp2 = array_manip.mult_ncerr(temp1[0], temp1[1], const2, 0.0)
    # E_i * k_i * (L_f / L_i) * (1 / k_f)^2 + E_f / k_f
    temp3 = array_manip.add_ncerr(temp2[0], temp2[1], const1, 0.0)
    # (4 * pi / l_f^2) * dlf/dh * (E_i * k_i * (L_f / L_i) * (1 / k_f)^2 +
    # E_f / k_f)
    return array_manip.mult_ncerr(temp3[0], temp3[1], const3, 0.0)
    
def __calc_x4(*args):
    """
    This function calculates the x4 coeffiecient to the S(Q,E) Jacobian

    @param args: A list of parameters used to calculate the x4 coeffiecient

    The following is a list of the arguments needed in there expected order
      1. Initial Energy
      2. Initial Time-of-Flight
      3. Vector of Zeros
    @type args: C{list}

    
    @return: The calculated x4 coefficient
    @rtype: (C{nessi_list.NessiList}, C{nessi_list.NessiList}) 
    """
    # E_i / T_i
    temp1 = array_manip.div_ncerr(args[0], args[2], args[1], args[2])
    # -2 * (E_i / T_i)
    return array_manip.mult_ncerr(temp1[0], temp1[1], -2.0, 0.0)

def __calc_EQ_Jacobian(*args):
    """
    This function calculates the Jacobian for S(Q,E)
    
    @param args: A list of parameters used to calculate the Jacobian

    The following is a list of the arguments needed in there expected order
      1. x_1 coefficient
      2. x_2 coefficient
      3. x_3 coefficient
      4. x_4 coefficient
      5. dT
      6. dh
      7. Vector of Zeros
    @type args: C{list}


    @return: The calculated Jacobian
    @rtype: (C{nessi_list.NessiList}, C{nessi_list.NessiList})
    """
    # x_2 * x_3
    temp1 = array_manip.mult_ncerr(args[1], args[6], args[2], args[6])
    # x_1 * x_4
    temp2 = array_manip.mult_ncerr(args[0], args[6], args[3], args[6])
    # dh * dT
    temp3 = array_manip.mult_ncerr(args[4], args[6], args[5], 0.0)

    # x_1 * x_4 - x_2 * x_3
    temp4 = array_manip.add_ncerr(temp1[0], temp1[1], temp2[0], temp2[1])
    # |x_1 * x_4 - x_2 * x_3|
    temp5 = (array_manip.abs_val(temp4[0]), temp4[1])
    # |x_1 * x_4 - x_2 * x_3| * dh * dT 
    return array_manip.mult_ncerr(temp3[0], temp3[1], temp5[0], temp5[1])

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
    print "* som: ", create_E_vs_Q_igs(som1, som1[0].axis[0].val,
                                       Q_axis)
