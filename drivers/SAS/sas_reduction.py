#!/usr/bin/env python

import os, sys
import hlr_utils
from   sas_normalize import *

def getXY(s):
    x=list(s[0].axis[0].val[:-1])        
    y=list(s[0].y[:]            )
    return x,y

def nexusFilePath(topDir,run):
    return "%s/%s/NeXus/SANS_%s.nxs"    % (topDir,run,run)


if __name__ == "__main__":
    """TODO: Cleanup this mess below"""
    from   pylab import *

    bragg_edge = 4.04                      # Beryllium Bragg edge - for display purposes
    nexusDir   ="/LENS/SANS/2008_01_COM/1" # where to find nexus files
    run_num    =  48                       # run number
    tof_2d     = -800.0                    # TOF offset for 2D 
    tof_bm     =  800.0                    # TOF offset for BM
    lambda_min =    4.0                    # min wavelength for BM normalization
    lambda_max =   20.0                    # max wavelength for BM normalization
    

    lambda_axis = hlr_utils.Axis(3.00,23.00,0.10,
                                 units='Angstrom',
                                 title='lambda', bintype='lin') # lambda axis [Angstroms]

    q_axis      = hlr_utils.Axis(0.005,0.300,0.10,
                                 units='1/Angstrom',
                                 title='q', bintype='log')      # q axis [1/Angstroms]

    if len(sys.argv)>1: run_num = sys.argv[1]             
    if len(sys.argv)>2: tof_2d  = int(sys.argv[2])
    if len(sys.argv)>3: tof_bm  = int(sys.argv[3])

    nexusFile = nexusFilePath(nexusDir,run_num)

    print 'Arguments: ',sys.argv
    print len(lambda_axis.toNessiList()),lambda_axis.toNessiList()
    print len(q_axis.toNessiList()),q_axis.toNessiList()
    print nexusFile, os.path.exists(nexusFile)

    
    # m1 - beam monitor spectrum (wavelength)
    # s1 - 'raw' area detector spectrum (wavelength, pixel-by-pixel)
    # s2 - normalized area detector spectrum (wavelength, pixel-by-pixel)
    m1,s1,s2 = normalize_to_monitor(nexusFile,
                                    time_offset_detector=(tof_2d,0.0),
                                    time_offset_monitor =(tof_bm,0.0),
                                    lambda_min=(lambda_min,0.0),
                                    lambda_max=(lambda_max,0.0))

    # -------------------------------------------------------------------
    print ctime(),"summing beam monitor ..."
    bm = common_lib.rebin_axis_1D(m1,axis_out=lambda_axis.toNessiList()) # summed BM wavelength spectrum
    print ctime(),"summing area detector ..."
    sl = dr_lib.sum_all_spectra(s1,rebin_axis=lambda_axis.toNessiList()) # summed 2D wavelength spectrum
    print ctime(),"summing area detector (normalized)..."
    sn = dr_lib.sum_all_spectra(s2,rebin_axis=lambda_axis.toNessiList()) # summed 2D wavelength normalized spec
    print ctime(),"converting to scalar q..."
    s3 = common_lib.wavelength_to_scalar_Q(s2) 
    print ctime(),"summing q spectrum ..."
    sq = dr_lib.sum_all_spectra(s3,rebin_axis=q_axis.toNessiList())
    


    # -------------------------------------------------------------------
    # lets' plot
    print ctime(),"plotting ..."


    xm,ym = getXY(bm)
    xs,ys = getXY(sl)
    xn,yn = getXY(sn)
    xq,yq = getXY(sq)

    f1  = figure(1)
    subplot(311)
    semilogy(xm,ym)
    axvline(bragg_edge)
    ylabel('Intensity BM')
    title(os.path.basename(nexusFile))

    
    subplot(312)
    semilogy(xs,ys)
    axvline(bragg_edge)
    ylabel('Intensity Area')
    
    subplot(313)
    semilogy(xn,yn)
    axvline(bragg_edge)
    xlabel(r'$\lambda$ [$\AA$]')
    ylabel('Intensity Area/BM')


    f2  = figure(2)
    loglog(xq,yq,'o')
    xlabel(r'q [1/$\AA$]')
    ylabel('Intensity')
    title(os.path.basename(nexusFile))

    show()                #
