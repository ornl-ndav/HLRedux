#!/usr/bin/env python

import os, sys
import hlr_utils
from   sas_normalize import *

VERSION="0.01"

def getXY(s):
    x=list(s[0].axis[0].val[:-1])        
    y=list(s[0].y[:]            )
    return x,y

def nexusFilePath(archiveDir,proposal,run):
    return "%s/%s/1/%s/NeXus/SANS_%s.nxs"    % (archiveDir,proposal,run,run)


if __name__ == "__main__":
    """TODO: Cleanup this mess below"""
    import optparse
    from   pylab import *
    bragg_edge  = 4.04          # Beryllium Bragg edge - for display purposes
    nexusArchive= "/LENS/SANS"  # LENS NeXus archive directory

    #FIXME: hard-coded axis ranges and binning
    lambda_axis = hlr_utils.Axis(3.00,23.00,0.10,
                                 units='Angstrom',
                                 title='lambda', bintype='lin') # lambda axis [Angstroms]

    q_axis      = hlr_utils.Axis(0.005,0.300,0.10,
                                 units='1/Angstrom',
                                 title='q', bintype='log')      # q axis [1/Angstroms]

    # parse options
    argv0   = os.path.basename(sys.argv[0])
    usage   = "%s [options] <run_number>" % argv0
    version = "%s %s" % (argv0,VERSION)
    opt = optparse.OptionParser(usage=usage,version=version)
    opt.add_option('--time-offset-2d','-d', dest='tof_2d', default=-800,
                   help='set area detector TOF offset, default:-800')
    opt.add_option('--time-offset-bm','-m', dest='tof_bm', default=800,
                   help='set beam monitor detector TOF offset, default:800')
    opt.add_option('--q-plot'  ,'-q', dest='qplot'   , default=False, action='store_true',
                   help='plot q')
    opt.add_option('--mon-eff' ,'-e', dest='mon_eff' , default=False, action='store_true',
                   help='correct for 1/v monitor efficiency')
    opt.add_option('--proposal','-p', dest='proposal', default='2008_01_COM',
                   help='set SANS proposal id, default:2008_01_COM')
    options, arguments = opt.parse_args()
    
    tof_2d  = int(options.tof_2d) # TOF offset for 2D (area detector) 
    tof_bm  = int(options.tof_bm) # TOF offset for BM

    # for now only single run allowed
    if len(arguments)!=1:
        print "%s: exactly one run number required" % argv0
        opt.print_help()
        sys.exit(-1)

    run = arguments[0]
    nexusFile = nexusFilePath(nexusArchive,options.proposal,run)

    print 'NeXus file',nexusFile, 'exists?',os.path.exists(nexusFile)
    print 'l axis:',lambda_axis.toNessiList()
    print 'q axis:',q_axis.toNessiList()
    print 'tof_offset_2d=',tof_2d
    print 'tof_offset_bm=',tof_bm

    # Result of normalize_to_monitor is a tuple (m1,s1,s2)
    # m1 - beam monitor spectrum (wavelength)
    # s1 - area detector spectrum (wavelength, pixel-by-pixel)
    # s2 - normalized area detector spectrum (wavelength, pixel-by-pixel)
    # TODO: add error associated with tof_2d, tof_bm (currently 0.0)
    m1,s1,s2 = normalize_to_monitor(nexusFile,
                                    time_offset_detector=(tof_2d,0.0),
                                    time_offset_monitor =(tof_bm,0.0),
                                    mon_eff=options.mon_eff,
                                    verbose=True, debug=True)
    
    # -------------------------------------------------------------------
    print ctime(),"rebinning beam monitor wavelength spectrum"
    bm = common_lib.rebin_axis_1D(m1,axis_out=lambda_axis.toNessiList()) 
    print ctime(),"summing area detector wavelength spectrum"
    sl = dr_lib.sum_all_spectra(s1,rebin_axis=lambda_axis.toNessiList()) 
    print ctime(),"summing area detector wavelength spectrum (normalized)"
    sn = dr_lib.sum_all_spectra(s2,rebin_axis=lambda_axis.toNessiList()) 
    if options.qplot:
        print ctime(),"converting wavelength to scalar q"
        s3 = common_lib.wavelength_to_scalar_Q(s2) 
        print ctime(),"summing q spectrum"
        sq = dr_lib.sum_all_spectra(s3,rebin_axis=q_axis.toNessiList())
    else:
        sq = None
    
    # -------------------------------------------------------------------
    # lets' plot
    print ctime(),"plotting results"
    
    xm,ym = getXY(bm)
    xs,ys = getXY(sl)
    xn,yn = getXY(sn)
   
    
    f1  = figure(1)
    subplot(311)
    semilogy(xm,ym)
    axvline(bragg_edge)
    ylabel('Intensity (BM)')
    title(os.path.basename(nexusFile))
    
    
    subplot(312)
    semilogy(xs,ys)
    axvline(bragg_edge)
    ylabel('Intensity (2D)')
    
    subplot(313)
    semilogy(xn,yn)
    axvline(bragg_edge)
    xlabel(r'$\lambda$ [$\AA$]')
    ylabel('Intensity (2D/BM)')
    

    if sq:
        xq,yq = getXY(sq)
        f2  = figure(2)
        loglog(xq,yq,'o')
        xlabel(r'q [1/$\AA$]')
        ylabel('Intensity')
        title(os.path.basename(nexusFile))
    
    show()                #
