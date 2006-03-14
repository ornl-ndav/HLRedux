#!/usr/bin/env python
"""
This program covers the functionality outlined in 2.4.3 Area detector
measurement of specular reflectivity in <CHANGE:DR_Lib_RS.doc>.
"""

def step1():
    """Step 1. Convert IM1(TOF) to wavelength using function 3.15."""
    pass

def step2():
    """Step 2. Rebin eM1(lamda) to IM1(lambdas)'s wavelength axis
    using 3.12. The input is the efficiency eM1(lambda) with the
    output being erM1(lambda)."""
    pass

def step3():
    """Step 3. Correct IM1(lambda) for detector efficiency by using
    the function in 3.9 using IM1(lambda) as data1 and erM1(lambda) as
    data2. The result is IeM1(lambda)."""
    pass

def step4():
    """Step 4. Subtract the background using function 3.6 with
    IeDXY(lambda) as data1 and IeBXY(lambda) as data2. The result is
    IebDXY(lambda)."""
    pass

def step5():
    """Step 5. Determine the incident spectrum factor by using
    function 3.9 with M(lambda) as data1 and IeM1(lambda) as
    data2. The result is the incident spectrum factor,
    1/IeM2(lambda). This is essentially one over the incident
    spectrum. This step is necessary due to the removal of monitor 2
    when performing sample measurements."""
    pass

def step6():
    """Step 6. Scale the incident spectrum by the geometry factor
    using function 3.1 with 1/IeM2(lambda) as data1 and G as a. The
    result is the effective incident spectrum factor,
    Iinc(lambda). Note: Iinc(lambda) in not a raw spectrum as noted by
    section 0."""
    pass

def step7():
    """Step 7. Rebin Iinc(lambda) using with the same binning as
    IebDXY(lambda) by using function 3.12."""
    pass

def step8():
    """Step 8. Normalize using the incident spectrum factor using
    function 3.8 with IebDXY(lambda) as data1 and Iinc(lambda) as
    data2. The result is the reflectivity, R(lambda)."""
    pass

def step9():
    """Step 9. Sum the ROIs weighted by the uncertainties according to
    function 3.10."""
    pass

if __name__=="__main__":
    pass
