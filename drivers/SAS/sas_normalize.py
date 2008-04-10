#!/usr/bin/env python

import os
from   time import ctime

import DST
import common_lib
import dr_lib
import hlr_utils


def normalize_to_monitor(fileName,time_offset_detector,time_offset_monitor,**kwargs):
    """Work in progress
    TODO - write documentation
         - use hlr_config
         - the function should be probably called
           normalize_sas_data(datalist,conf, **kwargs)

    @param fileName: NeXus data file name
    @type  fileName: C{string}

    @param time_offset_detector: time offset for area detector
    @type  time_offset_detector: C{tuple} (val,val_err)

    @param time_offset_monitor: time offset for beam monitor
    @type  time_offset_monitorr: C{tuple} (val,val_err)

    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword mon_eff: if True, 1/v efficiency correction will be applied
    to beam monitor spectrum
    @type mon_eff: C{bool}

    @keyword verbose: 
    @type verbose: C{bool}

    @keyword debug: 
    @type verbose: C{bool}
  
    @return: Object that has undergone all requested processing steps
    @rtype: C{SOM.SOM}

    
    """
    # -------------------------------------------------------------------
    #TODO: move these constants to config/options
    so_axis    = "time_of_flight"          # main SOM axis
    data_bank  = "/entry/bank1,1"          # NeXus path for 2D data
    bmon_bank  = "/entry/monitor1,1"       # NeXus path for beam monitor
    # -------------------------------------------------------------------
    # process keyword arguments
    mon_eff    = False
    verbose    = False
    debug      = False
    if kwargs.has_key('mon_eff'): mon_eff = kwargs['mon_eff']
    if kwargs.has_key('verbose'): verbose = kwargs['verbose']
    if kwargs.has_key('debug'  ): debug   = kwargs['debug']
    # -------------------------------------------------------------------
    if verbose:
        print ctime(),'normalize_to_monitor:',os.path.basename(fileName)
    config            = hlr_utils.Configure()
    config.data       = fileName
    config.data_paths = hlr_utils.create_data_paths(data_bank)
    config.bmon_path  = hlr_utils.create_data_paths(bmon_bank)
    data_dst   = DST.getInstance("application/x-NeXus", config.data)
    # -------------------------------------------------------------------
    if verbose:
        print ctime(),"normalize_to_monitor: getting spectrum object"
    s1 = data_dst.getSOM(config.data_paths, so_axis)
    m1 = data_dst.getSOM(config.bmon_path , so_axis)
    # -------------------------------------------------------------------
    if verbose:
        print ctime(),"normalize_to_monitor: fixing bin contents"
    s2 = dr_lib.fix_bin_contents(s1)
    m2 = dr_lib.fix_bin_contents(m1)
    # -------------------------------------------------------------------
    if verbose:
        print ctime(),"normalize_to_monitor: converting to scalar wavelength"
    s3 = common_lib.tof_to_wavelength_lin_time_zero(s2,units="microsecond",
                                     time_zero_offset=time_offset_detector,
                                     inst_param='total'  )
    m3 = common_lib.tof_to_wavelength_lin_time_zero(m2,units="microsecond",
                                     time_zero_offset=time_offset_monitor,
                                     inst_param='primary')
    # -------------------------------------------------------------------
    if mon_eff:
        if verbose:
            print ctime(),"normalize_to_monitor: correcting for monitor efficiency"
        m4 = dr_lib.feff_correct_mon(m3)
    else:
        m4 = m3

    # -------------------------------------------------------------------
    if verbose:
        print ctime(),"normalize_to_monitor: rebinning beam monitor"
    m5 = dr_lib.rebin_monitor(m4, s3)
    # -------------------------------------------------------------------
    if verbose:
        print ctime(),"normalize_to_monitor: normalizing data to monitor"
    s4 = common_lib.div_ncerr(s3,m5)
    # -------------------------------------------------------------------
    if verbose:
        print ctime(),"normalize_to_monitor: done."
    if debug:
        return m4,s3,s4
    return s4


