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

import nessi_list

def rebin_diagonal(data_1D, data_multiD, *args, **kwargs):
    """
    This function rebins a diagonal 2D spectrum onto another 2D spectrum. The
    diagonal spectrum is created from a 1D spectrum that has 2 correlated axes.
    The component axes for both the original spectrum and rebinned spectrum
    must be specified. Also, the data block for the rebinned 2D spectrum must
    be provided.

    Parameters:
    ----------
    -> data_1D is a NessiList containing the 1D spectrum data
    """
    import bisect

    try:
        dim = kwargs["dim"]
    except KeyError:
        dim = 2

    orig_axes = args[:dim]
    rebin_axes = args[dim:]

    len_orig = []
    for axis in orig_axes:
        len_orig.append(len(axis)-1)

    len_rebin = []
    for axis in rebin_axes:
        len_rebin.append(len(axis)-1)        

    #print "0:",len_orig
    #print "1:",len_rebin

    orig_data_len = len(data_1D[0])

    for k in xrange(len_orig[0]):
        #print "A:",k
        x_orig_lo = orig_axes[0][k]
        x_orig_hi = orig_axes[0][k+1]
        y_orig_lo = orig_axes[1][k]
        y_orig_hi = orig_axes[1][k+1]

        check1 = (x_orig_lo < rebin_axes[0][0] and \
                  x_orig_hi < rebin_axes[0][0])
        check2 = (x_orig_lo > rebin_axes[0][-1] and \
                  x_orig_hi > rebin_axes[0][-1])
        check3 = (y_orig_lo < rebin_axes[1][0] and \
                  y_orig_hi < rebin_axes[1][0]) 
        check4 = (y_orig_lo > rebin_axes[1][-1] and \
                  y_orig_hi > rebin_axes[1][-1])
        
        #print "Q:",check1,check2,check3,check4

        if check1 or check2 or check3 or check4:
            continue

        index1 = bisect.bisect(rebin_axes[0], x_orig_lo)
        index2 = bisect.bisect(rebin_axes[0], x_orig_hi)
        index3 = bisect.bisect(rebin_axes[1], y_orig_lo)
        index4 = bisect.bisect(rebin_axes[1], y_orig_hi)
        index5 = bisect.bisect_left(rebin_axes[0], x_orig_lo)
        index6 = bisect.bisect_left(rebin_axes[0], x_orig_hi)
        index7 = bisect.bisect_left(rebin_axes[1], y_orig_lo)
        index8 = bisect.bisect_left(rebin_axes[1], y_orig_hi)

        #print "B0:",index1,index2,index3,index4,index5,index6,index7,index8
        
        index_x_left = __fix_index(max(index1, index5)-1, len_rebin[0])
        index_x_right = __fix_index(min(index2, index6), len_rebin[0])
        index_y_left = __fix_index(max(index3, index7)-1, len_rebin[1])
        index_y_right = __fix_index(min(index4, index8), len_rebin[1])

        #print "B1:",index_x_left,index_x_right,index_y_left,index_y_right

        if index_x_left == -1 or index_y_left == -1:
            continue

        #print "0X:",x_orig_lo,x_orig_hi
        #print "0Y:",y_orig_lo,y_orig_hi

        dx_orig = x_orig_hi - x_orig_lo
        dy_orig = y_orig_hi - y_orig_lo

        #for i in xrange(len_rebin[0]):
        for i in xrange(index_x_left, index_x_right):
            #print "C:",i
            x_rebin_lo = rebin_axes[0][i]
            x_rebin_hi = rebin_axes[0][i+1]
            #print "1X:",x_rebin_lo,x_rebin_hi

            #for j in xrange(len_rebin[1]):
            for j in xrange(index_y_left, index_y_right):
                #print "D:",j
                y_rebin_lo = rebin_axes[1][j]
                y_rebin_hi = rebin_axes[1][j+1]
                #print "1Y:",y_rebin_lo,y_rebin_hi

                #print "E:",k,i,j                
                delta_x = min(x_orig_hi,x_rebin_hi) - max(x_orig_lo,x_rebin_lo)
                delta_y = min(y_orig_hi,y_rebin_hi) - max(y_orig_lo,y_rebin_lo)

                #print "F:",delta_x,delta_y
                
                delta = delta_x * delta_y
                width = dx_orig * dy_orig

                #print "G:",delta,width
                portion = delta / width

                #print "H:",portion
                channel = j + i * len_rebin[1]

                #print "I:",channel
                data_multiD[0][channel] += data_1D[0][k] * portion
                data_multiD[1][channel] += data_1D[1][k] * portion * portion

                #print "J:",data_1D[0][k],data_multiD[0][channel]
                

    return data_multiD

def __fix_index(index, end_index):
    if index == -1:
        return 0
    elif index == end_index+1:
        return index-1
    else:
        return index

if __name__ == "__main__":

    data1 = nessi_list.NessiList()
    data1.extend(10,10,10,10)

    data2 = nessi_list.NessiList()
    data2.extend(20,20,20,20)

    err2 = nessi_list.NessiList()
    err2.extend(1,1,1,1)

    x0 = nessi_list.NessiList()
    x0.extend(0,1,2,3,4)
    y0 = nessi_list.NessiList()
    y0.extend(0,1,2,3,4)

    x1_1 = nessi_list.NessiList()
    x1_1.extend(0,1.3333,2.666666,4)

    x1_2 = nessi_list.NessiList()
    x1_2.extend(1.25,2.25,3.25)

    y1_1 = nessi_list.NessiList()
    y1_1.extend(0,2,4)

    y1_2 = nessi_list.NessiList()
    y1_2.extend(0,1.3333,2.666666,4)

    y1_3 = nessi_list.NessiList()
    y1_3.extend(0.75,1.25,1.75,2.25,2.75,3.25)

    data_mulD_1 = nessi_list.NessiList((len(x1_1)-1)*(len(y1_1)-1))
    err2_mulD_1 = nessi_list.NessiList((len(x1_1)-1)*(len(y1_1)-1))

    data_mulD_2 = nessi_list.NessiList((len(x1_1)-1)*(len(y1_2)-1))
    err2_mulD_2 = nessi_list.NessiList((len(x1_1)-1)*(len(y1_2)-1))

    data_mulD_3 = nessi_list.NessiList((len(x1_2)-1)*(len(y1_3)-1))
    err2_mulD_3 = nessi_list.NessiList((len(x1_2)-1)*(len(y1_3)-1))    

    print "*****************"
    print "* rebin_diagonal:", rebin_diagonal((data1, err2),
                                              (data_mulD_1, err2_mulD_1),
                                              x0, y0, x1_1, y1_1)
    
    print "* rebin_diagonal:", rebin_diagonal((data1, err2),
                                              (data_mulD_2, err2_mulD_2),
                                              x0, y0, x1_1, y1_2)
    
    print "* rebin_diagonal:", rebin_diagonal((data2, err2),
                                              (data_mulD_3, err2_mulD_3),
                                              x0, y0, x1_2, y1_3)
