#!/usr/bin/env python

import os, sys, math
import numpy, pylab
import common_lib
import hlr_utils
import nessi_list
import DST

HUGE_NUMBER = 1.0e33  # FIXME here
debug       = False
logfile     = 'log'


def nexusFilePath(archiveDir,proposal,run):
    "probably redundant"
    run = str(run)
    return os.path.join(archiveDir,proposal,'1',run,'NeXus','SANS_%s.nxs' % run)

def div_ncerr2(s1,s2,to_num=True):
    """Divide and clean """
    s = common_lib.div_ncerr(s1,s2)
    if debug:
        f = open(logfile,"at")
        nremoved=0
        ntotal=0
    if to_num:
        # remove NaN results of division
        for i in xrange(len(s)):
            if debug:
                datastr=""

                y0 = s[i].y
                nremoved=0
                ntotal=len(y0)
                for k in xrange(len(y0)):
                    xx = s[i].axis[0].val[k]
                    yy = y0[k]
                    if yy!=yy:
                        datastr  += ", %d,%.3f" % (k,xx)
                        nremoved += 1
            y     = numpy.nan_to_num(list(s[i].y))
            var_y = numpy.nan_to_num(list(s[i].var_y))
            s[i].y      = nessi_list.NessiList()
            s[i].var_y  = nessi_list.NessiList()
            s[i].y.extend(y) 
            s[i].var_y.extend(var_y)
            if debug:
                print >> f,"%s,%d,%d%s" % (s[i].id[1],nremoved,ntotal,datastr)
    if debug: f.close()
    return s


def subtract_wavelength_depentent_bkg(obj,c0,c1):
    (result, res_descr) = hlr_utils.empty_result(obj)
    o_descr = hlr_utils.get_descr(obj)
    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)

    for i in xrange(hlr_utils.get_length(obj)):
        axis   = hlr_utils.get_value(obj, i, o_descr, "x", 0)
        val    = hlr_utils.get_value(obj, i, o_descr, "y", 0)
        err2   = hlr_utils.get_err2 (obj, i, o_descr, "y", 0)
        map_so = hlr_utils.get_map_so(obj, None, i)

        for k in xrange(len(val)):
            #dx = axis[k+1]-axis[k]
            val[k] -= c0 + c1*axis[k]
        value  = (val,err2)
        hlr_utils.result_insert(result, res_descr, value, map_so,"y",0)
    return result





def get_monitor(fileName):
    """Read monitor from a 3 column ASCII file"""
    fd  = open(fileName, "r")
    a3c = DST.Ascii3ColDST(fd)
    m   = a3c.getSOM()
    a3c.release_resource()
    fd.close()
    return m


def getXYE(s,non_nan=True,non_zero=True,non_huge=True):
    """Get x,y,var_y from a SOM and clean-up the data for plotting """
    x=list(s[0].axis[0].val[:-1])        
    y=list(s[0].y[:])
    v=list(s[0].var_y[:])
    if non_nan:
        y=numpy.nan_to_num(y)
        v=numpy.nan_to_num(v)
    if non_zero:
        xn,yn,vn = ([],[],[])
        for i in xrange(len(y)):
            y2 = y[i]*y[i]
            if y[i]>0 and v[i]<y2:
                xn.append(x[i])
                yn.append(y[i])
                vn.append(v[i])
        x,y,v=(xn,yn,vn)
    if non_huge:
        xn,yn,vn = ([],[],[])
        for i in xrange(len(y)):
            if abs(y[i])<HUGE_NUMBER and abs(v[i])<HUGE_NUMBER:
                xn.append(x[i])
                yn.append(y[i])
                vn.append(v[i])
        x,y,v=(xn,yn,vn)
    return x,y,v

def in_circle(x,y,x0,y0,r,inside=True):
    x -= x0
    y -= y0
    ra2 = x**2 + y**2
    rc2 = r*r
    if inside:
        return bool(ra2<=rc2)
    else:
        return bool(rc2<=ra2)


def create_roi(x0,y0,r1,r2,nx=80,ny=80,include=True):
    x0  += nx/2.0
    y0  += ny/2.0
    roi=[]
    exclude = not bool(include)
    for i in range(nx):
        for j in range(ny):
            cond1 = in_circle(i,j,x0,y0,r1,inside=False)
            cond2 = in_circle(i,j,x0,y0,r2,inside=True)
            cond  = bool(cond1 and cond2)
            if cond ^ exclude:
                roi.append((i,j))
    return roi

