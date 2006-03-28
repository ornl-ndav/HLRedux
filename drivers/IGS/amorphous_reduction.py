#!/usr/bin/env python
"""
This program covers the functionality outlined in 2.2.1 Powder or
amorphous material reduction in <CHANGE:DR_Lib_RS.doc>.
"""

def dead_time_correction(config, data_som):
    """Step 1. Apply dead time correction to each I(TOF) using
    function 3.38. The result is ItiXY(TOF)."""

    return data_som

def subtract_norm_bkg_from_norm(config,norm_som, norm_bkg_som):
    """Step 2. Subtract measured normalization background using 3.6
    with ItNXY(TOF) as data1 and ItNBXY(TOF) as data2. The result is
    ItbNXY(TOF)."""

    if norm_som==None:
        return None
    elif norm_bkg_som==None:
        return norm_som

    import hlr_sub_ncerr

    return sub_ncerr(norm_som, norm_bkg_som)

def subtract_dark_current_from_data(config, data_som, dc_som):
    """Step 3. Subtract the dark current spectrum using function 3.6
    with ItDXY(TOF) as data1 and ItDCXY(TOF) as data2. The result of
    this is ItdDXY(TOF)."""

    if dc_som==None:
        return data_som

    import hlr_sub_ncerr

    return sub_ncerr(data_som, dc_som)

def determine_time_indep_bkg(config, data_som):
    """Step 4. Determine the sample dependent, time independent
    background B by fitting a line to predetermined end points of
    ItdDXY(TOF) using function 3.43."""

    kwargs = ""

    if not config.TOF_start==None:
        kwargs = "start=".TOF_start

    if not config.TOF_end==None:
        kwargs = kwargs."end=".TOF_end

    import hlr_weighted_average

    return weighted_average(data_som, kwargs)

def subtract_time_indep_bkg(config, data_som, B):
    """Step 5. Subtract B from the data spectrum using function 3.2
    with ItdDXY(TOF) as data1 and B as a. The result is ItdsDXY(TOF)."""

    if B == None:
        return data_som

    import hlr_subtract_time_indep_bkg

    return subtract_time_indep_bkg(data_som, B)

def subtract_bkg_from_data(config, data_som):
    """Step 6. Subtract the measured background spectrum from the data
    spectrum using function 3.6 with ItdsDXY(TOF) as data1 and
    ItBXY(TOF) as data2. The result of this is ItdsbDXY(TOF)."""

    if config.no_bkg_sub:
        return data_som

    return data_som

def step7(config, data_som, norm_som):
    """Step 7. Normalize ItdsbDXY(TOF) by vanadium spectrum,
    ItbNXY(TOF), using function 3.9. The result is ItdsbnDXY(TOF)."""

    if config.no_norm:
        return data_som

    return data_som

def step8(config, data_som):
    """Step 8. Convert ItM2(TOF) and ItdsbnDXY(TOF) to ItM2(lambda)
    and ItdsbnDXY(lambda) using function 3.15 for M2 and function 3.29
    for DXY."""

    if config.no_mon_norm:
        mon2_som = None

    return data_som, mon2_som

def step9(config, mon2_som):
    """Step 9. Rebin the monitor efficiency to each monitor's
    wavelength axis using 3.12. The input is the efficiency
    eM2(lambda) with the output being erM2(lambda)."""

    if config.no_mon_norm or config.no_mon_eff:
        return None

    return mon2_eff


def step10(config, mon2_som, mon2_eff):
    """Step 10. Divide ItM2(lambda) by erM2(lambda) using function
    3.9. The result is IeM2(lambda)."""

    if config.no_nom_norm or config.no_mon_eff:
        return mon2_som

    return mon2_som

def step11(config, data_som):
    """Step 11. Rebin eDXY(lambda) to the same binning in wavelength
    as ItbdnDXY(lambda) by using function 3.12. The result is
    erDXY(lambda)"""

    if config.no_det_eff:
        return None

    return det_eff

def step12(config, data_som, det_eff):
    """Step 12. Correct ItbdneDXY(lambda) for detector efficiency by
    using the function in 3.9 using ItbdnDXY(lambda) as data1 and
    erDXY(lambda) as data2. The result is ItbdneDXY(lambda)."""

    if config.no_det_eff:
        return data_som

    return data_som

