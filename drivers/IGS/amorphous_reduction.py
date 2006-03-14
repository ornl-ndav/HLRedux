#!/usr/bin/env python
"""
This program covers the functionality outlined in 2.2.1 Powder or
amorphous material reduction in <CHANGE:DR_Lib_RS.doc>.
"""

def step1():
    """Step 1. Apply dead time correction to each I(TOF) using
    function 3.38. The result is ItiXY(TOF)."""
    pass

def step2():
    """Step 2. Subtract measured normalization background using 3.6
    with ItNXY(TOF) as data1 and ItNBXY(TOF) as data2. The result is
    ItbNXY(TOF)."""
    pass

def step3():
    """Step 3. Subtract the dark current spectrum using function 3.6
    with ItDXY(TOF) as data1 and ItDCXY(TOF) as data2. The result of
    this is ItdDXY(TOF)."""
    pass

def step4():
    """Step 4. Determine the sample dependent, time independent
    background B by fitting a line to predetermined end points of
    ItdDXY(TOF) using function 3.43."""
    pass

def step5():
    """Step 5. Subtract B from the data spectrum using function 3.2
    with ItdDXY(TOF) as data1 and B as a. The result is ItdsDXY(TOF)."""
    pass

def step6():
    """Step 6. Subtract the measured background spectrum from the data
    spectrum using function 3.6 with ItdsDXY(TOF) as data1 and
    ItBXY(TOF) as data2. The result of this is ItdsbDXY(TOF)."""
    pass

def step7():
    """Step 7. Normalize ItdsbDXY(TOF) by vanadium spectrum,
    ItbNXY(TOF), using function 3.9. The result is ItdsbnDXY(TOF)."""
    pass

def step8():
    """Step 8. Cqonvert ItM2(TOF) and ItdsbnDXY(TOF) to ItM2(lambda)
    and ItdsbnDXY(lambda) using function 3.15 for M2 and function 3.29
    for DXY."""
    pass

def step9():
    """Step 9. Rebin the monitor efficiency to each monitor's
    wavelength axis using 3.12. The input is the efficiency
    eM2(lambda) with the output being erM2(lambda)."""
    pass

def step10():
    """Step 10. Divide ItM2(lambda) by erM2(lambda) using function
    3.9. The result is IeM2(lambda)."""
    pass

def step11():
    """Step 11. Rebin eDXY(lambda) to the same binning in wavelength
    as ItbdnDXY(lambda) by using function 3.12. The result is
    erDXY(lambda)"""
    pass

def step12():
    """Step 12. Correct ItbdneDXY(lambda) for detector efficiency by
    using the function in 3.9 using ItbdnDXY(lambda) as data1 and
    erDXY(lambda) as data2. The result is ItbdneDXY(lambda)."""
    pass

def step13():
    """Step 13. Normalize by the integrated monitor intensity using
    3.5 using ItbdneDXY(lambda) as data1 and IteM2(lambda) as a. The
    result of this is S(lambda)."""
    pass

def step14():
    """Step 14. Calculate initial wavevector using function 3.24."""
    pass

def step15():
    """Step 15. Calculate incident energy using function 3.22."""
    pass

def step16():
    """Step 16. Calculate final wavevector using function 3.24."""
    pass

def step17():
    """Step 17. Calculate final energy using function 3.22."""
    pass

def step18():
    """Step 18. Calculate energy transfer using function 3.30."""
    pass

def step19():
    """Step 19. Calculate momentum transfer using function 3.33."""
    pass

def step20():
    """Step 20. Rebin onto user defined two dimensional grid using
    function 3.13."""
    pass

def step21():
    """Step 21. Sum all spectrum together using function 3.10."""
    pass

if __name__=="__main__":
    pass
