#!/usr/bin/env python

# $Id$

import os, sys
from   time          import ctime, time
import hlr_utils
from   sas_normalize import *
from   sas_utils     import *

VERSION="0.1"



if __name__ == "__main__":
    """TODO: Cleanup this mess below"""
    import optparse
    from   pylab import *
    bragg_edge   = 4.044          # Beryllium Bragg edge - for display purposes

    l_axis = hlr_utils.Axis(2.00,22.00,0.20,
                                 units='Angstrom',
                                 title='lambda', bintype='lin') # lambda axis [Angstroms]

    q_axis = hlr_utils.Axis(0.001,1.0,0.10,
                                 units='1/Angstrom',
                                 title='q', bintype='log')      # q axis [1/Angstroms]

    # parse options
    argv0   = os.path.basename(sys.argv[0])
    usage   = "%s [options] <runS> [<runB>]" % argv0
    version = "%s %s" % (argv0,VERSION)
    tof_2d  = 500 # 1000
    tof_bm  = 500 # 1100
    opt = optparse.OptionParser(usage=usage,version=version)
    opt.add_option('--time-offset-2d','-d', dest='tof_2d', default=tof_2d,
                   help='set area detector TOF offset, default:%s' % tof_2d)
    opt.add_option('--time-offset-bm','-m', dest='tof_bm', default=tof_bm,
                   help='set beam monitor  TOF offset, default:%s' % tof_bm)
    opt.add_option('--wavelength-cut','-l', dest='lam_cut', default=None,
                   help='set wavelength cut (lambda_min), default:None')
    opt.add_option('--background-coefficients','-B', dest='bg_coeff', default=None,
                   help='set background-subtraction coefficients ')

    opt.add_option('--lambda-bins', dest='l_bins', default=None,
                   help="""Specify the minimum and maximum wavelength values and
                   the wavelength bin width in Angstroms""")
    
    opt.add_option('--q-bins', dest='q_bins', default=None,
                   help="""Specify the minimum and maximum momentum transfer
                   values, the momentum transfer bin width in
                   Angstroms^-1 and the type (lin or log)""")

    opt.add_option('--roi-file','-r', dest='roi_file', default=None ,
                   help='select roi file')
    opt.add_option('--transmission-file','-t', dest='trans_file', default=None ,
                   help='select transmission file')

    opt.add_option('--acceptance-file','-a', dest='qacc_file', default=None ,
                   help='select q acceptance file')
    
    opt.add_option('--monitor-eff','-e', dest='mon_eff' , default=False, action='store_true',
                   help='correct for 1/v monitor efficiency')

    opt.add_option('--q-plot'  ,'-q', dest='qplot'   , default=False, action='store_true',
                   help='plot I(q) instead of I(lambda)')
    

    opt.add_option('--output' ,'-o', dest='output'   , default=None,
                   help='output file, default:SANS-<X>-<RUN>.txt')
    opt.add_option('--print'   ,'-p', dest='printfig'   , default=False, action='store_true',
                   help='save figure(s) into *.pdf file(s)')
    opt.add_option('--no-display','-n', dest='display'  , default=True , action='store_false',
                   help='do not display figures')
    opt.add_option('--logscale','-L', dest='logscale'   , default=False, action='store_true',
                   help='plot using logarithmic scale')

    opt.add_option('--proposal','-P', dest='proposal', default='2008_01_COM',
                   help='set SANS proposal id, default:2008_01_COM')
    opt.add_option('--archive' ,'-A', dest='archive' , default='/LENS/SANS',
                   help='set SANS archive directory, default=/LENS/SANS')    

    opt.add_option('--debug', dest='debug'   , default=False, action='store_true',
                   help='turn on debugging')
    options, arguments = opt.parse_args()

   

    
    tof_2d  = int(options.tof_2d)  # TOF offset for 2D (area detector) 
    tof_bm  = int(options.tof_bm)  # TOF offset for BM

    # for now only single run allowed
    if len(arguments)<1:
        print '*** ERROR *** ',
        print "%s: at least one run number required" % argv0
        sys.exit(-1)
    if len(arguments)>2:
        print '*** ERROR ***  ',
        print "%s: at most two run numbers allowed" % argv0
        sys.exit(-1)

    if options.debug:
        sas_utils.debug=True
        sas_utils.logfile="debug-%s.log" % arguments[0]


    runS = arguments[0]
    nexusFileS = nexusFilePath(options.archive,options.proposal,runS)
    if not os.path.exists(nexusFileS):
        print '*** ERROR *** ',
        print 'file',nexusFileS,'does not exist'
        sys.exit(-1)

    runB       = None
    nexusFileB = None
    
    if len(arguments)>1 :
        runB       = arguments[1]
        nexusFileB = nexusFilePath(options.archive,options.proposal,runB)
        if not os.path.exists(nexusFileB):
            print '*** ERROR *** ',
            print 'file',nexusFileB,'does not exist'
            sys.exit(-1)

    if options.l_bins is not None:
        l_axis = hlr_utils.AxisFromString(options.l_bins)

    if options.q_bins is not None:
        q_axis = hlr_utils.AxisFromString(options.q_bins)

    subtit=''
    if options.trans_file: subtit += 'T'
    if options.qplot:
        subtit += 'Q'
    else:
        subtit += 'L'
    if runB:
        subtit += 'B'
    if options.qacc_file:
        subtit += 'A'

    outfile='SANS-%s-%s.txt' % (subtit,runS)
    prnfile='SANS-%s-%s.pdf' % (subtit,runS)
    if options.output:
        outfile=options.output
        prnfile=options.output+'.pdf'

    t0 = time()
    print ctime(),argv0,"start"
    print '  Signal    :', nexusFileS
    print '  Background:', nexusFileB
    if options.qplot:
        print '  Q:',q_axis
    else:
        print '  L:',l_axis
    print '  TOF Offset 2D ='   , tof_2d, 'usec'
    print '  TOF Offset BM ='   , tof_bm, 'usec'
    print '  Wavelength Cut='   , options.lam_cut,'Angstroms'
    print '  Background Coeff=',  options.bg_coeff
    print '  ROI file='         , options.roi_file
    print '  Transmission File=', options.trans_file
    print '  Q-Acceptance File=', options.qacc_file
    print '  Out File='         , outfile

    # Result of normalize_to_monitor is a tuple (m1,s1,s2)
    # m1 - beam monitor spectrum (wavelength)
    # s1 - area detector spectrum (wavelength, pixel-by-pixel)
    # s2 - normalized area detector spectrum (wavelength, pixel-by-pixel)
    # TODO: add error associated with tof_2d, tof_bm (currently 0.0)
    m1,s1,s2 = normalize_to_monitor(nexusFileS,
                                    time_offset_detector=(tof_2d,0.0),
                                    time_offset_monitor =(tof_bm,0.0),
                                    lam_cut=options.lam_cut,
                                    bg_coeff=options.bg_coeff,
                                    mon_eff=options.mon_eff,
                                    signal_roi=options.roi_file,
                                    verbose=True, debug=True)

    if runB:
        b2 = normalize_to_monitor(nexusFileB,
                                  time_offset_detector=(tof_2d,0.0),
                                  time_offset_monitor =(tof_bm,0.0),
                                  lam_cut=options.lam_cut,
                                  mon_eff=options.mon_eff,
                                  signal_roi=options.roi_file,
                                  verbose=True)
    else:
        b2 = None
    
    
    run_title = s2.attr_list['title']

    # -------------------------------------------------------------------
    if b2:
        print ctime(),"subtracting background"
        s3 = common_lib.sub_ncerr(s2,b2)
    else:
        s3 = s2

    
    if options.trans_file:
        print ctime(),"reading transmission monitor"
        t1 = get_monitor(options.trans_file)
        
        print ctime(),"rebinning transmission monitor"
        t2 = dr_lib.rebin_monitor(t1, s3)

        print ctime(),"normalizing to transmission monitor"
        s4 = sas_utils.div_ncerr2(s3  , t2)
    else:
        s4 = s3


    if options.qplot:
        print ctime(),"converting wavelength to scalar q"
        s5 = common_lib.wavelength_to_scalar_Q(s4)

        print ctime(),"summing q spectrum"
        s6 = dr_lib.sum_all_spectra(s5,rebin_axis=q_axis.toNessiList())

        if options.qacc_file:
            print ctime(),"getting q acceptance spectrum"
            ta = get_monitor(options.qacc_file)
            print ctime(),"normalizing to q acceptance spectrum"
            sq = sas_utils.div_ncerr2(s6  , ta)
        else:
            sq = s6
        
        
    else:
        print ctime(),"rebinning beam monitor wavelength spectrum"
        bm = common_lib.rebin_axis_1D(m1,axis_out=l_axis.toNessiList()) 

        print ctime(),"summing area detector wavelength spectrum"
        sl = dr_lib.sum_all_spectra(s1,rebin_axis=l_axis.toNessiList()) 

        print ctime(),"summing area detector wavelength spectrum (normalized)"
        sq = dr_lib.sum_all_spectra(s4,rebin_axis=l_axis.toNessiList()) 

   
    
    # -------------------------------------------------------------------
    # lets' plot
    print ctime(),"plotting results"
    
    hlr_utils.write_file(outfile, "text/Spec", sq,
                         verbose=True,
                         replace_path=False,
                         replace_ext=False,
                         message='Data saved to file %s' % outfile)

    if options.qplot:
        ax   = subplot(111)
        errorplot(ax,sq,marker='s',logxscale=options.logscale,logyscale=options.logscale)
        title("%s: %s" % (os.path.basename(nexusFileS),run_title))        
        xlabel(r'q [1/$\AA$]')
        ylabel('Intensity')

    else:
        xm,ym,em = getXYE(bm)
        xs,ys,es = getXYE(sl)
        xq,yq,eq = getXYE(sq)

        em   = sqrt(array(em))
        es   = sqrt(array(es))
        eq   = sqrt(array(eq))
   
        ax = subplot(311)
        errorplot(ax,bm,marker='^',logyscale=options.logscale)
        title("%s: %s" % (os.path.basename(nexusFileS),run_title))        
        if options.logscale: ax.set_yscale('log')
        axvline(bragg_edge)
        ylabel('Intensity (BM)')
    
        ax = subplot(312)
        errorplot(ax,sl,marker='v',logyscale=options.logscale)
        #errorbar(xs,ys,yerr=es,marker='v',fmt='-')
        axvline(bragg_edge)
        ylabel('Intensity (2D)')
        
        ax = subplot(313)
        errorplot(ax,sq,marker='s')
        #errorbar(xq,yq,yerr=eq,marker='s',fmt=' ')
        xlabel(r'$\lambda$ [$\AA$]')
        ylabel('Intensity (2D/BM)')

    if options.printfig: savefig(prnfile,format='pdf')

    print ctime(),argv0,'done',
    print "(%.1f seconds)" % (time()-t0)
    if options.display:  show()                
