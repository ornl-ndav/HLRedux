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

def calc_EQ_Jacobian(*args):
    """
    This function calculates the Jacobian for S(Q,E) via the following formula

    A = |x_1 * x4 - x_2 * x_3| * dh * dT
    
    @param args: A list of parameters used to calculate the Jacobian

    The following is a list of the arguments needed in there expected order
      1. x_1 coefficient
      2. x_2 coefficient
      3. x_3 coefficient
      4. x_4 coefficient
      5. dT (Time-of-flight bin widths)
      6. dh (Height of detector pixel)
      7. Vector of Zeros
    @type args: C{list}


    @return: The calculated Jacobian
    @rtype: (C{nessi_list.NessiList}, C{nessi_list.NessiList})
    """
    import array_manip

    # Settle out the arguments to sensible names
    x_1 = args[0]
    x_2 = args[1]
    x_3 = args[2]
    x_4 = args[3]
    dT = args[4]
    dh = args[5]
    zero_vec = args[6]
    
    # x_2 * x_3
    x_23 = array_manip.mult_ncerr(x_2, zero_vec, x_3, zero_vec)
    # x_1 * x_4
    x_14 = array_manip.mult_ncerr(x_1, zero_vec, x_4, zero_vec)
    # dh * dT
    dhdT = array_manip.mult_ncerr(dT, zero_vec, dh, 0.0)
    # x_1 * x_4 - x_2 * x_3
    x14_m_x23 = array_manip.sub_ncerr(x_14[0], x_14[1], x_23[0], x_23[1])
    # |x_1 * x_4 - x_2 * x_3|
    abs_x14_m_x23 = (array_manip.abs_val(x14_m_x23[0]), x14_m_x23[1])
    # |x_1 * x_4 - x_2 * x_3| * dh * dT 
    return array_manip.mult_ncerr(dhdT[0], dhdT[1],
                                  abs_x14_m_x23[0], abs_x14_m_x23[1])

def calc_EQ_Jacobian_dgs(*args):
    """
    This function calculates the area of a polygon for use in the application
    of the Jacobian for DGS S(Q,E) data.

    @param args: A list of parameters used to calculate the area

    The following is a list of the arguments needed in their expected order
      1. E_1
      2. Q_1
      3. E_2
      4. Q_2
      5. E_3
      6. Q_3
      7. E_4
      8. Q_4
    @type args: C{list}
    
    
    @return: The polygon areas
    @rtype: (C{nessi_list.NessiList}, C{nessi_list.NessiList})
    """
    import nessi_list
    import utils

    # Settle out the arguments to sensible names
    E1 = args[0]
    Q1 = args[1]
    E2 = args[2]
    Q2 = args[3]
    E3 = args[4]
    Q3 = args[5]
    E4 = args[6]
    Q4 = args[7]

    poly_size = 4

    area = nessi_list.NessiList(len(E1))
    area_err2 = nessi_list.NessiList(len(E1))

    import itertools
    xvals = [xvals for xvals in itertools.izip(E1, E2, E3, E4, E1, E2)]
    yvals = [yvals for yvals in itertools.izip(Q1, Q2, Q3, Q4, Q1, Q2)]
    for x, y, i in itertools.izip(xvals, yvals, itertools.count()):
        xn = nessi_list.NessiList()
        xn.extend(x)
        yn = nessi_list.NessiList()
        yn.extend(y)
        area[i] = utils.calc_area_2D_polygon(xn, yn, poly_size)

    return (area, area_err2)
