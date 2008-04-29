#!/usr/bin/env python

# $Id$

import os, sys
import hlr_utils
from   sas_normalize import *
from   sas_utils     import *

VERSION="0.01"


if __name__ == "__main__":
    """TODO: Cleanup this mess below"""
    import optparse
    from   pylab import *
    bragg_edge  = 4.04          # Beryllium Bragg edge - for display purposes
    vycor_peak  = 0.0171	#

    #FIXME: hard-coded axis ranges and binning
    lambda_axis = hlr_utils.Axis(4.00,20.00,0.10,
                                 units='Angstrom',
                                 title='lambda', bintype='lin') # lambda axis [Angstroms]

    q_axis      = hlr_utils.Axis(0.001,1.0,0.01,
                                 units='1/Angstrom',
                                 title='q', bintype='log')      # q axis [1/Angstroms]

    # parse options
    argv0   = os.path.basename(sys.argv[0])
    usage   = "%s [options] <nexus_file>" % argv0
    version = "%s %s" % (argv0,VERSION)
    tof_2d  = 0
    tof_bm  = 0
    opt = optparse.OptionParser(usage=usage,version=version)
    opt.add_option('--time-offset-2d','-d', dest='tof_2d', default=tof_2d,
                   help='set area detector TOF offset, default:%s' % tof_2d)
    opt.add_option('--time-offset-bm','-m', dest='tof_bm', default=tof_bm,
                   help='set beam monitor  TOF offset, default:%s' % tof_bm)
    opt.add_option('--normalize','-n', dest='normalize' , default=False, action='store_true',
                   help='do normalize to beam monitor')
    opt.add_option('--q-plot'   ,'-q', dest='qplot'     , default=False, action='store_true',
                   help='plot q')
    options, arguments = opt.parse_args()
    
    tof_2d  = int(options.tof_2d)  # TOF offset for 2D (area detector) 
    tof_bm  = int(options.tof_bm)  # TOF offset for BM

    # for now only single run allowed
    if len(arguments)!=1:
        print "%s: exactly one run number required" % argv0
        opt.print_help()
        sys.exit(-1)

    nexusFile = arguments[0]

    print 'NeXus file',nexusFile, 'exists?',os.path.exists(nexusFile)
    print 'l axis:',lambda_axis
    print 'q axis:',q_axis
    print 'tof_offset_2d =',tof_2d
    print 'tof_offset_bm =',tof_bm

    # Result of normalize_to_monitor is a tuple (m1,s1,s2)
    # m1 - beam monitor spectrum (wavelength)
    # s1 - area detector spectrum (wavelength, pixel-by-pixel)
    # s2 - normalized area detector spectrum (wavelength, pixel-by-pixel)
    # TODO: add error associated with tof_2d, tof_bm (currently 0.0)
    m1,s1,s2 = normalize_to_monitor(nexusFile,
                                    time_offset_detector=(tof_2d,0.0),
                                    time_offset_monitor =(tof_bm,0.0),
                                    verbose=True, debug=True,
                                    normalize=options.normalize)

    
    # -------------------------------------------------------------------
    if options.qplot:
        print ctime(),"converting wavelength to scalar q"
        s4 = common_lib.wavelength_to_scalar_Q(s2)

        print ctime(),"summing q spectrum"
        sq = dr_lib.sum_all_spectra(s4,rebin_axis=q_axis.toNessiList())
        
    else:
        print ctime(),"rebinning beam monitor wavelength spectrum"
        bm = common_lib.rebin_axis_1D(m1,axis_out=lambda_axis.toNessiList()) 

        print ctime(),"summing area detector wavelength spectrum"
        sl = dr_lib.sum_all_spectra(s1,rebin_axis=lambda_axis.toNessiList()) 

        print ctime(),"summing area detector wavelength spectrum (normalized)"
        sq = dr_lib.sum_all_spectra(s2,rebin_axis=lambda_axis.toNessiList()) 

   
    
    # -------------------------------------------------------------------
    # lets' plot
    print ctime(),"plotting results"
    run_title = s2.attr_list['title']
    run       = s2.attr_list['run_number']
    subtit=''

    if options.qplot:
        subtit='Q'
        xq,yq,eq = getXYE(sq,cleanup=True)
        #xq,yq = getXY(sq)

        subplot(111)
        title("%s: %s" % (os.path.basename(nexusFile),run_title))        
        semilogy(xq,yq,'s')
        #plot(xq,yq,'s')
        #axvline(vycor_peak)
        xlabel(r'q [1/$\AA$]')
        ylabel('Intensity')

    else:
        subtit='L'
        xm,ym = getXY(bm)
        xs,ys = getXY(sl)
        xq,yq = getXY(sq)
   
        subplot(311)
        title("%s: %s" % (os.path.basename(nexusFile),run_title))        
        plot(xm,ym,'.')
        axvline(bragg_edge)
        ylabel('Intensity (BM)')
    
        subplot(312)
        plot(xs,ys,'.')
        axvline(bragg_edge)
        ylabel('Intensity (2D)')
        
        subplot(313)
        plot(xq,yq,'.')
        axvline(bragg_edge)
        xlabel(r'$\lambda$ [$\AA$]')
        ylabel('Intensity (2D/BM)')

       
    show()                #
