#!/usr/bin/env python
"""
This program covers the functionality outlined in 2.4.1 Measurement of
incident spectrum ration, M(lambda) in <CHANGE:DR_Lib_RS.doc>.
"""

def step1():
    """Step 1. Convert IM1(TOF) and IM2(TOF) to wavelength using
    function 3.15."""
    pass

def step2():
    """Step 2. Rebin the monitor efficiency to each monitor's
    wavelength axis using 3.12. The input is the efficiency
    epsilon(lambda) with the output being epsilon^r(lambda)."""
    pass

def step3():
    """Step 3. Correct for detector efficiency by using the function
    in 3.9 using I(lambda) as data1 and epsilon^r(lambda) as
    data2. The result is I^epsilon(lambda)."""
    pass

def step4():
    """Step 4. Rebin I^epsilon_M2(lambda) to I^epsilon_M1(lambda)'s
    wavelength axis using function 3.12. The input is
    I^epsilon_M2(lambda) with the output being I^epsilonr_M2(lambda)."""
    pass

def step5():
    """Step 5. Divide the two monitor intensities using function 3.9
    with I^epsilon_M1(lambda) as data1 and I^epsilonr_M2(lambda) as
    data2. The result is M(lambda)."""
    pass

if __name__=="__main__":
    pass
