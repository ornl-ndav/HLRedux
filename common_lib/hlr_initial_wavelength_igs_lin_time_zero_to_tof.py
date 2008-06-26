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

def initial_wavelength_igs_lin_time_zero_to_tof(obj, **kwargs):
    """
    @param obj: Object to be converted
    @type obj: C{SOM.SOM}, C{SOM.SO} or C{tuple}

    @param kwargs: A list of keyword arguments that the function accepts:

    @keyword lambda_f:The final wavelength and its associated error^2
    @type lambda_f: C{tuple}

    @keyword time_zero_slope: The time zero slope and its associated error^2
    @type time_zero_slope: C{tuple}

    @keyword time_zero_offset: The time zero offset and its associated error^2
    @type time_zero_offset: C{tuple}

    @keyword dist_source_sample: The source to sample distance information and
                                 its associated error^2
    @type dist_source_sample: C{tuple} or C{list} of C{tuple}s

    @keyword dist_sample_detector: The sample to detector distance information
                                   and its associated error^2
    @type dist_sample_detector: C{tuple} or C{list} of C{tuple}s

    @keyword run_filter: This determines if the filter on the negative
                         wavelengths is run. The default setting is True.
    @type run_filter: C{boolean}

    @keyword lojac: A flag that allows one to turn off the calculation of the
                    linear-order Jacobian. The default action is True for
                    histogram data.
    @type lojac: C{boolean}

    @keyword units: The expected units for this function. The default for this
                    function is I{Angstroms}
    @type units: C{string}


    @return: Object with a primary axis in initial_wavelength_igs converted to
             time-of-flight
    @rtype: C{SOM.SOM}, C{SOM.SO} or C{tuple}


    @raise TypeError: The incoming object is not a type the function recognizes

    @raise RuntimeError: The C{SOM} x-axis units are not I{microseconds}
    """
    result = None

    return result
    
