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

    @keyword so_id: The identifier represents a number, string, tuple or other
                    object that describes the resulting C{SO}
    @type so_id: C{int}, C{string}, C{tuple}, C{pixel ID}
    
    @keyword y_label: The y axis label
    @type y_label: C{string}
    
    @keyword y_units: The y axis units
    @type y_units: C{string}
    
    @keyword x_labels: This is a list of names that sets the individual x axis
    labels
    @type x_labels: C{list} of C{string}s
    
    @keyword x_units: This is a list of names that sets the individual x axis
    units
    @type x_units: C{list} of C{string}s

    @keyword split: This flag causes the counts and the fractional area to
                    be written out into separate files.
    @type split: C{boolean}

    @keyword configure: This is the object containing the driver configuration.
    @type configure: C{Configure}

    @keyword timer: Timing object so the function can perform timing estimates.
    @type timer: C{sns_timer.DiffTime}


    @return: Object containing a 2D C{SO} with E and Q axes
    @rtype: C{SOM.SOM}    
    """
    import array_manip
    import axis_manip
    import common_lib
    import hlr_utils
    import nessi_list
    import SOM

    # Check for keywords
    t = kwargs.get("timer")
    corner_geom = kwargs.get("corner_geom", "")
    configure = kwargs.get("configure")
    split = kwargs.get("split", False)

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

        avg_theta1 = (cangles.getPolar(0) + cangles.getPolar(1)) / 2.0
        avg_theta2 = (cangles.getPolar(2) + cangles.getPolar(3)) / 2.0

        (Q1,
         Q1_err2) = axis_manip.init_scatt_wavevector_to_scalar_Q(k_i[0][:-1],
                                                                 k_i[1][:-1],
                                                                 k_f[0],
                                                                 k_f[1],
                                                                 avg_theta1,
                                                                 0.0)
        
        (Q2,
         Q2_err2) = axis_manip.init_scatt_wavevector_to_scalar_Q(k_i[0][:-1],
                                                                 k_i[1][:-1],
                                                                 k_f[0],
                                                                 k_f[1],
                                                                 avg_theta2,
                                                                 0.0)

        (Q3,
         Q3_err2) = axis_manip.init_scatt_wavevector_to_scalar_Q(k_i[0][1:],
                                                                 k_i[1][1:],
                                                                 k_f[0],
                                                                 k_f[1],
                                                                 avg_theta1,
                                                                 0.0)

        (Q4,
         Q4_err2) = axis_manip.init_scatt_wavevector_to_scalar_Q(k_i[0][1:],
                                                                 k_i[1][1:],
                                                                 k_f[0],
                                                                 k_f[1],
                                                                 avg_theta2,
                                                                 0.0)
        try:
            (y_2d, y_2d_err2,
             area_new) = axis_manip.rebin_2D_quad_to_rectlin(Q_1, E_t[:-1],
                                                           Q_2, E_t[:-1],
                                                           Q_3, E_t[1:],
                                                           Q_4, E_t[1:],
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

    # Check for so_id keyword argument
    so_dim.id = kwargs.get("so_id", 0)

    comb_som = SOM.SOM()
    comb_som.copyAttributes(som)

    comb_som = __set_som_attributes(comb_som, inst_name, **kwargs)

    if split:
        comb_som.append(so_dim)
        
        # Write out summed counts into file
        hlr_utils.write_file(configure.output, "text/Dave2d", comb_som,
                             output_ext="cnt",
                             verbose=configure.verbose,
                             data_ext=configure.ext_replacement,         
                             path_replacement=configure.path_replacement,
                             message="summed counts")

        # Replace counts data with fractional area. The axes remain the same
        comb_som[0].y = area_sum
        comb_som[0].var_y = area_sum_err2

        # Write out summed counts into file
        hlr_utils.write_file(configure.output, "text/Dave2d", comb_som,
                             output_ext="fra",
                             verbose=configure.verbose,
                             data_ext=configure.ext_replacement,         
                             path_replacement=configure.path_replacement,
                             message="fractional area")        

    else:
        # Divide summed fractional counts by the sum of the fractional areas
        (so_dim.y, so_dim.var_y) = array_manip.div_ncerr(so_dim.y,
                                                         so_dim.var_y,
                                                         area_sum,
                                                         area_sum_err2)


        comb_som.append(so_dim)

    del so_dim
        
    return comb_som

def __set_som_attributes(tsom, inst_name, **kwargs):
    """
    This is a helper function that sets attributes for the final S(Q,E)
    C{SOM.SOM}.

    @param tsom: The input object for attribute setting
    @type tsom: C{SOM.SOM}

    @param inst_name: The short name for an instrument
    @type inst_name: C{string}

    @param kwargs: These are keywords that are specified by the main function.
    

    @return: The C{SOM.SOM} with attributes set
    @rtype: C{SOM.SOM}
    """
    # Check for y_label keyword argument
    tsom.setYLabel(kwargs.get("y_label", "Counts"))
    # Check for y_units keyword argument
    tsom.setYUnits(kwargs.get("y_units", "Counts / meV A^-1"))
    # Check for x_labels keyword argument
    tsom.setAllAxisLabels(kwargs.get("x_labels",
                                     ["Momentum transfer", "Energy transfer"]))
    # Check for x_units keyword argument
    tsom.setAllAxisUnits(kwargs.get("x_units", ["A^-1", "meV"]))
    
    return tsom
