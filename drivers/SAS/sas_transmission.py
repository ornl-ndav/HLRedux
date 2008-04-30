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
    bragg_edge=4.00

    # parse options
    argv0   = os.path.basename(sys.argv[0])
    usage   = "%s [options] <run_number1> <run_number2" % argv0
    version = "%s %s" % (argv0,VERSION)
    tof_2d  = 1000
    tof_bm  = 1100
    opt = optparse.OptionParser(usage=usage,version=version)
    opt.add_option('--time-offset-2d','-d', dest='tof_2d', default=tof_2d,
                   help='set area detector TOF offset, default:%s' % tof_2d)
    opt.add_option('--time-offset-bm','-m', dest='tof_bm', default=tof_bm,
                   help='set beam monitor  TOF offset, default:%s' % tof_bm)
    opt.add_option('--wavelength-cut','-l', dest='lam_cut', default=bragg_edge,
                   help='set wavelength cut (lambda_min), default:%s' % bragg_edge)
    opt.add_option('--roi_file','-r', dest='roi_file', default=None ,
                   help='select roi file')
    opt.add_option('--output'  ,'-o', dest='output'  , default=None,
                   help='write transmission spectrum to a file')
    opt.add_option('--print'   ,'-p', dest='printfig', default=False, action='store_true',
                   help='save figure(s) into *.jpeg file(s)')
    opt.add_option('--proposal','-P', dest='proposal', default='2008_01_COM',
                   help='set SANS proposal id, default:2008_01_COM')
    opt.add_option('--archive' ,'-A', dest='archive' , default='/LENS/SANS',
                   help='set SANS archive directory, default=/LENS/SANS')
    options, arguments = opt.parse_args()
    
 
    
    tof_2d  = int(options.tof_2d)    # TOF offset for 2D (area detector) 
    tof_bm  = int(options.tof_bm)    # TOF offset for BM
    lam_cut = float(options.lam_cut)

    #FIXME: hard-coded axis ranges and binning
    lambda_axis = hlr_utils.Axis(lam_cut,20.00,0.4,
                                 units='Angstrom',
                                 title='lambda', bintype='lin') # lambda axis [Angstroms]

    print ctime(),"start"

    # for now only single run allowed
    if len(arguments)!=2:
        print "%s: exactly two run numbers required" % argv0
        opt.print_help()
        sys.exit(-1)

    runI0      = arguments[1]
    runI1      = arguments[0]

    nexusFile1 = nexusFilePath(options.archive,options.proposal,runI1)
    nexusFile0 = nexusFilePath(options.archive,options.proposal,runI0)

    print 'NeXus file'     , nexusFile1, 'exists?',os.path.exists(nexusFile1)
    print 'NeXus file'     , nexusFile0, 'exists?',os.path.exists(nexusFile0)
    print 'l axis:'        , lambda_axis
    print 'tof_offset_2d =', tof_2d
    print 'tof_offset_bm =', tof_bm
    print 'wavelength_cut=', lam_cut
    print 'roi_files='     , options.roi_file
    print 'output='        , options.output


    # -------------------------------------------------------------------
    # transmission run
    print ctime(),"getting transmission wavelength spectrum"
    m1 = normalize_to_monitor(nexusFile1,
                              time_offset_detector=(tof_2d,0.0),
                              time_offset_monitor =(tof_bm,0.0),
                              lam_cut=options.lam_cut,
                              signal_roi=options.roi_file,
                              verbose=True)

    m0 = normalize_to_monitor(nexusFile0,
                              time_offset_detector=(tof_2d,0.0),
                              time_offset_monitor =(tof_bm,0.0),
                              lam_cut=options.lam_cut,
                              signal_roi=options.roi_file,
                              verbose=True)
    
    print ctime(),"summing transmission wavelength spectrum"
    m1s = dr_lib.sum_all_spectra(m1,rebin_axis=lambda_axis.toNessiList())
    m0s = dr_lib.sum_all_spectra(m0,rebin_axis=lambda_axis.toNessiList())

    #m2  = common_lib.div_ncerr(m1s,m0s)
    m2  = sas_utils.div_ncerr2(m1s,m0s)

    outfile='trans-%s-%s.dat' % (runI1,runI0)
    if options.output:
        outfile=options.output
    hlr_utils.write_file(outfile, "text/Spec", m2,
                         verbose=True,
                         replace_path=False,
                         replace_ext=False,
                         message="Writing transmission I(lambda) to %s" % outfile)

  
    # lets' plot
    print ctime(),"plotting results"
    xm,ym,yem = getXYE(m2)
    yem = sqrt(array(yem))
    ax = subplot(111)
    errorbar(xm,ym,yerr=yem,marker='s',fmt=' ')
    
    ax.set_xlim(2.0,20.0)
    ax.set_ylim(0.0,1.2)
    
    if options.printfig:
        savefig('trans-%s-%s.pdf' % (runI1,runI0),format='pdf')

    show()


