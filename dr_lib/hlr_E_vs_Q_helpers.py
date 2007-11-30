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

def rebin_EQ(counts, counts_err2, Q_rebin, E_rebin, counts_2D, counts_2D_err2,
             area, area_err2, *args):
    """
    This function rebins a given spectrum onto the new E and Q axes.

    @param counts: The array holding the spectrum's neutron counts
    @type counts: C{nessi_list.NessiList}

    @param counts_err2: The array holding the spectrum's error^2 on the
                        neutron counts
    @type counts_err2: C{nessi_list.NessiList}

    @param Q_rebin: The new momentum transfer axis
    @type Q_rebin: C{nessi_list.NessiList}

    @param E_rebin: The new energy transfer axis
    @type E_rebin: C{nessi_list.NessiList}

    @param counts_2D: The counts array associated with the new energy transfer
                      and momentum transfer axes.
    @type counts_2D: C{nessi_list.NessiList}

    @param counts_2D_err2: The error^2 array associated with the new energy
                           transfer and momentum transfer axes.
    @type counts_2D_err2: C{nessi_list.NessiList}

    @param area: The array for holding the fractional areas from the bin
    intersections. This array is the same size as counts_2D.
    @type area: C{nessi_list.NessiList}

    @param area_err2: The array for holding the error^2 on the fractional
                      areas from the bin intersections. This array is the same
                      size as counts_2D_err2.
    @type area_err2: C{nessi_list.NessiList}

    @param args: The list of S(Q,E) bin vertex coordinates

    The following is a list of the arguments needed in there expected order
      1. Q_1 
      2. E_1
      3. Q_2
      4. E_2
      5. Q_3
      6. E_3
      7. Q_4
      8. E_4
    @type args: C{tuple}s of two C{nessi_list.NessiList}s
    """
    import bisect

    import hlr_utils
    import nessi_list
    import utils
    
    # Settle out the arguments to sensible names
    Q_1 = args[0][0]
    E_1 = args[0][1]
    Q_2 = args[1][0]
    E_2 = args[1][1]
    Q_3 = args[2][0]
    E_3 = args[2][1]
    Q_4 = args[3][0]
    E_4 = args[3][1]    

    #print "D:", E_rebin, Q_rebin

    # Setup some placeholder arrays
    orig_bin_x = nessi_list.NessiList(4)
    orig_bin_y = nessi_list.NessiList(4)
    
    rebin_bin_x = nessi_list.NessiList(4)
    rebin_bin_y = nessi_list.NessiList(4)

    # Setup some repeatedly used lengths
    len_Q_rebin = len(Q_rebin)
    len_E_rebin = len(E_rebin)
    rebin_counts_len = len_E_rebin - 1
    arr_len = len(Q_1)

    for i in xrange(arr_len):
        
        #print "C:", Q_1[i], E_1[i], Q_2[i], E_2[i], Q_3[i], E_3[i],\
        #      Q_4[i], E_4[i]

        Q_min = min(Q_1[i], Q_2[i], Q_3[i], Q_4[i])
        Q_max = max(Q_1[i], Q_2[i], Q_3[i], Q_4[i])

        E_min = min(E_1[i], E_2[i], E_3[i], E_4[i])
        E_max = max(E_1[i], E_2[i], E_3[i], E_4[i])        

        #print "C:", Q_min, Q_max, E_min, E_max

        check1 = (E_min < E_rebin[0] and E_max < E_rebin[0])
        check2 = (E_min > E_rebin[-1] and E_max > E_rebin[-1])
        check3 = (Q_min < Q_rebin[0] and Q_max < Q_rebin[0])
        check4 = (Q_min > Q_rebin[-1] and Q_max > Q_rebin[-1])

        # If the bin is outside the grid range, no need to continue
        if check1 or check2 or check3 or check4:
            continue

        #print "After making checks"

        orig_bin_x[0] = Q_1[i]
        orig_bin_x[1] = Q_2[i]
        orig_bin_x[2] = Q_3[i]
        orig_bin_x[3] = Q_4[i]        

        orig_bin_y[0] = E_1[i]
        orig_bin_y[1] = E_2[i]
        orig_bin_y[2] = E_3[i]
        orig_bin_y[3] = E_4[i]

        #print "Using bisectors"

        x_min = utils.bisect_helper(Q_rebin, Q_min)
        x_max = utils.bisect_helper(Q_rebin, Q_max)
        
        y_min = utils.bisect_helper(E_rebin, E_min)
        y_max = utils.bisect_helper(E_rebin, E_max)
        """

        index1 = bisect.bisect(Q_rebin, Q_min)
        index2 = bisect.bisect(Q_rebin, Q_max)
        index3 = bisect.bisect_left(Q_rebin, Q_min)
        index4 = bisect.bisect_left(Q_rebin, Q_max)        
        
        index5 = bisect.bisect(E_rebin, E_min)
        index6 = bisect.bisect(E_rebin, E_max)
        index7 = bisect.bisect_left(E_rebin, E_min)
        index8 = bisect.bisect_left(E_rebin, E_max)

        x_min = hlr_utils.fix_index(max(index1, index3) - 1, len_Q_rebin - 1)
        x_max = hlr_utils.fix_index(max(index2, index4) - 1, len_Q_rebin - 1)

        y_min = hlr_utils.fix_index(max(index5, index7) - 1, len_E_rebin - 1)
        y_max = hlr_utils.fix_index(max(index6, index8) - 1, len_E_rebin - 1)
        """        
        #print "B:", i, (x_min, x_max), (y_min, y_max)

        for j in xrange(x_min, x_max+1):

            for k in xrange(y_min, y_max+1):

                #print "E:", (j, k)

                rebin_bin_x[0] = Q_rebin[j]
                rebin_bin_x[1] = Q_rebin[j]
                rebin_bin_x[2] = Q_rebin[j+1]
                rebin_bin_x[3] = Q_rebin[j+1]                

                rebin_bin_y[0] = E_rebin[k]
                rebin_bin_y[1] = E_rebin[k+1]
                rebin_bin_y[2] = E_rebin[k+1]
                rebin_bin_y[3] = E_rebin[k]                

                #print "Gx:", rebin_bin_x
                #print "Gy:", rebin_bin_y
         
                #print "F: Finding intersection"
                (frac_bin_x,
                 frac_bin_y) = utils.convex_polygon_intersect(orig_bin_x,
                                                              orig_bin_y,
                                                              rebin_bin_x,
                                                              rebin_bin_y)

                len_poly = len(frac_bin_x)
                #print "K:", len_poly
                if len_poly < 3:
                    continue
                #print "Got here"

                #print "QQx:", frac_bin_x
                #print "QQy:", frac_bin_y

                frac_bin_x.append(frac_bin_x[0])
                frac_bin_x.append(frac_bin_x[1])

                frac_bin_y.append(frac_bin_y[0])
                frac_bin_y.append(frac_bin_y[1])                

                #print "QQQx:", frac_bin_x
                #print "QQQy:", frac_bin_y

                #print "G: Finding intersection area"

                frac_area = utils.calc_area_2D_polygon(frac_bin_x, frac_bin_y,
                                                       len_poly)
                
                channel = k + j * rebin_counts_len

                #print "H:", channel, frac_area

                counts_2D[channel] += (frac_area * counts[i])
                counts_2D_err2[channel] += (frac_area * frac_area \
                                            * counts_err2[i])
                area[channel] += frac_area

