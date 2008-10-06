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

def create_Qvec_vs_E_dgs(som, E_i, **kwargs):
    """
    This function starts with the energy transfer axis from DGS reduction and
    turns this into a 4D spectra with Qx, Qy, Qz and Et axes.

    @param som: The input object with initial IGS wavelength axis
    @type som: C{SOM.SOM}

    @param E_i: The initial energy for the given data.
    @type E_i: C{tuple}

    @param kwargs: A list of keyword arguments that the function accepts:

    @keyword timer: Timing object so the function can perform timing estimates.
    @type timer: C{sns_timer.DiffTime}

    @keyword corner_geom: The filename that contains the corner geometry
                          information.
    @type corner_geom: C{string}
    """
    import array_manip
    import axis_manip
    import common_lib
    import hlr_utils

    # Check keywords
    try:
        t = kwargs["timer"]
    except KeyError:
        t = None

    try:
        corner_geom = kwargs["corner_geom"]
    except KeyError:
        corner_geom = ""

    # Convert initial energy to initial wavevector
    l_i = common_lib.energy_to_wavelength(E_i)
    k_i = common_lib.wavelength_to_scalar_k(l_i)

    # Since all the data is rebinned to the same energy transfer axis, we can
    # calculate the final energy axis once
    E_t = som[0].axis[0].val
    if som[0].axis[0].var is not None:
        E_t_err2 = som[0].axis[0].var
    else:
        import nessi_list
        E_t_err2 = nessi_list.NessiList(len(E_t))        

    E_f = array_manip.sub_ncerr(E_i[0], E_i[1], E_t, E_t_err2)
    
    # Now we can get the final wavevector
    l_f = axis_manip.energy_to_wavelength(E_f[0], E_f[1])
    k_f = axis_manip.wavelength_to_scalar_k(l_f[0], l_f[1])

    # Grab the instrument from the som
    inst = som.attr_list.instrument

    # Get the corner geoemetry information
    if t is not None:
        t.getTime(False)
        
    corner_angles = hlr_utils.get_corner_geometry(corner_geom)

    if t is not None:
        t.getTime(msg="After reading in corner geometry information ")

    # Iterate though the data
    len_som = hlr_utils.get_length(som)
    for i in xrange(len_som):
        map_so = hlr_utils.get_map_so(som, None, i)

        yval = hlr_utils.get_value(som, i, "SOM", "y")
        yerr2 = hlr_utils.get_err2(som, i, "SOM", "y")

        polar = hlr_utils.get_parameter("polar", map_so, inst)
        azi = hlr_utils.get_parameter("azimuthal", map_so, inst)

        (Qx, Qx_err2,
         Qy, Qy_err2,
         Qz, Qz_err2) = axis_manip.init_scatt_wavevector_to_Q(k_i[0], k_i[1],
                                                              k_f[0], k_f[1],
                                                              azi[0], azi[1],
                                                              polar[0],
                                                              polar[1])
