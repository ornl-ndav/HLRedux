#!/usr/bin/env python

import os, sys, math
import numpy
import common_lib
import hlr_utils
import nessi_list


def nexusFilePath(archiveDir,proposal,run):
    "probably redundant"
    return "%s/%s/1/%s/NeXus/SANS_%s.nxs"    % (archiveDir,proposal,run,run)

def div_ncerr2(s1,s2,to_num=True):
    s = common_lib.div_ncerr(s1,s2)
    if to_num:
        # remove NaN results of division
        for i in xrange(len(s)):
            y     = numpy.nan_to_num(list(s[i].y))
            var_y = numpy.nan_to_num(list(s[i].var_y))
            s[i].y      = nessi_list.NessiList()
            s[i].var_y  = nessi_list.NessiList()
            s[i].y.extend(y) 
            s[i].var_y.extend(var_y) 
    return s

def getXY(s,histo=False):
    y=list(s[0].y[:])
    if histo:
        x=list(s[0].axis[0].val[:])
        y.append(s[0].y[-1])
    else:
        x=list(s[0].axis[0].val[:-1])
    return x,y

def getXYE(s,non_nan=True,non_zero=True):
    x=list(s[0].axis[0].val[:-1])        
    y=list(s[0].y[:])
    v=list(s[0].var_y[:])
    if non_nan:
        y=numpy.nan_to_num(y)
        v=numpy.nan_to_num(v)
    if non_zero:
        xn = []
        yn = []
        vn = []
        for i in xrange(len(y)):
            y2 = y[i]*y[i]
            if y[i]>0 and v[i]<y2:
                xn.append(x[i])
                yn.append(y[i])
                vn.append(v[i])
        return xn,yn,vn
    return x,y,v



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

