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
import hlr_utils
import utils

def calc_BSS_coeffs(map_so, inst, *args):
    """
    This function calculates the x_i coefficients for the BSS instrument

    @param map_so: The spectrum object to calculate the coefficients for
    @type map_so: C{SOM.SO}

    @param inst: The instrument object associated with the data
    @type inst: C{SOM.Instrument} or C{SOM.CompositeInstrument}

    @param args: A list of parameters (C{tuple}s with value and err^2) used to
    calculate the x_i coefficients

    The following is a list of the arguments needed in there expected order
      1. Initial Energy
      2. Momentum Transfer
      3. Initial Wavevector
      4. Initial Time-of-Flight
      5. Polar Angle
      6. Final Energy
      7. Final Wavevector
      8. Final Wavelength
      9. Source to Sample Distance
      10. Sample to Detector Distance
      11. Vector of Zeros
    @type args: C{list}


    @return: The calculated coefficients (x_1, x_2, x_3, x_4)
    @rtype: C{tuple} of 4 C{nessi_list.NessiList}s 
    """
    import math
    
    # Settle out the arguments to sensible names
    E_i = args[0][0]
    E_i_err2 = args[0][1]
    Q = args[1][0]
    Q_err2 = args[1][1]
    k_i = args[2][0]
    k_i_err2 = args[2][1]
    T_i = args[3][0]
    T_i_err2 = args[3][1]
    polar_angle = args[4]
    E_f = args[5]
    k_f = args[6]
    l_f = args[7]
    L_s = args[8]
    L_d = args[9]
    zero_vec = args[10]

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

    dlf_dh = 0.1
    dphi_dh = 0.1
    dpol_dh = 0.1
    dpol_dpolD = 0.1
    dphi_dpolD = 0.1

    # Calculate bin centric values
    (E_i_bc, E_i_bc_err2) = utils.calc_bin_centers(E_i, E_i_err2)
    (k_i_bc, k_i_bc_err2) = utils.calc_bin_centers(k_i, k_i_err2)
    (Q_bc, Q_bc_err2) = utils.calc_bin_centers(Q, Q_err2)
    (T_i_bc, T_i_bc_err2) = utils.calc_bin_centers(T_i, T_i_err2)
    
    # Get numeric values
    sin_polar = math.sin(polar_angle)
    cos_polar = math.cos(polar_angle)
    length_ratio = L_d / L_s
    lambda_const = ((2.0 * math.pi) / (l_f * l_f)) * dlf_dh
    kf_cos_pol = k_f * cos_polar
    kf_sin_pol = k_f * sin_polar

    # Calculate coefficients
    (x_1, x_1_err2) = __calc_x1(k_i_bc, Q_bc, length_ratio, k_f,
                                kf_cos_pol, kf_sin_pol, lambda_const,
                                dphi_dh, dpol_dh, dpol_dpolD, dphi_dpolD,
                                cos_polar, zero_vec)
    (x_2, x_2_err2) = __calc_x2(k_i_bc, Q_bc, T_i_bc, kf_cos_pol, zero_vec)
    (x_3, x_3_err2) = __calc_x3(k_i_bc, E_i_bc, length_ratio, E_f, k_f,
                                lambda_const, zero_vec)
    (x_4, x_4_err2) = __calc_x4(E_i_bc, T_i_bc, zero_vec)

    return (x_1, x_2, x_3, x_4)

