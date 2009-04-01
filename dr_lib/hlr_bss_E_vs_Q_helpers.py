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
      5. Detector Pixel Height
      6. Polar Angle
      7. Final Energy
      8. Final Wavevector
      9. Final Wavelength
      10. Source to Sample Distance
      11. Sample to Detector Distance
      12. Time-zero Slope
      13. Vector of Zeros
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
    dh = args[4]
    polar_angle = args[5]
    E_f = args[6]
    k_f = args[7]
    l_f = args[8]
    L_s = args[9]
    L_d = args[10]
    T_0_s = args[11]
    zero_vec = args[12]

    # Constant h/m_n (meters / microsecond)
    H_OVER_MNEUT = 0.003956034e-10
    
    # Get the differential geometry parameters
    dlf_dh_tuple = hlr_utils.get_parameter("dlf_dh", map_so, inst)
    dlf_dh = dlf_dh_tuple[0]
    # dlf_dh should be unitless (Angstrom/Angstrom)
    dlf_dh *= 1e-10
    
    dpol_dh_tuple = hlr_utils.get_parameter("dpol_dh", map_so, inst)
    dpol_dh = dpol_dh_tuple[0]
    # Convert to radian/Angstrom
    dpol_dh *= 1e-10
    
    dpol_dtd_tuple = hlr_utils.get_parameter("dpol_dtd", map_so, inst)
    dpol_dtd = dpol_dtd_tuple[0]
    
    # Get the detector pixel angular width
    dtd_tuple = hlr_utils.get_parameter("dtd", map_so, inst)
    dtd = dtd_tuple[0]

    # Calculate bin centric values
    E_i_bc_tuple = utils.calc_bin_centers(E_i, E_i_err2)
    E_i_bc = E_i_bc_tuple[0]

    k_i_bc_tuple = utils.calc_bin_centers(k_i, k_i_err2)
    k_i_bc = k_i_bc_tuple[0]
    
    Q_bc_tuple = utils.calc_bin_centers(Q, Q_err2)
    Q_bc = Q_bc_tuple[0]
    
    T_i_bc_tuple = utils.calc_bin_centers(T_i, T_i_err2)
    T_i_bc = T_i_bc_tuple[0]
    
    # Get numeric values
    sin_polar = math.sin(polar_angle)
    cos_polar = math.cos(polar_angle)
    length_ratio = L_d / L_s
    lambda_const = ((2.0 * math.pi) / (l_f * l_f)) * dlf_dh
    kf_cos_pol = k_f * cos_polar
    kf_sin_pol = k_f * sin_polar
    t0_slope_corr = (1.0 / (1.0 + H_OVER_MNEUT * (T_0_s / L_s)))
    dtd_over_dh = dtd / dh

    # Calculate coefficients
    x_1_tuple = __calc_x1(k_i_bc, Q_bc, length_ratio, k_f, kf_cos_pol,
                          kf_sin_pol, lambda_const, dpol_dh, dpol_dtd,
                          dtd_over_dh, cos_polar, t0_slope_corr, zero_vec)
    x_1 = x_1_tuple[0]
    
    x_2_tuple = __calc_x2(k_i_bc, Q_bc, T_i_bc, kf_cos_pol, t0_slope_corr,
                          zero_vec)
    x_2 = x_2_tuple[0]
    
    x_3_tuple = __calc_x3(k_i_bc, E_i_bc, length_ratio, E_f, k_f, lambda_const,
                          t0_slope_corr, zero_vec)
    x_3 = x_3_tuple[0]
    
    x_4_tuple = __calc_x4(E_i_bc, T_i_bc, t0_slope_corr, zero_vec)
    x_4 = x_4_tuple[0]

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

    (dQ_3, dQ_3_err2) = array_manip.mult_ncerr(dQ_1, dQ_1_err2, -1.0, 0.0)
    (dE_3, dE_3_err2) = array_manip.mult_ncerr(dE_1, dE_1_err2, -1.0, 0.0)
    (dQ_4, dQ_4_err2) = array_manip.mult_ncerr(dQ_2, dQ_2_err2, -1.0, 0.0)
    (dE_4, dE_4_err2) = array_manip.mult_ncerr(dE_2, dE_2_err2, -1.0, 0.0)

    Q_1 = array_manip.add_ncerr(Q_bc, Q_bc_err2, dQ_1, dQ_1_err2)
    E_t_1 = array_manip.add_ncerr(E_t_bc, E_t_bc_err2, dE_1, dE_1_err2)
    
    Q_2 = array_manip.add_ncerr(Q_bc, Q_bc_err2, dQ_2, dQ_2_err2)
    E_t_2 = array_manip.add_ncerr(E_t_bc, E_t_bc_err2, dE_2, dE_2_err2)
    
    Q_3 = array_manip.add_ncerr(Q_bc, Q_bc_err2, dQ_3, dQ_3_err2)
    E_t_3 = array_manip.add_ncerr(E_t_bc, E_t_bc_err2, dE_3, dE_3_err2)
    
    Q_4 = array_manip.add_ncerr(Q_bc, Q_bc_err2, dQ_4, dQ_4_err2)
    E_t_4 = array_manip.add_ncerr(E_t_bc, E_t_bc_err2, dE_4, dE_4_err2)

    return ((Q_1[0], E_t_1[0]), (Q_2[0], E_t_2[0]),
            (Q_3[0], E_t_3[0]), (Q_4[0], E_t_4[0]))