def write_roi(filename,roi,bank='bank1'):
    roi_file= open(filename,'wt')
    for id in roi:
        print >> roi_file,"%s_%s_%s" % (bank,id[0],id[1])
    roi_file.close()


def read_roi(filename,bank='bank1'):
    roi = []
    roi_file = open(filename,'rt')
    for line in roi_file.readlines():
        if not line.startswith(bank): continue
        id = line.strip().split('_')
        roi.append((int(id[1]),int(id[2])))
    roi_file.close()
    return roi


def errorplot(ax,s,marker='s',logxscale=False,logyscale=False):
    """ """
    x,y,e = getXYE(s)
    if len(y)<1:
        print "*** NO GOOD DATA TO PLOT"
        return None
    e  = numpy.sqrt(numpy.array(e))
    if logyscale:
        for i in xrange(len(e)):
            # TODO: FIXME here
            # At the moment 'clip' the error bar so that is does not go below zero
            if  e[i]>=y[i]: 
                e[i]=y[i]*0.99
        ax.set_yscale('log')
    if logxscale:
        ax.set_xscale('log')
    
    return pylab.errorbar(x,y,yerr=e,marker=marker,fmt=' ')



def sas_resolution(wavelength,radius,source_aperture,sample_aperture,primary, secondary):
    """Mildner-Carpenter Formula 
    Mildner, D. F. R. & Carpenter, J. M. (1984).
    J. Appl. Cryst. 17, 249-256
    Appendix C, formula C3 (cyllindrical symmetry)

    wavelength = (lambda,delta_lambda)  - neutron wavelength
    radius     = (r, dr)                - radius-of-integration 
    source_aperture			- aperture of the source
    sample_aperture		        - aperture of the sample
    primary				- primary flight path
    secondary				- secondary flight path

    Notes: 
    1) For fixed 
		delta_lambda/lambda, 
		source_aperture, sample_aperture
		primary, secondary 
       sqrt(sq2)/q is a const for a given r and dr"""
    
    k     = 2.0*math.pi/wavelength[0]       #  wavevector
    theta = math.atan2(radius[0],secondary) #  scattering angle
    dl    = wavelength[1]/wavelength[0]     #  delta(lambda)/ lambda

    # change naming convention
    r     = radius[0]**2        
    dr    = radius[1]**2
    r1    = source_aperture**2
    r2    = sample_aperture**2
    L1    = primary**2
    L2    = secondary**2
    L2p   = L2/(math.cos(theta)**2)     #  effective secondary flight path    

    q     = 2.0*k*math.sin(theta/2.0)  
    sq2   = k*k/12.0*(3*r1/L1 + 3*r2/L2p + (dr+r*dl*dl)/L2)
    return q,sq2


def get_spectrum(fileName,**kwargs):
    import DST
    from   time       import ctime
    """Work in progress
    """
    # -------------------------------------------------------------------
    #TODO: move these constants to config/options
    so_axis    = "time_of_flight"          # main SOM axis
    data_bank  = "/entry/bank1,1"          # NeXus path for 2D data
    # -------------------------------------------------------------------
    # process keyword arguments
    verbose    = False
    debug      = False
    signal_roi = None
    if kwargs.has_key('signal_roi'): signal_roi = kwargs['signal_roi']
    if kwargs.has_key('verbose'):    verbose    = kwargs['verbose'   ]
    if kwargs.has_key('debug'  ):    debug      = kwargs['debug'     ]
    # -------------------------------------------------------------------
    if verbose:
        print ctime(),'get_spectrum:',os.path.basename(fileName)
    config            = hlr_utils.Configure()
    config.data       = fileName
    config.data_paths = hlr_utils.create_data_paths(data_bank)
    data_dst          = DST.getInstance("application/x-NeXus", config.data)
    # -------------------------------------------------------------------
    if verbose:
        print ctime(),"get_spectrum: getting spectrum object"
    s1 = data_dst.getSOM(config.data_paths, so_axis,roi_file=signal_roi)
    return s1

