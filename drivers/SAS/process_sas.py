#!/usr/bin/env python

import os, sys, math
from   time import ctime
import DST
import nessi_list
import common_lib
import dr_lib
import hlr_utils
import logging
from   pylab import *


smallfloat =1e-1
file_name  = sys.argv[1]
so_axis    = "time_of_flight"
data_bank  = "/entry/bank1,1"
bmon_bank  = "/entry/monitor1,1"

def getXY(s):
    x=list(s[0].axis[0].val[:-1])        
    y=list(s[0].y[:]            )
    return x,y

def process_sas(fileName,axis,t0_d,t0_m):
    print ctime(),'runHLR:',os.path.basename(fileName)
    config            = hlr_utils.Configure()
    config.data       = fileName
    config.data_paths = hlr_utils.create_data_paths(data_bank)
    config.bmon_path  = hlr_utils.create_data_paths(bmon_bank)
    data_dst   = DST.getInstance("application/x-NeXus", config.data)
    # ------------------------------------
    print ctime(),"runHLR: getting spectrum object ..."
    s1 = data_dst.getSOM(config.data_paths, so_axis)
    m1 = data_dst.getSOM(config.bmon_path , so_axis)
    # ------------------------------------
    print ctime(),"runHLR: fixing bin contents ..."
    s2 = dr_lib.fix_bin_contents(s1)
    m2 = dr_lib.fix_bin_contents(m1)
    # ------------------------------------
    print ctime(),"runHLR: converting to scalar wavelength ..."
    s3 = common_lib.tof_to_wavelength_lin_time_zero(s2,units="microsecond",
                                                    time_zero_offset=t0_d,
                                                    inst_param='total'  )
    m3 = common_lib.tof_to_wavelength_lin_time_zero(m2,units="microsecond",
                                                    time_zero_offset=t0_m,
                                                    inst_param='primary')

    lambda_min = ( 4.0,0.0)
    lambda_max = (20.0,0.0)

    # ------------------------------------
    print ctime(),"runHLR: correcting for monitor efficiency ..."
    m4 = dr_lib.feff_correct_mon(m3)
    # ------------------------------------
    print ctime(),"runHLR: making dimensionless monitor  ..."
    m5 = dr_lib.dimensionless_mon(m4, lambda_min, lambda_max)
    # ------------------------------------
    print ctime(),"runHLR: rebinning bmon ..."
    m6 = dr_lib.rebin_monitor(m5, s3)
    # ------------------------------------
    #print ctime(),"runHLR: normalizing ..."
    s4 = common_lib.div_ncerr(s3,m6)
    # ------------------------------------
    print ctime(),"runHLR: summing ..."
    sa = dr_lib.sum_all_spectra(s3,rebin_axis=axis.toNessiList())
    sb = dr_lib.sum_all_spectra(s4,rebin_axis=axis.toNessiList())
    m  = common_lib.rebin_axis_1D(m5,axis_out=axis.toNessiList())
    #
    # ------------------------------------
    print ctime(),"runHLR: done"
    return sa,sb,m

if __name__ == "__main__":
    run = sys.argv[1]
    nexusDir ="/LENS/SANS/2008_01_COM/1"
    nexusFile="%s/%s/NeXus/SANS_%s.nxs"              % (nexusDir,run,run)

    axis=hlr_utils.Axis(3.00,20.00,0.02,units='Angstrom',title='lambda',bintype='lin')
    bins=array(list(axis.toNessiList()))
    print axis.toNessiList()
    print nexusFile, os.path.exists(nexusFile)

    sa,sb,m = process_sas(nexusFile,axis,t0_d=(0.0,1.0),t0_m=(0.0,1.0))

    f  = figure()

    xs,ys = getXY(sa)
    xm,ym = getXY(m)

    subplot(311)
    semilogy(xs,ys)
    
    subplot(312)
    semilogy(xm,ym)
    
    subplot(313)
    xn,yn = getXY(sb)
    semilogy(xn,yn)

    show()                #
