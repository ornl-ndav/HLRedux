#!/usr/bin/env python
"""
This program covers the functionality outlined in 2.2.1 Powder or
amorphous material reduction in <CHANGE:DR_Lib_RS.doc>.
"""

def step1(config):
    """Step 1. Apply dead time correction to each I(TOF) using
    function 3.38. The result is ItiXY(TOF)."""
    
    if not config.use_dead_time:
        return None

    return data_som

def step2(config):
    """Step 2. Subtract measured normalization background using 3.6
    with ItNXY(TOF) as data1 and ItNBXY(TOF) as data2. The result is
    ItbNXY(TOF)."""

    if not config.norm_bkg and not config.norm:
        return None
    
    return None

def step3(config, data_som):
    """Step 3. Subtract the dark current spectrum using function 3.6
    with ItDXY(TOF) as data1 and ItDCXY(TOF) as data2. The result of
    this is ItdDXY(TOF)."""

    if not config.dark_current:
        return data_som
    
    return data_som

def step4(config, data_som):
    """Step 4. Determine the sample dependent, time independent
    background B by fitting a line to predetermined end points of
    ItdDXY(TOF) using function 3.43."""

    if config.no_tib:
        return None

    return None

def step5(config, data_som, B=None):
    """Step 5. Subtract B from the data spectrum using function 3.2
    with ItdDXY(TOF) as data1 and B as a. The result is ItdsDXY(TOF)."""

    if config.no_tib:
        return data_som

    return data_som

def step6(config, data_som):
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
        raise RuntimeError, "Need pass a data file name to the driver script."

    d_som1 = step1(config)
    n_som1 = step2(config)
    d_som2 = step3(config, d_som1)
    B = step4(config, d_som2)
    d_som3 = step5(config, d_som2, B)
    d_som4 = step6(config, d_som3)
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
    

