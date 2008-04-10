#!/usr/bin/env python

import os, sys, math
from   time import ctime
import DST
import nessi_list
import common_lib
import dr_lib
import hlr_utils


def normalize_to_monitor(fileName,
                         time_offset_detector,time_offset_monitor,
                         lambda_min,lambda_max):
    """Work in progress
    TODO - write documentation
    function parameters:
      fileName   - NeXus data file name
      time_offset_detector - time offset for 2D detector
      time_offset_monitor  - time offset for BM detector
      lambda_min           - min wavelength for BM normalization
      lambda_max           - max wavelength for BM normalization
    """
    # -------------------------------------------------------------------
    so_axis    = "time_of_flight"          # main SOM axis
    data_bank  = "/entry/bank1,1"          # NeXus path for 2D data
    bmon_bank  = "/entry/monitor1,1"       # NeXus path for beam monitor
    # -------------------------------------------------------------------
    print ctime(),'normalize_to_monitor:',os.path.basename(fileName)
    config            = hlr_utils.Configure()
    config.data       = fileName
    config.data_paths = hlr_utils.create_data_paths(data_bank)
    config.bmon_path  = hlr_utils.create_data_paths(bmon_bank)
    data_dst   = DST.getInstance("application/x-NeXus", config.data)
    # -------------------------------------------------------------------
    print ctime(),"normalize_to_monitor: getting spectrum object ..."
    s1 = data_dst.getSOM(config.data_paths, so_axis)
    m1 = data_dst.getSOM(config.bmon_path , so_axis)
    # -------------------------------------------------------------------
    print ctime(),"normalize_to_monitor: fixing bin contents ..."
    s2 = dr_lib.fix_bin_contents(s1)
    m2 = dr_lib.fix_bin_contents(m1)
    # -------------------------------------------------------------------
    print ctime(),"normalize_to_monitor: converting to scalar wavelength ..."
    s3 = common_lib.tof_to_wavelength_lin_time_zero(s2,units="microsecond",
                                     time_zero_offset=time_offset_detector,
                                     inst_param='total'  )
    m3 = common_lib.tof_to_wavelength_lin_time_zero(m2,units="microsecond",
                                     time_zero_offset=time_offset_monitor,
                                     inst_param='primary')
    # -------------------------------------------------------------------
    print ctime(),"normalize_to_monitor: correcting for monitor efficiency ..."
    m4 = dr_lib.feff_correct_mon(m3)
    # -------------------------------------------------------------------
    print ctime(),"normalize_to_monitor: making dimensionless monitor  ..."
    m5 = dr_lib.dimensionless_mon(m4, lambda_min, lambda_max)
    # -------------------------------------------------------------------
    print ctime(),"normalize_to_monitor: rebinning bmon ..."
    m6 = dr_lib.rebin_monitor(m5, s3)
    # -------------------------------------------------------------------
    print ctime(),"normalize_to_monitor: normalizing ..."
    s4 = common_lib.div_ncerr(s3,m6)
    # -------------------------------------------------------------------
    print ctime(),"normalize_to_monitor: done"
    return m5,s3,s4