def step13(config, data_som, mon_som):
    """Step 13. Normalize by the integrated monitor intensity using
    3.5 using ItbdneDXY(lambda) as data1 and IteM2(lambda) as a. The
    result of this is S(lambda)."""

    if config.no_int_mon_norm:
        return data_som

def step14(config, data_som):
    """Step 14. Calculate initial wavevector using function 3.24."""

    return data_som

def step15(config, data_som):
    """Step 15. Calculate incident energy using function 3.22."""

    return data_som

def step16(config, data_som):
    """Step 16. Calculate final wavevector using function 3.24."""

    return data_som

def step17(config, data_som):
    """Step 17. Calculate final energy using function 3.22."""
    return data_som

def step18(config, data_som):
    """Step 18. Calculate energy transfer using function 3.30."""
    return data_som

def step19(config, data_som):
    """Step 19. Calculate momentum transfer using function 3.33."""
    return data_som

def step20(config, data_som):
    """Step 20. Rebin onto user defined two dimensional grid using
    function 3.13."""

    if config.Q_bins==None and config.E_bins==None:
        config.banks_separate=True
        return data_som
    
    return data_som

def step21(config, data_som):
    """Step 21. Sum all spectrum together using function 3.10."""

    if config.banks_separate:
        return data_som

    return data_som

def run(config):
    # Michael works here

    if config.data==None:
        raise RuntimeError, "Need to pass a data filename to the driver \
        script."

    import dst_base
    
    data_dst = dst_base.getInstance("application/x-NeXus", config.data)
    som_id = ("/entry/data", 1)
    so_axis = "time_of_flight"

    d_som1 = data_dst.getSOM(som_id, so_axis)

    if not config.use_dead_time:
        d_som2 = dead_time_correction(config, d_som1)
    else:
        d_som2 = d_som1

    if not config.norm==None:
        norm_dst = dst_base.getInstance("application/x-NeXus", config.norm)
        n_som1 = norm_dst.getSOM(som_id, so_axis)
    else:
        n_som1 = None
        
    if not config.norm_bkg==None
        norm_bkg_dst = dst_base.getInstance("application/x-NeXus",\
                                            config.norm_bkg)
        n_bkg_som1 = norm_bkg_dst.getSOM(som_id, so_axis)
    else:
        n_bkg_som1 = None


    n_som2 = subtract_norm_bkg_from_norm(config, n_som1, n_bkg_som1)

    if not config.dark_current==None:
        dc_dst = dst_base.getInstance("application/x-NeXus",\
                                      config.dark_current)
        dc_som1 = dst_base.getSOM(som_id, so_axis)
    else:
        dc_som1 = None
        
    d_som3 = subtract_dark_current_from_data(config, d_som2, dc_som1)

    if not config.no_tib:
        B = determine_time_indep_bkg(config, d_som3)
    else:
        B = None

    d_som4 = subtract_time_indep_bkg(config, d_som3, B)

    if not config.bkg==None:
        bkg_dst = dst_base.getInstance("application/x-NeXus",\
                                      config.dark_current)
        bkg_som1 = dst_base.getSOM(som_id, so_axis)
    else:
        bkg_som1 = None

    d_som4 = subtract_bkg_from_data(config, d_som3, bkg_som1)

    
    d_som5 = step7(config, d_som4, n_som1)
    d_som6, m_som1 = step8(config, d_som5)
    m_eff = step9(config, m_som1)
    m_som2 = step10(config, m_som1, m_eff)
    det_eff = step11(config, d_som6)
    d_som7 = step12(config, d_som6, det_eff)
    d_som8 = step13(config, d_som7, m_som2)
    d_som9 = step14(config, d_som8)
    d_som10 = step15(config, d_som9)
    d_som11 = step16(config, d_som10)
    d_som12 = step17(config, d_som11)
    d_som13 = step18(config, d_som12)
    d_som14 = step19(config, d_som13)
    d_som15 = step20(config, d_som14)
    d_som16 = step21(config, d_som15)

if __name__=="__main__":
    # Pete works here

    run()
    