def calc_BSS_solid_angle(map_so, inst):
    """
    This function calculates the solid angle for a given BSS detector pixel

    @param map_so: The object containing the pixel ID
    @type map_so: C{SOM.SO}

    @param inst: The object containing the instrument geometry
    @type inst: C{SOM.Instrument} or C{SOM.CompositeInstrument}


    @return: The solid angle for the given pixel
    @rtype: C{float}
    """
    # Get polar angle from instrument information
    angle_tuple = hlr_utils.get_parameter("polar", map_so, inst)
    angle = angle_tuple[0]

    # Get the detector pixel height
    dh_tuple = hlr_utils.get_parameter("dh", map_so, inst)
    dh = dh_tuple[0]

    # Get the detector pixel angular width
    dtd_tuple = hlr_utils.get_parameter("dtd", map_so, inst)
    dtd = dtd_tuple[0]

    # Get partial derivatives
    dazi_dh_tuple = hlr_utils.get_parameter("dazi_dh", map_so, inst)
    dazi_dh = dazi_dh_tuple[0]
    
    dpol_dh_tuple = hlr_utils.get_parameter("dpol_dh", map_so, inst)
    dpol_dh = dpol_dh_tuple[0]
    
    dpol_dtd_tuple = hlr_utils.get_parameter("dpol_dtd", map_so, inst)
    dpol_dtd = dpol_dtd_tuple[0]
    
    dazi_dtd_tuple = hlr_utils.get_parameter("dazi_dtd", map_so, inst)
    dazi_dtd = dazi_dtd_tuple[0]

    import math

    sin_pol = math.sin(angle)

    return math.fabs(sin_pol * dtd * dh *
                     (dpol_dtd * dazi_dh - dpol_dh * dazi_dtd))

