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

def create_E_vs_Q_dgs(som, E_i, Q_final, **kwargs):
    """
    This function starts with the rebinned energy transfer and turns this
    into a 2D spectra with E and Q axes for DGS instruments.

    @param som: The input object with initial IGS wavelength axis
    @type som: C{SOM.SOM}

    @param E_i: The initial energy for the given data.
    @type E_i: C{tuple}

    @param Q_final: The momentum transfer axis to rebin the data to
    @type Q_final: C{nessi_list.NessiList}

    @param kwargs: A list of keyword arguments that the function accepts:

    @keyword corner_geom: The filename that contains the corner geometry
                          information.
    @type corner_geom: C{string}

    @keyword configure: This is the object containing the driver configuration.
    @type configure: C{Configure}

    @keyword timer: Timing object so the function can perform timing estimates.
    @type timer: C{sns_timer.DiffTime}    
    """
    import array_manip
    import axis_manip
    import common_lib
    import hlr_utils
    import nessi_list
    import SOM

    # Check keywords
    t = kwargs.get("timer")

    # Check for the corner geometry file
    corner_geom = kwargs.get("corner_geom", "")

    # Check for configure keyword
    configure = kwargs.get("configure")

    # Setup output object
    so_dim = SOM.SO(dim)

    so_dim.axis[0].val = Q_final
    so_dim.axis[1].val = som[0].axis[0].val # E_t
    
    # Calculate total 2D array size
    N_tot = len(so_dim.axis[0].val) * len(so_dim.axis[1].val)

    # Create y and var_y lists from total 2D size
    so_dim.y = nessi_list.NessiList(N_tot)
    so_dim.var_y = nessi_list.NessiList(N_tot)

    # Create area sum and errors for the area sum lists from total 2D size
    area_sum = nessi_list.NessiList(N_tot)
    area_sum_err2 = nessi_list.NessiList(N_tot)

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

        cangles = corner_angles[str(map_so.id)]

        (Q1, Q1_err2) = axis_manip.init_scatt_wavevector_to_scalar_Q(k_i[0],
                                                                     k_i[1],
                                                                     k_f[0],
                                                                     k_f[1],
                                                           cangles.getPolar(0),
                                                                     0.0)
        
        (Q2, Q2_err2) = axis_manip.init_scatt_wavevector_to_scalar_Q(k_i[0],
                                                                     k_i[1],
                                                                     k_f[0],
                                                                     k_f[1],
                                                           cangles.getPolar(1),
                                                                     0.0)

        (Q3, Q3_err2) = axis_manip.init_scatt_wavevector_to_scalar_Q(k_i[0],
                                                                     k_i[1],
                                                                     k_f[0],
                                                                     k_f[1],
                                                           cangles.getPolar(2),
                                                                     0.0)

        (Q4, Q4_err2) = axis_manip.init_scatt_wavevector_to_scalar_Q(k_i[0],
                                                                     k_i[1],
                                                                     k_f[0],
                                                                     k_f[1],
                                                           cangles.getPolar(3),
                                                                     0.0)
        try:
            (y_2d, y_2d_err2,
             area_new) = axis_manip.rebin_2D_quad_to_rectlin(Q_1, E_t_1,
                                                           Q_2, E_t_2,
                                                           Q_3, E_t_3,
                                                           Q_4, E_t_4,
                                                           counts,
                                                           counts_err2,
                                                           so_dim.axis[0].val,
                                                           so_dim.axis[1].val)
        except IndexError, e:
            # Get the offending index from the error message
            index = int(str(e).split()[1].split('index')[-1].strip('[]'))
            print "Id:", map_so.id
            print "Index:", index
            print "Verticies: %f, %f, %f, %f, %f, %f, %f, %f" % (Q_1[index],
                                                                 E_t_1[index],
                                                                 Q_2[index],
                                                                 E_t_2[index],
                                                                 Q_3[index],
                                                                 E_t_3[index],
                                                                 Q_4[index],
                                                                 E_t_4[index])
            raise IndexError(str(e))

        # Add in together with previous results
        (so_dim.y, so_dim.var_y) = array_manip.add_ncerr(so_dim.y,
                                                         so_dim.var_y,
                                                         y_2d, y_2d_err2)
        
        (area_sum, area_sum_err2) = array_manip.add_ncerr(area_sum,
                                                          area_sum_err2,
                                                          area_new,
                                                          area_sum_err2)

    return None
