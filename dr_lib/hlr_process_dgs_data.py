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

def process_dgs_data(obj, conf, **kwargs):
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

    # Step 8: Create empty can background contribution

    # Step 9: Create background spectra

    # Step 10: Subtract background from data

    # Step 11: Calculate initial velocity
    if conf.initial_energy is not None:
        initial_wavelength = common_lib.energy_to_wavelength(\
            conf.initial_energy.toValErrTuple())
        initial_velocity = common_lib.wavelength_to_velocity(\
            initial_wavelength)
    else:
        # This should actually calculate it, but don't have a way right now
        pass

    # Step 12: Calculate the time-zero offset
    if conf.time_zero_offset is not None:
        time_zero_offset = conf.time_zero_offset.toValErrTuple()
    else:
        # This should actually calculate it, but don't have a way right now
        time_zero_offset = (0.0, 0.0)

    # Step 13: Convert time-of-flight to final velocity
    obj1 = common_lib.tof_to_final_velocity_dgs(obj, initial_velocity,
                                                time_zero_offset,
                                                units="microsecond")

    del obj
    # Step 14: Convert final velocity to final wavelength
    obj2 = common_lib.velocity_to_wavelength(obj1)

    del obj1
    # Step 15: Rebin the detector efficiency to the detector pixel axis

    # Step 16: Divide the detector pixel spectra by the detector efficiency

    return obj2
