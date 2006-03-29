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
    return hlr_sub_ncerr.sub_ncerr(norm_som, norm_bkg_som)

def subtract_dark_current_from_data(config, data_som, dc_som):
    """Step 3. Subtract the dark current spectrum using function 3.6
    with ItDXY(TOF) as data1 and ItDCXY(TOF) as data2. The result of
    this is ItdDXY(TOF)."""

    if dc_som==None:
        return data_som

    import hlr_sub_ncerr
    return hlr_sub_ncerr.sub_ncerr(data_som, dc_som)

def determine_time_indep_bkg(config, data_som):
    """Step 4. Determine the sample dependent, time independent
    background B by fitting a line to predetermined end points of
    ItdDXY(TOF) using function 3.43."""

    kwargs = ""

    if not config.TOF_start==None:
        kwargs = "start="+TOF_start

    if not config.TOF_end==None:
        kwargs = kwargs+", end="+TOF_end

    import hlr_weighted_average
    return hlr_weighted_average.weighted_average(data_som, kwargs)

def subtract_time_indep_bkg(config, data_som, B):
    """Step 5. Subtract B from the data spectrum using function 3.2
    with ItdDXY(TOF) as data1 and B as a. The result is ItdsDXY(TOF)."""

    if B == None:
        return data_som

    import hlr_subtract_time_indep_bkg
    return hlr_subtract_time_indep_bkg.subtract_time_indep_bkg(data_som, B)

def subtract_bkg_from_data(config, data_som, bkg_som):
    """Step 6. Subtract the measured background spectrum from the data
    spectrum using function 3.6 with ItdsDXY(TOF) as data1 and
    ItBXY(TOF) as data2. The result of this is ItdsbDXY(TOF)."""

    if config.no_bkg_sub:
        return data_som

    import hlr_sub_ncerr
    return hlr_sub_ncerr.sub_ncerr(data_som, bkg_som)

def norm_data_by_van(config, data_som, norm_som):
    """Step 7. Normalize ItdsbDXY(TOF) by vanadium spectrum,
    ItbNXY(TOF), using function 3.9. The result is ItdsbnDXY(TOF)."""

    import hlr_div_ncerr
    return hlr_div_ncerr.div_ncerr(data_som, norm_som)

def convert_data_and_mon_to_wavelength(config, data_som, mon2_som):
    """Step 8. Convert ItM2(TOF) and ItdsbnDXY(TOF) to ItM2(lambda)
    and ItdsbnDXY(lambda) using function 3.15 for M2 and function 3.29
    for DXY."""

    if mon2_som!=None:
        import hlr_tof_to_wavelength
        mon2_som1 = hlr_tof_to_wavelength.tof_to_wavelength(mon2_som)
    else:
        mon2_som1 = None

    import hlr_tof_initial_wavelength_igs
    data_som1=hlr_tof_initial_wavelength_igs.tof_initial_wavelength_igs(\
        data_som)

    return data_som1, mon2_som1

def rebin_mon_eff(config, mon2_som, mon2_eff):
    """Step 9. Rebin the monitor efficiency to each monitor's
    wavelength axis using 3.12. The input is the efficiency
    eM2(lambda) with the output being erM2(lambda)."""

    return mon2_eff

def eff_correct_mon(config, mon2_som, mon2_eff):
    """Step 10. Divide ItM2(lambda) by erM2(lambda) using function
    3.9. The result is IeM2(lambda)."""

    if mon2_eff == None:
        return mon2_som

    return mon2_som

def rebin_det_eff(config, data_som, det_eff):
    """Step 11. Rebin eDXY(lambda) to the same binning in wavelength
    as ItbdnDXY(lambda) by using function 3.12. The result is
    erDXY(lambda)"""

    return det_eff

def eff_correct_data(config, data_som, det_eff):
    """Step 12. Correct ItbdneDXY(lambda) for detector efficiency by
    using the function in 3.9 using ItbdnDXY(lambda) as data1 and
    erDXY(lambda) as data2. The result is ItbdneDXY(lambda)."""

    if det_eff==None:
        return data_som

    return data_som

def norm_data_by_mon(config, data_som, mon_som):
    """Step 13. Normalize by the integrated monitor intensity using
    3.5 using ItbdneDXY(lambda) as data1 and IteM2(lambda) as a. The
    result of this is S(lambda)."""

    if mon_som==None:
        return data_som

    import hlr_div_ncerr
    return hlr_div_ncerr.div_ncerr(data_som, mon_som)

def calc_k_initial(config, data_som):
    """Step 14. Calculate initial wavevector using function 3.24."""

    import hlr_wavelength_to_scalar_k
    return hlr_wavelength_to_scalar_k.wavelength_to_scalar_k(data_som)

