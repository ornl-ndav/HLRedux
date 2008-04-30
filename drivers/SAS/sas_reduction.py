#!/usr/bin/env python

# $Id$

import os, sys 
import hlr_utils
from   sas_normalize import *
from   sas_utils     import *

VERSION="0.01"

def get_monitor(fileName):
    print ctime(),"reading transmission monitor from %s" % fileName
    fd  = open(fileName, "r")
    a3c = DST.Ascii3ColDST(fd)
    m   = a3c.getSOM()
    a3c.release_resource()
    fd.close()
    return m


def errorlog(ax,s,marker='s'):
    x,y,e = getXYE(s)
    e     = sqrt(array(e))
    for i in xrange(len(e)):
        # TODO: FIXME here
        # At the moment 'clip' the error bar so that is does not go below zero
        if e[i]>=y[i]: 
            e[i]=y[i]
            
    ax.set_xscale('log')
    ax.set_yscale('log')
    errorbar(x,y,yerr=e,marker=marker,fmt=' ')

if __name__ == "__main__":
    """TODO: Cleanup this mess below"""
    import optparse
    from   pylab import *
    bragg_edge  = 4.04          # Beryllium Bragg edge - for display purposes
    vycor_peak  = 0.0171	#

    #FIXME: hard-coded axis ranges and binning
    lambda_axis = hlr_utils.Axis(4.00,20.00,0.20,
                                 units='Angstrom',
                                 title='lambda', bintype='lin') # lambda axis [Angstroms]

    q_axis      = hlr_utils.Axis(0.001,1.0,0.05,
                                 units='1/Angstrom',
                                 title='q', bintype='log')      # q axis [1/Angstroms]

    # parse options
    argv0   = os.path.basename(sys.argv[0])
    usage   = "%s [options] <run_number>" % argv0
    version = "%s %s" % (argv0,VERSION)
    tof_2d  = 1000
    tof_bm  = 1100
    opt = optparse.OptionParser(usage=usage,version=version)
    opt.add_option('--time-offset-2d','-d', dest='tof_2d', default=tof_2d,
                   help='set area detector TOF offset, default:%s' % tof_2d)
    opt.add_option('--time-offset-bm','-m', dest='tof_bm', default=tof_bm,
                   help='set beam monitor  TOF offset, default:%s' % tof_bm)
    opt.add_option('--wavelength-cut','-l', dest='lam_cut', default=None,
                   help='set wavelength cut (lambda_min), default:None')
    opt.add_option('--q-plot'  ,'-q', dest='qplot'   , default=False, action='store_true',
                   help='plot q')
    opt.add_option('--output' ,'-o', dest='output'   , default=None,
                   help='output file, default:None')
    opt.add_option('--roi_file','-r', dest='roi_file', default=None ,
                   help='select roi file')
    opt.add_option('--transmission_file','-t', dest='trans_file', default=None ,
                   help='select transmission file')
    opt.add_option('--mon-eff' ,'-e', dest='mon_eff' , default=False, action='store_true',
                   help='correct for 1/v monitor efficiency')
    opt.add_option('--print'   ,'-p', dest='printfig'   , default=False, action='store_true',
                   help='save figure(s) into *.pdf file(s)')
    opt.add_option('--proposal','-P', dest='proposal', default='2008_01_COM',
                   help='set SANS proposal id, default:2008_01_COM')
    opt.add_option('--archive' ,'-A', dest='archive' , default='/LENS/SANS',
                   help='set SANS archive directory, default=/LENS/SANS')    
   
    options, arguments = opt.parse_args()
    
    tof_2d  = int(options.tof_2d)  # TOF offset for 2D (area detector) 
    tof_bm  = int(options.tof_bm)  # TOF offset for BM

    # for now only single run allowed
    if len(arguments)!=1:
        print "%s: exactly one run number required" % argv0
        opt.print_help()
        sys.exit(-1)

    run = arguments[0]
    nexusFile = nexusFilePath(options.archive,options.proposal,run)

    print 'NeXus file',nexusFile, 'exists?',os.path.exists(nexusFile)
    print 'l axis:',lambda_axis
    print 'q axis:',q_axis
    print 'tof_offset_2d =',tof_2d
    print 'tof_offset_bm =',tof_bm
    print 'wavelength_cut=',options.lam_cut
    print 'out_file=',options.output
    print 'roi_file=',options.roi_file
    print 'transmission_file=',options.trans_file    

    # Result of normalize_to_monitor is a tuple (m1,s1,s2)
    # m1 - beam monitor spectrum (wavelength)
    # s1 - area detector spectrum (wavelength, pixel-by-pixel)
    # s2 - normalized area detector spectrum (wavelength, pixel-by-pixel)
    # TODO: add error associated with tof_2d, tof_bm (currently 0.0)
    m1,s1,s2 = normalize_to_monitor(nexusFile,
                                    time_offset_detector=(tof_2d,0.0),
                                    time_offset_monitor =(tof_bm,0.0),
                                    lam_cut=options.lam_cut,
                                    mon_eff=options.mon_eff,
                                    signal_roi=options.roi_file,
                                    verbose=True, debug=True)
    
    # -------------------------------------------------------------------
    if options.trans_file:
        print ctime(),"reading transmission monitor"
        mt1 = get_monitor(options.trans_file)
        
        print ctime(),"rebinning transmission monitor"
        mt2 = dr_lib.rebin_monitor(mt1, s2)

        print ctime(),"normalizing to transmission monitor"
        #s3 = common_lib.div_ncerr(s2  , mt2)
        s3 = sas_utils.div_ncerr2(s2  , mt2)
    else:
        s3 = s2
    
    if options.qplot:
        print ctime(),"converting wavelength to scalar q"
        s4 = common_lib.wavelength_to_scalar_Q(s3)
               
        print ctime(),"summing q spectrum"
        sq = dr_lib.sum_all_spectra(s4,rebin_axis=q_axis.toNessiList())
        
    else:
        print ctime(),"rebinning beam monitor wavelength spectrum"
        bm = common_lib.rebin_axis_1D(m1,axis_out=lambda_axis.toNessiList()) 

        print ctime(),"summing area detector wavelength spectrum"
        sl = dr_lib.sum_all_spectra(s1,rebin_axis=lambda_axis.toNessiList()) 

        print ctime(),"summing area detector wavelength spectrum (normalized)"
        sq = dr_lib.sum_all_spectra(s3,rebin_axis=lambda_axis.toNessiList()) 

   
    
    # -------------------------------------------------------------------
    # lets' plot
    print ctime(),"plotting results"
    run_title = s2.attr_list['title']
    subtit=''

    if options.qplot:
        subtit='Q'

        ax   = subplot(111)
        errorlog(ax,sq,marker='s')
        #xq,yq,eq = getXYE(sq)
        #eq   = sqrt(array(eq))
        #ax.set_xscale('log')
        #ax.set_yscale('log')
        #errorbar(xq,yq,yerr=eq,marker='s',fmt=' ')

        title("%s: %s" % (os.path.basename(nexusFile),run_title))        
        axvline(vycor_peak)
        xlabel(r'q [1/$\AA$]')
        ylabel('Intensity')

    else:
        subtit='L'
        xm,ym,em = getXYE(bm)
        xs,ys,es = getXYE(sl)
        xq,yq,eq = getXYE(sq)

        em   = sqrt(array(em))
        es   = sqrt(array(es))
        eq   = sqrt(array(eq))
   
        subplot(311)
        title("%s: %s" % (os.path.basename(nexusFile),run_title))        
        #plot(xm,ym,'.')
        errorbar(xm,ym,yerr=em,marker='v',fmt=' ')
        axvline(bragg_edge)
        ylabel('Intensity (BM)')
    
        subplot(312)
        #plot(xs,ys,'o')
        errorbar(xs,ys,yerr=es,marker='^',fmt=' ')
        axvline(bragg_edge)
        ylabel('Intensity (2D)')
        
        subplot(313)
        errorbar(xq,yq,yerr=eq,marker='s',fmt=' ')
        axvline(bragg_edge)
        xlabel(r'$\lambda$ [$\AA$]')
        ylabel('Intensity (2D/BM)')



    outfile='SANS-%s-%s.txt' % (subtit,run)
    if options.output:
        outfile=options.output
        
    hlr_utils.write_file(outfile, "text/Spec", sq,
                         verbose=True,
                         replace_path=False,
                         replace_ext=False,
                         message='Data saved to file %s' % outfile)

    if options.printfig:
        savefig('SANS-%s-%s.pdf' % (subtit,run),format='pdf')

       
    show()                #
