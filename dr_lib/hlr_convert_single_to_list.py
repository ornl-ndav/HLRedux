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

def convert_single_to_list(funcname, number, som, **kwargs):
    """
    This function retrieves a function object from the L{common_lib} set of
    functions that provide axis transformations and converts the provided
    number based on that function. Instrument geometry information needs to be
    provided via the C{SOM}. The following is the list of functions supported
    by this one.

      - d_spacing_to_tof_focused_det
      - energy_to_wavelength
      - frequency_to_energy
      - initial_wavelength_igs_lin_time_zero_to_tof
      - init_scatt_wavevector_to_scalar_Q
      - tof_to_initial_wavelength_igs_lin_time_zero
      - tof_to_initial_wavelength_igs
      - tof_to_scalar_Q
      - tof_to_wavelength_lin_time_zero
      - tof_to_wavelength
      - wavelength_to_d_spacing
      - wavelength_to_energy
      - wavelength_to_scalar_k
      - wavelength_to_scalar_Q

    @param funcname: The name of the axis conversion function to use
    @type funcname: C{string}

    @param number: The value and error^2 to convert
    @type number: C{tuple}

    @param som: The object containing geometry and other special information
    @type som: C{SOM.SOM}

    @param kwargs: A list of keyword arguments that the function accepts:

    @keyword inst_param: The type of parameter requested from an associated
                         instrument. For this function the acceptable
                         parameters are I{primary}, I{secondary} and I{total}.
                         Default is I{primary}.
    @type inst_param: C{string}

    @keyword pixel_id: The pixel ID from which the geometry information will
                       be retrieved from the instrument
    @type pixel_id: C{tuple}=(\"bankN\", (x, y))


    @return: A converted number for every unique spectrum
    @rtype: C{list} of C{tuple}s


    @raise AttributeError: The requested function is not in the approved
                           list
    """
    # Setup supported function list and check to see if funcname is available
    function_list = []
    function_list.append("d_spacing_to_tof_focused_det")
    function_list.append("energy_to_wavelength")
    function_list.append("frequency_to_energy")
    function_list.append("initial_wavelength_igs_lin_time_zero_to_tof")
    function_list.append("init_scatt_wavevector_to_scalar_Q")
    function_list.append("tof_to_initial_wavelength_igs_lin_time_zero")
    function_list.append("tof_to_initial_wavelength_igs")
    function_list.append("tof_to_scalar_Q")
    function_list.append("tof_to_wavelength_lin_time_zero")
    function_list.append("tof_to_wavelength")
    function_list.append("wavelength_to_d_spacing")
    function_list.append("wavelength_to_energy")
    function_list.append("wavelength_to_scalar_k")
    function_list.append("wavelength_to_scalar_Q")

    if funcname not in function_list:
        raise AttributeError("Function %s is not supported by "\
                             +"convert_single_to_list" % funcname)

    import common_lib

    # Get the common_lib function object
    func = common_lib.__getattribute__(funcname)

    # Setup inclusive dictionary containing the requested keywords for all
    # common_lib axis conversion functions

    fkwds = {}
    fkwds["pathlength"] = ()
    fkwds["polar"] = ()
    fkwds["lambda_f"] = ()
    try:
        lambda_final = som.attr_list["Wavelength_final"]
    except KeyError:
        lambda_final = None
    try:
        fkwds["time_zero_slope"] = som.attr_list["Time_zero_slope"]
    except KeyError:
        pass
    try:
        fkwds["time_zero_offset"] = som.attr_list["Time_zero_offset"]
    except KeyError:
        pass
    try:
        fkwds["time_zero"] = som.attr_list["Time_zero"]
    except KeyError:
        pass    
    fkwds["dist_source_sample"] = ()
    fkwds["dist_sample_detector"] = ()
    try:
        fkwds["inst_param"] = kwargs["inst_param"]
    except KeyError:
        fkwds["inst_param"]  = "primary"
    try:
        fkwds["pixel_id"] = kwargs["pixel_id"]
    except KeyError:
        fkwds["pixel_id"]  = None
    fkwds["run_filter"] = False

    # Set up for working through data
    # This time highest object in the hierarchy is NOT what we need
    result = []
    res_descr = "list"

    inst = som.attr_list.instrument
    
    import hlr_utils

    # iterate through the values
    for i in xrange(hlr_utils.get_length(som)):
        map_so = hlr_utils.get_map_so(som, None, i)
        
        fkwds["pathlength"] = hlr_utils.get_parameter(fkwds["inst_param"],
                                                      map_so, inst)
        
        fkwds["dist_source_sample"] = hlr_utils.get_parameter("primary",
                                                              map_so, inst)

        fkwds["dist_sample_detector"] = hlr_utils.get_parameter("secondary",
                                                                map_so, inst)

        fkwds["polar"] = hlr_utils.get_parameter("polar", map_so, inst)

        fkwds["lambda_f"] = hlr_utils.get_special(lambda_final, map_so)

        value = tuple(func(number, **fkwds))

        hlr_utils.result_insert(result, res_descr, value, None, "all")

    return result