def calc_BSS_EQ_verticies(*args):
    """
    This function calculates the S(Q,E) bin verticies for BSS. It uses the
    x_i coefficients, dT, dh and the E and Q bin centers for the calculation.

    @param args: A list of parameters (C{tuple}s with value and err^2) used to
    calculate the x_i coefficients

    The following is a list of the arguments needed in there expected order
      1. Energy Transfer
      2. Momentum Transfer
      3. x_1 coefficient
      4. x_2 coefficient
      5. x_3 coefficient
      6. x_4 coefficient
      7. dT (Time-of-flight bin widths)
      8. dh (Height of detector pixel)
      9. Vector of Zeros
    @type args: C{list}


    @return: The calculated Q and E verticies ((Q_1, E_1), (Q_2, E_2),
             (Q_3, E_3), (Q_4, E_4))
    @rtype: C{tuple} of 4 C{tuple}s of 2 C{nessi_list.NessiList}s 
    """
    # Settle out the arguments to sensible names    
    E_t = args[0][0]
    E_t_err2 = args[0][1]
    Q = args[1][0]
    Q_err2 = args[1][1]
    x_1 = args[2]
    x_2 = args[3]
    x_3 = args[4]
    x_4 = args[5]
    dT = args[6]
    dh = args[7]
    zero_vec = args[8]

    # Calculate bin centric values
    (E_t_bc, E_t_bc_err2) = utils.calc_bin_centers(E_t, E_t_err2)
    (Q_bc, Q_bc_err2) = utils.calc_bin_centers(Q, Q_err2)

    (x1dh, x1dh_err2) = array_manip.mult_ncerr(x_1, zero_vec, dh, 0.0)
    (x3dh, x3dh_err2) = array_manip.mult_ncerr(x_3, zero_vec, dh, 0.0)
    (x2dT, x2dT_err2) = array_manip.mult_ncerr(x_2, zero_vec, dT, zero_vec)
    (x4dT, x4dT_err2) = array_manip.mult_ncerr(x_4, zero_vec, dT, zero_vec)    

    (x1dh_p_x2dT, x1dh_p_x2dT_err2) = array_manip.add_ncerr(x1dh, x1dh_err2,
                                                            x2dT, x2dT_err2)
    (x3dh_p_x4dT, x3dh_p_x4dT_err2) = array_manip.add_ncerr(x3dh, x3dh_err2,
                                                            x4dT, x4dT_err2)
    (x1dh_m_x2dT, x1dh_m_x2dT_err2) = array_manip.sub_ncerr(x1dh, x1dh_err2,
                                                            x2dT, x2dT_err2)
    (x3dh_m_x4dT, x3dh_m_x4dT_err2) = array_manip.sub_ncerr(x3dh, x3dh_err2,
                                                            x4dT, x4dT_err2) 

    (dQ_1, dQ_1_err2) = array_manip.mult_ncerr(x1dh_p_x2dT, x1dh_p_x2dT_err2,
                                               -0.5, 0.0)
    (dE_1, dE_1_err2) = array_manip.mult_ncerr(x3dh_p_x4dT, x3dh_p_x4dT_err2,
                                               -0.5, 0.0)
    (dQ_2, dQ_2_err2) = array_manip.mult_ncerr(x1dh_m_x2dT, x1dh_m_x2dT_err2,
                                               -0.5, 0.0)
    (dE_2, dE_2_err2) = array_manip.mult_ncerr(x3dh_m_x4dT, x3dh_m_x4dT_err2,
                                               -0.5, 0.0)

    dQ_3 = array_manip.abs_val(dQ_1)
    dE_3 = array_manip.abs_val(dE_1)
    dQ_4 = array_manip.abs_val(dQ_2)
    dE_4 = array_manip.abs_val(dE_2)
    dQ_3_err2 = array_manip.abs_val(dQ_1_err2)
    dE_3_err2 = array_manip.abs_val(dE_1_err2)
    dQ_4_err2 = array_manip.abs_val(dQ_2_err2)
    dE_4_err2 = array_manip.abs_val(dE_2_err2)

    (Q_1, Q_1_err2) = array_manip.add_ncerr(Q_bc, Q_bc_err2, dQ_1, dQ_1_err2)
    (E_t_1, E_t_1_err2) = array_manip.add_ncerr(E_t_bc, E_t_bc_err2,
                                                dE_1, dE_1_err2)
    (Q_2, Q_2_err2) = array_manip.add_ncerr(Q_bc, Q_bc_err2, dQ_2, dQ_2_err2)
    (E_t_2, E_t_2_err2) = array_manip.add_ncerr(E_t_bc, E_t_bc_err2,
                                                dE_2, dE_2_err2)    
    (Q_3, Q_3_err2) = array_manip.add_ncerr(Q_bc, Q_bc_err2, dQ_3, dQ_3_err2)
    (E_t_3, E_t_3_err2) = array_manip.add_ncerr(E_t_bc, E_t_bc_err2,
                                                dE_3, dE_3_err2)
    (Q_4, Q_4_err2) = array_manip.add_ncerr(Q_bc, Q_bc_err2, dQ_4, dQ_4_err2)
    (E_t_4, E_t_4_err2) = array_manip.add_ncerr(E_t_bc, E_t_bc_err2,
                                                dE_4, dE_4_err2)
    
    return ((Q_1, E_t_1), (Q_2, E_t_2), (Q_3, E_t_3), (Q_4, E_t_4))
    
def __calc_x1(*args):
    """
    This function calculates the x1 coeffiecient to the S(Q,E) Jacobian

    @param args: A list of parameters used to calculate the x1 coefficient

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

    @param args: A list of parameters used to calculate the x2 coefficient

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

    @param args: A list of parameters used to calculate the x3 coefficient

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

    @param args: A list of parameters used to calculate the x4 coefficient

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