def calc_BSS_delta_azi(map_so, inst):
    """
    This function calculates the delta azimuthal quantity for a given BSS
    detector pixel. The formula is:

    delta azi = dtd * dazi_dtd + dh * dazi_dh

    @param map_so: The object containing the pixel ID
    @type map_so: C{SOM.SO}

    @param inst: The object containing the instrument geometry
    @type inst: C{SOM.Instrument} or C{SOM.CompositeInstrument}


    @return: The delta azimuthal for the given pixel
    @rtype: C{float}
    """
    # Get the detector pixel height
    dh_tuple = hlr_utils.get_parameter("dh", map_so, inst)
    dh = dh_tuple[0]

    # Get the detector pixel angular width
    dtd_tuple = hlr_utils.get_parameter("dtd", map_so, inst)
    dtd = dtd_tuple[0]

    # Get partial derivatives
    dazi_dh_tuple = hlr_utils.get_parameter("dazi_dh", map_so, inst)
    dazi_dh = dazi_dh_tuple[0]

    dazi_dtd_tuple = hlr_utils.get_parameter("dazi_dtd", map_so, inst)
    dazi_dtd = dazi_dtd_tuple[0]

    return (dtd * dazi_dtd) + (dh * dazi_dh)

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
      8. Derivative dazi_dh
      9. Derivative dpol_dh
      10. Derivative dpol_dtd
      11. Derivative dazi_dtd
      12. Cos(polar)
      13. Time-zero Slope Correction
      14. Vector of Zeros
    @type args: C{list}

    
    @return: The calculated x1 coefficient
    @rtype: (C{nessi_list.NessiList}, C{nessi_list.NessiList})
    """
    # Settle out the arguments to sensible names
    k_i = args[0]
    Q = args[1]
    len_ratio = args[2]
    k_f = args[3]
    k_f_cos_pol = args[4]
    k_f_sin_pol = args[5]
    lam_const = args[6]
    dpol_dh = args[7]
    dpol_dtd = args[8]
    dtd_over_dh = args[9]
    cos_pol = args[10]
    t_0_s_corr = args[11]
    z_vec = args[12]
    
    # (L_f / L_i) * (1 / k_f)^2 * (1 / 1 + ((h / m) * (t0_s / L_i)))
    const1 = (len_ratio * t_0_s_corr) / (k_f * k_f)
    # (dpol/dh + (dpol/dtd * dtd/dh)) * k_f * sin(pol)
    const2 = (dpol_dh + (dpol_dtd * dtd_over_dh)) * k_f_sin_pol

    # k_i^2
    temp1 = array_manip.mult_ncerr(k_i, z_vec, k_i, z_vec)
    # (L_f / L_i) * (k_i / k_f)^2 * (1 / 1 + ((h / m) * (t0_s / L_i)))
    temp2 = array_manip.mult_ncerr(temp1[0], temp1[1], const1, 0.0)
    # k_i - k_f * cos(pol)
    temp3 = array_manip.sub_ncerr(k_i, z_vec, k_f_cos_pol, 0.0)
    # (k_i - k_f * cos(pol)) * (L_f / L_i) * (k_i / k_f)^2
    temp4 = array_manip.mult_ncerr(temp2[0], temp2[1], temp3[0], temp3[1])

    # k_i * cos(pol)
    temp5 = array_manip.mult_ncerr(k_i, z_vec, cos_pol, 0.0)
    # k_f - k_i * cos(pol)
    temp6 = array_manip.sub_ncerr(k_f, 0.0, temp5[0], temp5[1])

    # (k_i - k_f * cos(pol)) * (L_f / L_i) * (k_i / k_f)^2 -
    # (k_f - k_i * cos(pol))
    temp7 = array_manip.sub_ncerr(temp4[0], temp4[1], temp6[0], temp6[1])
    # ((k_i - k_f * cos(pol)) * (L_f / L_i) * (k_i / k_f)^2 -
    # (k_f - k_i * cos(pol))) * (2 * pi / l_f^2) * dlf/dh
    temp8 = array_manip.mult_ncerr(temp7[0], temp7[1], lam_const, 0.0)

    # k_i * k_f * sin(pol) * (dpol/dh + (dpol/dtd * dtd/dh))
    temp9 = array_manip.mult_ncerr(k_i, z_vec, const2, 0.0)

    # ((k_i - k_f * cos(pol)) * (L_f / L_i) * (k_i / k_f)^2 -
    # (k_f - k_i * cos(pol))) * (2 * pi / l_f^2) * dlf/dh + 
    # k_i * k_f * sin(pol) * (dpol/dh + (dpol/dtd * dtd/dh))
    temp10 = array_manip.add_ncerr(temp8[0], temp8[1], temp9[0], temp9[1])

    # (((k_i - k_f * cos(pol)) * (L_f / L_i) * (k_i / k_f)^2 -
    # (k_f - k_i * cos(pol))) * (2 * pi / l_f^2) * dlf/dh + 
    # k_i * k_f * sin(pol) * (dpol/dh - (dpol/dtd dazi/dh / dazi/dtd))
    return array_manip.div_ncerr(temp10[0], temp10[1], Q, z_vec)

def __calc_x2(*args):
    """
    This function calculates the x2 coeffiecient to the S(Q,E) Jacobian

    @param args: A list of parameters used to calculate the x2 coefficient

    The following is a list of the arguments needed in there expected order
      1. Initial Wavevector
      2. Momentum Transfer
      3. Initial Time-of-Flight
      4. Wavevector Final x Cos(polar)
      5. Time-zero Slope Correction
      6. Vector of Zeros
    @type args: C{list}

    
    @return: The calculated x2 coefficient
    @rtype: (C{nessi_list.NessiList}, C{nessi_list.NessiList})
    """
    # Settle out the arguments to sensible names
    k_i = args[0]
    Q = args[1]
    T_i = args[2]
    k_f_cos_pol = args[3]
    t_0_s_corr = args[4]
    z_vec = args[5]
    
    # k_f * cos(pol) - k_i
    temp1 = array_manip.sub_ncerr(k_f_cos_pol, 0.0, k_i, z_vec)
    # (k_f * cos(pol) - k_i) / Q
    temp2 = array_manip.div_ncerr(temp1[0], temp1[1], Q, z_vec)
    # k_i / T_i
    temp3 = array_manip.div_ncerr(k_i, z_vec, T_i, z_vec)
    # (k_i / T_i) * ((k_f * cos(pol) - k_i) / Q)
    temp4 = array_manip.mult_ncerr(temp2[0], temp2[1], temp3[0], temp3[1])
    # (k_i / T_i) * ((k_f * cos(pol) - k_i) / Q) * 
    # (1 / 1 + ((h / m) * (t0_s / L_i)))
    return array_manip.mult_ncerr(temp4[0], temp4[1], t_0_s_corr, 0.0)

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
      7. Time-zero Slope Correction
      8. Vector of Zeros
    @type args: C{list}

    
    @return: The calculated x3 coefficient
    @rtype: (C{nessi_list.NessiList}, C{nessi_list.NessiList})
    """
    # Settle out the arguments to sensible names
    k_i = args[0]
    E_i = args[1]
    len_ratio = args[2]
    E_f = args[3]
    k_f = args[4]
    lam_const = args[5]
    t_0_s_corr = args[6]
    z_vec = args[7]
    
    # E_f / k_f
    const1 = E_f / k_f
    # (L_f / L_i) * (1 / k_f)^2 * (1 / 1 + ((h / m) * (t0_s / L_i)))
    const2 = (len_ratio * t_0_s_corr) / (k_f * k_f)
    # (4 * pi / l_f^2) * dlf/dh
    const3 = 2.0 * lam_const
    # E_i * k_i
    temp1 = array_manip.mult_ncerr(k_i, z_vec, E_i, z_vec)
    # E_i * k_i * (L_f / L_i) * (1 / k_f)^2
    # * (1 / 1 + ((h / m) * (t0_s / L_i)))
    temp2 = array_manip.mult_ncerr(temp1[0], temp1[1], const2, 0.0)
    # E_i * k_i * (L_f / L_i) * (1 / k_f)^2
    # * (1 / 1 + ((h / m) * (t0_s / L_i)))+ E_f / k_f
    temp3 = array_manip.add_ncerr(temp2[0], temp2[1], const1, 0.0)
    # (4 * pi / l_f^2) * dlf/dh * (E_i * k_i * (L_f / L_i) * (1 / k_f)^2
    # * (1 / 1 + ((h / m) * (t0_s / L_i))) + E_f / k_f)
    return array_manip.mult_ncerr(temp3[0], temp3[1], const3, 0.0)
    
def __calc_x4(*args):
    """
    This function calculates the x4 coeffiecient to the S(Q,E) Jacobian

    @param args: A list of parameters used to calculate the x4 coefficient

    The following is a list of the arguments needed in there expected order
      1. Initial Energy
      2. Initial Time-of-Flight
      3. Time-zero Slope Correction
      4. Vector of Zeros
    @type args: C{list}

    
    @return: The calculated x4 coefficient
    @rtype: (C{nessi_list.NessiList}, C{nessi_list.NessiList}) 
    """
    # Settle out the arguments to sensible names
    E_i = args[0]
    T_i = args[1]
    t_0_s_corr = args[2]
    z_vec = args[3]
    
    # E_i / T_i
    temp1 = array_manip.div_ncerr(E_i, z_vec, T_i, z_vec)
    # -2 * (E_i / T_i)
    temp2 = array_manip.mult_ncerr(temp1[0], temp1[1], -2.0, 0.0)
    # -2 * (E_i / T_i) * (1 / 1 + ((h / m) * (t0_s / L_i)))
    return array_manip.mult_ncerr(temp2[0], temp2[1], t_0_s_corr, 0.0)