def calc_E_initial(config, data_som):
    """Step 15. Calculate incident energy using function 3.22."""

    import hlr_wavelength_to_energy
    return hlr_wavelength_to_energy.wavelength_to_energy(data_som)

def calc_k_final(config):
    """Step 16. Calculate final wavevector using function 3.24."""

    import hlr_wavelength_to_scalar_k
    return hlr_wavelength_to_scalar_k.wavelength_to_scalar_k(config.wavelength_final)

def calc_E_final(config):
    """Step 17. Calculate final energy using function 3.22."""

    import hlr_wavelength_to_energy
    return hlr_wavelength_to_energy.wavelength_to_energy(config.wavelength_final)

def calc_energy_transfer(config, data_som, energy_final):
    """Step 18. Calculate energy transfer using function 3.30."""

    import hlr_energy_transfer
    data_som1 = hlr_energy_transfer.energy_transfer(data_som, energy_final)

    import hlr_frequency_to_energy
    return hlr_frequency_to_energy.frequency_to_energy(data_som1)

def calc_scalar_Q(config, data_som, k_final):
    """Step 19. Calculate momentum transfer using function 3.33."""

    import hlr_init_scatt_wavevector_to_scalar_Q
    return hlr_init_scatt_wavevector_to_scalar_Q.init_scatt_wavevector_to_scalar_Q(data_som, k_final)

def rebin_final(config, data_som):
    """Step 20. Rebin onto user defined two dimensional grid using
    function 3.13."""
    
    import hlr_rebin_axis_2D
    return hlr_rebin_axis_2D.rebin_axis_2D(data_som, config.Q_bins,\
                                           config.E_bins)

def sum_all_spectra(config, data_som):
    """Step 21. Sum all spectrum together using function 3.10."""

    # Need HLR function for combining all spectra
    pass

def run(config):
    # Michael works here

    if config.data==None:
        raise RuntimeError, "Need to pass a data filename to the driver \
        script."

    if config.output==None:
        print "No output file name specified. Using temp.srf"
        config.output="temp.srf"

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
        norm_dst.release_resource()
    else:
        n_som1 = None
        
    if not config.norm_bkg==None:
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
        dc_dst.release_resource()
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
        bkg_dst.release_resource()
    else:
        bkg_som1 = None

    d_som4 = subtract_bkg_from_data(config, d_som3, bkg_som1)

    if not config.no_norm:
        d_som5 = norm_data_by_van(config, d_som4, n_som1)
    else:
        d_som5 = d_som4

    if config.no_mon_norm:
        m_som1 = None
    else:
        som_id = ("/entry/monitor2", 1)
        m_som1 = data_dst.getSOM(som_id, so_axis)

    # Note: wavelength_final MUST be a tuple
    if config.wavelength_final==None:
        config.wavlength_final = data_dst.getParam("wavelength_final")

    dsom5.attr_list["Wavelength_final"]=config.wavelength_final

    if config.mon_geom:
        pass

    d_som6, m_som2 = convert_data_and_mon_to_wavelength(config, d_som5, m_som1)

    if config.mon_eff==None:
        m_eff1 = None
    else:
        meff_dst = dst_base.getInstance("text/xml",\
                                        config.mon_eff)
        m_eff1 = meff_dst.getSOM("/entry/monitor2")
        m_eff2 = rebin_mon_eff(config, m_som2, m_eff1)
        
    m_som3 = eff_correct_mon(config, m_som2, m_eff2)

    if config.det_eff==None:
        det_eff2 = None
    else:
        deteff_dst = dst_base.getInstance("text/xml",\
                                          config.det_eff)
        det_eff1 = deteff_dst.getSOM("/entry/dectector")
        det_eff2 = rebin_det_eff(config, d_som6, det_eff1)
    
    d_som7 = eff_correct_data(config, d_som6, det_eff2)

    d_som8 = norm_data_by_mon(config, d_som7, m_som3)
    
    d_som9 = calc_k_initial(config, d_som8)
    
    d_som10 = calc_E_initial(config, d_som9)

    data_dst.release_resource()
    
    k_final = calc_k_final(config)
    
    E_final = calc_E_final(config)
    
    d_som11 = energy_transfer(config, d_som10, E_final)
    
    d_som12 = calc_scalar_Q(config, d_som11, k_final)

    if config.Q_bins==None or config.E_bins==None:
        config.banks_separate=True
        d_som13 = d_som12
    else:
        d_som13 = rebin_final(config, d_som12)

    if not config.banks_separate:
        d_som14 = sum_all_spectra(config, d_som13)
    else:
        d_som14 = d_som13

    resource = open(config.output, "w")
    a3c = dst_base.getInstance("text/Spec", resource)
    a3c.writeSOM(d_som14)
    a3c.release_resource()

if __name__=="__main__":
    # Pete works here

    run()
    

