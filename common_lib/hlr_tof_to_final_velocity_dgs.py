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

def tof_to_final_velocity_dgs(obj. **kwargs):
    """
    This function converts a primary axis of a C{SOM} or C{SO} from
    time-of-flight to final_velocity_dgs. The time-of-flight axis for a
    C{SOM} must be in units of I{microseconds}. The primary axis of a C{SO} is
    assumed to be in units of I{microseconds}. A C{tuple} of C{(tof, tof_err2)}
    (assumed to be in units of I{microseconds}) can be converted to
    C{(final_velocity_dgs, final_velocity_dgs_err2)}.

    @param obj: Object to be converted
    @type obj: C{SOM.SOM}, C{SOM.SO} or C{tuple}
    
    @param kwargs: A list of keyword arguments that the function accepts:

    @keyword velocity_i: The initial velocity and its associated error^2
    @type velocity_i: C{tuple}
    
    @keyword time_zero_offset: The time zero offset and its associated error^2
    @type time_zer_offset: C{tuple}
    
    @keyword dist_source_sample: The source to sample distance information and
                                 its associated error^2
    @type dist_source_sample: C{tuple} or C{list} of C{tuple}s 

    @keyword dist_sample_detector: The sample to detector distance information
                                   and its associated error^2
    @type dist_sample_detector: C{tuple} or C{list} of C{tuple}s

    @keyword units: The expected units for this function. The default for this
                    function is I{microseconds}
    @type units: C{string}


    @return: Object with a primary axis in time-of-flight converted to
             final_velocity_dgs
    @rtype: C{SOM.SOM}, C{SOM.SO} or C{tuple}


    @raise TypeError: The incoming object is not a type the function recognizes
    @raise RuntimeError: The C{SOM} x-axis units are not I{microseconds}
    """
    import hlr_utils

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj)
    o_descr = hlr_utils.get_descr(obj)

    # Setup keyword arguments
    try:
        velocity_i = kwargs["velocity_i"]
    except KeyError:
        velocity_i = None

    try:
        time_zero_offset = kwargs["time_zero_offset"]
    except KeyError:
        time_zero_offset = None

    try:
        dist_source_sample = kwargs["dist_source_sample"]
    except KeyError:
        dist_source_sample = None

    try:
        dist_sample_detector = kwargs["dist_sample_detector"]
    except KeyError:
        dist_sample_detector = None

    try:
        units = kwargs["units"]
    except KeyError:
        units = "microseconds"

    return result
