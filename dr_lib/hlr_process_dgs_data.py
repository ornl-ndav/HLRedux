#                  High-Level Reduction Functions
#           A part of the SNS Analysis Software Suite.
#
#                  Spallation Neutron Source
#          Oak Ridge National Laboratory, Oak Ridge TN.
#
#
#                             NOTICE
#
# For this software and its associated documentation, permission is granted
# to reproduce, prepare derivative works, and distribute copies to the public
# for any purpose and without fee.
#
# This material was prepared as an account of work sponsored by an agency of
# the United States Government.  Neither the United States Government nor the
# United States Department of Energy, nor any of their employees, makes any
# warranty, express or implied, or assumes any legal liability or
# responsibility for the accuracy, completeness, or usefulness of any
# information, apparatus, product, or process disclosed, or represents that
# its use would not infringe privately owned rights.
#

# $Id$

def process_dgs_data(obj, conf, bcan, ecan, tcoeff, **kwargs):
    """
    This function combines Steps 7 through 16 in Section 2.1.1 of the data
    reduction process for Direct Geometry Spectrometers as specified by the
    document at 
    U{http://neutrons.ornl.gov/asg/projects/SCL/reqspec/DR_Lib_RS.doc}. The
    function takes a calibrated dataset, a L{hlr_utils.Configure} object and
    processes the data accordingly.

    @param obj: A calibrated dataset object.
    @type obj: C{SOM.SOM}

    @param conf: Object that contains the current setup of the driver.
    @type conf: L{hlr_utils.Configure}

    @param bcan: The object containing the black can data.
    @type bcan: C{SOM.SOM}

    @param ecan: The object containing the empty can data.
    @type ecan: C{SOM.SOM}

    @param tcoeff: The transmission coefficient appropriate to the given data
                   set.
    @type: C{tuple}
    
    @param kwargs: A list of keyword arguments that the function accepts:

    @keyword dataset_type: The practical name of the dataset being processed.
                           The default value is I{data}.
    @type dataset_type: C{string}

    @keyword timer: Timing object so the function can perform timing estimates.
    @type timer: C{sns_timer.DiffTime}


    @return: Object that has undergone all requested processing steps
    @rtype: C{SOM.SOM}
    """
    import common_lib
    import dr_lib
    import hlr_utils

    # Check keywords
    try:
        dataset_type = kwargs["dataset_type"]
    except KeyError:
        dataset_type = "data"

    try:
        t = kwargs["timer"]
    except KeyError:
        t = None

    # Step 7: Create black can background contribution
    if bcan is not None:
        bccoeff = common_lib.sub_ncerr((1.0, 0.0), tcoeff)
        bcan1 = common_lib.mult_ncerr(bcan, bccoeff)
        del bcan
    else:
        bcan1 = None

    # Step 8: Create empty can background contribution
    if ecan is not None:
        ecan1 = common_lib.mult_ncerr(ecan, tcoeff)
        del ecan
    else:
        ecan1 = None

    # Step 9: Create background spectra
    if bcan1 is not None and ecan1 is not None:
        b_som = common_lib.add_ncerr(bcan1, ecan1)
    elif bcan1 is not None and ecan1 is None:
        b_som = bcan1
    elif bcan1 is None and ecan1 is not None:
        b_som = ecan1
    else:
        b_som = None

    del bcan1, ecan1
        
    # Step 10: Subtract background from data
    obj1 = dr_lib.subtract_bkg_from_data(obj, b_som, verbose=conf.verbose,
                                         timer=t,
                                         dataset1=dataset_type,
                                         dataset2="background")

    del obj, b_som

    # Step 11: Calculate initial velocity
    if conf.verbose:
        print "Calculating initial velocity"

    if t is not None:
        t.getTime(False)
        
    if conf.initial_energy is not None:
        initial_wavelength = common_lib.energy_to_wavelength(\
            conf.initial_energy.toValErrTuple())
        initial_velocity = common_lib.wavelength_to_velocity(\
            initial_wavelength)
    else:
        # This should actually calculate it, but don't have a way right now
        pass

    if t is not None:
        t.getTime(msg="After calculating initial velocity ")

    # Step 12: Calculate the time-zero offset
    if conf.time_zero_offset is not None:
        time_zero_offset = conf.time_zero_offset.toValErrTuple()
    else:
        # This should actually calculate it, but don't have a way right now
        time_zero_offset = (0.0, 0.0)

    # Step 13: Convert time-of-flight to final velocity
    if conf.verbose:
        print "Converting TOF to final velocity DGS"

    if t is not None:
        t.getTime(False)
        
    obj2 = common_lib.tof_to_final_velocity_dgs(obj1, initial_velocity,
                                                time_zero_offset,
                                                units="microsecond")

    if t is not None:
        t.getTime(msg="After calculating TOF to final velocity DGS ")
        
    del obj1
    
    # Step 14: Convert final velocity to final wavelength
    if conf.verbose:
        print "Converting final velocity DGS to final wavelength"

    if t is not None:
        t.getTime(False)
        
    obj3 = common_lib.velocity_to_wavelength(obj2)

    if t is not None:
        t.getTime(msg="After calculating velocity to wavelength ")

    del obj2

    if conf.dump_wave_comb:
        obj3_1 = dr_lib.sum_all_spectra(obj3,
                                     rebin_axis=conf.lambda_bins.toNessiList())
        hlr_utils.write_file(conf.output, "text/Spec", obj3_1,
                             output_ext="fwv",
                             data_ext=conf.ext_replacement,    
                             path_replacement=conf.path_replacement,
                             verbose=conf.verbose,
                             message="combined final wavelength information")

        del obj3_1

    # Step 15: Rebin the detector efficiency to the detector pixel axis

    # Step 16: Divide the detector pixel spectra by the detector efficiency

    return obj3
