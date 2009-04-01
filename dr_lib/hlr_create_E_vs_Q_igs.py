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

import array_manip
import axis_manip
import hlr_utils
import SOM

def create_E_vs_Q_igs(som, *args, **kwargs):
    """
    This function starts with the initial IGS wavelength axis and turns this
    into a 2D spectra with E and Q axes.

    @param som: The input object with initial IGS wavelength axis
    @type som: C{SOM.SOM}

    @param args: A mandatory list of axes for rebinning. There is a particular
                 order to them. They should be present in the following order:

                 Without errors
                   1. Energy transfer
                   2. Momentum transfer
                 With errors
                   1. Energy transfer
                   2. Energy transfer error^2
                   3. Momentum transfer
                   4. Momentum transfer error ^2
    @type args: C{nessi_list.NessiList}s
       
    @param kwargs: A list of keyword arguments that the function accepts:

    @keyword withXVar: Flag for whether the function should be expecting the
                       associated axes to have errors. The default value will
                       be I{False}.
    @type withXVar: C{boolean}

    @keyword data_type: Name of the data type which can be either I{histogram},
                        I{density} or I{coordinate}. The default value will be
                        I{histogram}
    @type data_type: C{string}
    
    @keyword Q_filter: Flag to turn on or off Q filtering. The default behavior
                       is I{True}.
    @type Q_filter: C{boolean}
    
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


    @return: Object containing a 2D C{SO} with E and Q axes
    @rtype: C{SOM.SOM}


    @raise RuntimeError: Anything other than a C{SOM} is passed to the function
    
    @raise RuntimeError: An instrument is not contained in the C{SOM}
    """
    import nessi_list

    # Setup some variables 
    dim = 2
    N_y = []
    N_tot = 1
    N_args = len(args)

    # Get T0 slope in order to calculate dT = dT_i + dT_0
    try:
        t_0_slope = som.attr_list["Time_zero_slope"][0]
        t_0_slope_err2 = som.attr_list["Time_zero_slope"][1]
    except KeyError:
        t_0_slope = float(0.0)
        t_0_slope_err2 = float(0.0)

    # Check withXVar keyword argument and also check number of given args.
    # Set xvar to the appropriate value
    try:
        value = kwargs["withXVar"]
        if value.lower() == "true":
            if N_args != 4:
                raise RuntimeError("Since you have requested x errors, 4 x "\
                                   +"axes must be provided.")
            else:
                xvar = True
        elif value.lower() == "false":
            if N_args != 2:
                raise RuntimeError("Since you did not requested x errors, 2 "\
                                   +"x axes must be provided.")
            else:
                xvar = False
        else:
            raise RuntimeError("Do not understand given parameter %s" % \
                               value)
    except KeyError:
        if N_args != 2:
            raise RuntimeError("Since you did not requested x errors, 2 "\
                               +"x axes must be provided.")
        else:
            xvar = False

    # Check dataType keyword argument. An offset will be set to 1 for the
    # histogram type and 0 for either density or coordinate
    try:
        data_type = kwargs["data_type"]
        if data_type.lower() == "histogram":
            offset = 1
        elif data_type.lower() == "density" or \
                 data_type.lower() == "coordinate":
            offset = 0
        else:
            raise RuntimeError("Do not understand data type given: %s" % \
                               data_type)
    # Default is offset for histogram
    except KeyError:
        offset = 1

    try:
        Q_filter = kwargs["Q_filter"]
    except KeyError:
        Q_filter = True

    # Check for split keyword
    try:
        split = kwargs["split"]
    except KeyError:
        split = False

    # Check for configure keyword
    try:
        configure = kwargs["configure"]
    except KeyError:
        configure = None

    so_dim = SOM.SO(dim)

    for i in range(dim):
        # Set the x-axis arguments from the *args list into the new SO
        if not xvar:
            # Axis positions are 1 (Q) and 0 (E)
            position = dim - i - 1
            so_dim.axis[i].val = args[position]
        else:
            # Axis positions are 2 (Q), 3 (eQ), 0 (E), 1 (eE)
            position = dim - 2 * i
            so_dim.axis[i].val = args[position]
            so_dim.axis[i].var = args[position + 1]

        # Set individual value axis sizes (not x-axis size)
        N_y.append(len(args[position]) - offset)

        # Calculate total 2D array size
        N_tot = N_tot * N_y[-1]

    # Create y and var_y lists from total 2D size
    so_dim.y = nessi_list.NessiList(N_tot)
    so_dim.var_y = nessi_list.NessiList(N_tot)
    
    # Create area sum and errors for the area sum lists from total 2D size
    area_sum = nessi_list.NessiList(N_tot)
    area_sum_err2 = nessi_list.NessiList(N_tot)

    # Create area sum and errors for the area sum lists from total 2D size
    bin_count = nessi_list.NessiList(N_tot)
    bin_count_err2 = nessi_list.NessiList(N_tot)
    
    inst = som.attr_list.instrument
    lambda_final = som.attr_list["Wavelength_final"]
    inst_name = inst.get_name()

    import bisect
    import math

    import dr_lib
    import utils

    arr_len = 0
    #: Vector of zeros for function calculations
    zero_vec = None
    
    for j in xrange(hlr_utils.get_length(som)):
        # Get counts
        counts = hlr_utils.get_value(som, j, "SOM", "y")
        counts_err2 = hlr_utils.get_err2(som, j, "SOM", "y")

        arr_len = len(counts)
        zero_vec = nessi_list.NessiList(arr_len)

        # Get mapping SO
        map_so = hlr_utils.get_map_so(som, None, j)

        # Get lambda_i
        l_i = hlr_utils.get_value(som, j, "SOM", "x")
        l_i_err2 = hlr_utils.get_err2(som, j, "SOM", "x")
        
        # Get lambda_f from instrument information
        l_f_tuple = hlr_utils.get_special(lambda_final, map_so)
        l_f = l_f_tuple[0]
        l_f_err2 = l_f_tuple[1]
        
        # Get source to sample distance
        (L_s, L_s_err2) = hlr_utils.get_parameter("primary", map_so, inst)

        # Get sample to detector distance
        L_d_tuple = hlr_utils.get_parameter("secondary", map_so, inst)
        L_d = L_d_tuple[0]

        # Get polar angle from instrument information
        (angle, angle_err2) = hlr_utils.get_parameter("polar", map_so, inst)

        # Get the detector pixel height
        dh_tuple = hlr_utils.get_parameter("dh", map_so, inst)
        dh = dh_tuple[0]
        # Need dh in units of Angstrom
        dh *= 1e10

        # Calculate T_i
        (T_i, T_i_err2) = axis_manip.wavelength_to_tof(l_i, l_i_err2, 
                                                       L_s, L_s_err2)

        # Scale counts by lambda_f / lambda_i
        (l_i_bc, l_i_bc_err2) = utils.calc_bin_centers(l_i, l_i_err2)

        (ratio, ratio_err2) = array_manip.div_ncerr(l_f, l_f_err2,
                                                    l_i_bc, l_i_bc_err2)

        (counts, counts_err2) = array_manip.mult_ncerr(counts, counts_err2,
                                                       ratio, ratio_err2)

        # Calculate E_i
        (E_i, E_i_err2) = axis_manip.wavelength_to_energy(l_i, l_i_err2)

        # Calculate E_f
        (E_f, E_f_err2) = axis_manip.wavelength_to_energy(l_f, l_f_err2)

        # Calculate E_t
        (E_t, E_t_err2) = array_manip.sub_ncerr(E_i, E_i_err2, E_f, E_f_err2)

        if inst_name == "BSS":
            # Convert E_t from meV to ueV
            (E_t, E_t_err2) = array_manip.mult_ncerr(E_t, E_t_err2,
                                                     1000.0, 0.0)
            (counts, counts_err2) = array_manip.mult_ncerr(counts, counts_err2,
                                                           1.0/1000.0, 0.0)

        # Convert lambda_i to k_i
        (k_i, k_i_err2) = axis_manip.wavelength_to_scalar_k(l_i, l_i_err2)

        # Convert lambda_f to k_f
        (k_f, k_f_err2) = axis_manip.wavelength_to_scalar_k(l_f, l_f_err2)

        # Convert k_i and k_f to Q
        (Q, Q_err2) = axis_manip.init_scatt_wavevector_to_scalar_Q(k_i,
                                                                   k_i_err2,
                                                                   k_f,
                                                                   k_f_err2,
                                                                   angle,
                                                                   angle_err2)

        # Calculate dT = dT_0 + dT_i
        dT_i = utils.calc_bin_widths(T_i, T_i_err2)

        (l_i_bw, l_i_bw_err2) = utils.calc_bin_widths(l_i, l_i_err2)
        dT_0 = array_manip.mult_ncerr(l_i_bw, l_i_bw_err2,
                                      t_0_slope, t_0_slope_err2)

        dT_tuple = array_manip.add_ncerr(dT_i[0], dT_i[1], dT_0[0], dT_0[1])
        dT = dT_tuple[0]

        # Calculate Jacobian
        if inst_name == "BSS":
            (x_1, x_2,
             x_3, x_4) = dr_lib.calc_BSS_coeffs(map_so, inst, (E_i, E_i_err2),
                                                (Q, Q_err2), (k_i, k_i_err2),
                                                (T_i, T_i_err2), dh, angle,
                                                E_f, k_f, l_f, L_s, L_d,
                                                t_0_slope, zero_vec)
        else:
            raise RuntimeError("Do not know how to calculate x_i "\
                               +"coefficients for instrument %s" % inst_name)

        (A, A_err2) = dr_lib.calc_EQ_Jacobian(x_1, x_2, x_3, x_4, dT, dh,
                                              zero_vec)
        
        # Apply Jacobian: C/dlam * dlam / A(EQ) = C/EQ
        (jac_ratio, jac_ratio_err2) = array_manip.div_ncerr(l_i_bw,
                                                            l_i_bw_err2,
                                                            A, A_err2)
        (counts, counts_err2) = array_manip.mult_ncerr(counts, counts_err2,
                                                       jac_ratio,
                                                       jac_ratio_err2)
        
        # Reverse counts, E_t, k_i and Q
        E_t = axis_manip.reverse_array_cp(E_t)
        E_t_err2 = axis_manip.reverse_array_cp(E_t_err2)
        Q = axis_manip.reverse_array_cp(Q)
        Q_err2 = axis_manip.reverse_array_cp(Q_err2)        
        counts = axis_manip.reverse_array_cp(counts)
        counts_err2 = axis_manip.reverse_array_cp(counts_err2)
        k_i = axis_manip.reverse_array_cp(k_i)
        x_1 = axis_manip.reverse_array_cp(x_1)
        x_2 = axis_manip.reverse_array_cp(x_2)
        x_3 = axis_manip.reverse_array_cp(x_3)
        x_4 = axis_manip.reverse_array_cp(x_4)
        dT = axis_manip.reverse_array_cp(dT)        

        # Filter for duplicate Q values
        if Q_filter:
            k_i_cutoff = k_f * math.cos(angle)
            k_i_cutbin = bisect.bisect(k_i, k_i_cutoff)
            
            counts.__delslice__(0, k_i_cutbin)
            counts_err2.__delslice__(0, k_i_cutbin)
            Q.__delslice__(0, k_i_cutbin)
            Q_err2.__delslice__(0, k_i_cutbin)
            E_t.__delslice__(0, k_i_cutbin)
            E_t_err2.__delslice__(0, k_i_cutbin)
            x_1.__delslice__(0, k_i_cutbin)
            x_2.__delslice__(0, k_i_cutbin)
            x_3.__delslice__(0, k_i_cutbin)
            x_4.__delslice__(0, k_i_cutbin)            
            dT.__delslice__(0, k_i_cutbin)
            zero_vec.__delslice__(0, k_i_cutbin)

        try:
            if inst_name == "BSS":
                ((Q_1, E_t_1),
                 (Q_2, E_t_2),
                 (Q_3, E_t_3),
                 (Q_4, E_t_4)) = dr_lib.calc_BSS_EQ_verticies((E_t, E_t_err2),
                                                              (Q, Q_err2), x_1,
                                                              x_2, x_3, x_4,
                                                              dT, dh, zero_vec)
            else:
                raise RuntimeError("Do not know how to calculate (Q_i, "\
                                   +"E_t_i) verticies for instrument %s" \
                                   % inst_name)

        except IndexError:
            # All the data got Q filtered, move on
            continue

        try:
            (y_2d, y_2d_err2,
             area_new,
             bin_count_new) = axis_manip.rebin_2D_quad_to_rectlin(Q_1, E_t_1,
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

        if configure.dump_pix_contrib or configure.scale_sqe:
            if inst_name == "BSS":
                dOmega = dr_lib.calc_BSS_solid_angle(map_so, inst)
                dazi = dr_lib.calc_BSS_delta_azi(map_so, inst)

                sconst = dOmega * dazi
                
                (bin_count_new,
                 bin_count_err2) = array_manip.mult_ncerr(bin_count_new,
                                                          bin_count_err2,
                                                          sconst, 0.0)
                
                (bin_count,
                 bin_count_err2) = array_manip.add_ncerr(bin_count,
                                                         bin_count_err2,
                                                         bin_count_new,
                                                         bin_count_err2)
        else:
            del bin_count_new
                
    # Check for so_id keyword argument
    try:
        so_dim.id = kwargs["so_id"]
    except KeyError:
        so_dim.id = 0

    comb_som = SOM.SOM()
    comb_som.copyAttributes(som)

    if configure.scale_sqe:
        kwargs["scaled_sqe"] = True

    comb_som = __set_som_attributes(comb_som, inst_name, **kwargs)

    if configure.dump_pix_contrib:
        som1 = SOM.SOM()
        som1.copyAttributes(comb_som)
        som1.append(SOM.SO(2, so_dim.id))
        som1[0].y = bin_count
        som1[0].var_y = bin_count_err2
        som1[0].axis[0].val = so_dim.axis[0].val
        som1[0].axis[1].val = so_dim.axis[1].val

        # Write out pixel contribution into file
        hlr_utils.write_file(configure.output, "text/Dave2d", som1,
                             output_ext="pcs",
                             verbose=configure.verbose,
                             data_ext=configure.ext_replacement,         
                             path_replacement=configure.path_replacement,
                             message="pixel contribution")

        del som1

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
        
        if configure.scale_sqe:
            (so_dim.y, so_dim.var_y) = array_manip.div_ncerr(so_dim.y,
                                                             so_dim.var_y,
                                                             bin_count,
                                                             bin_count_err2)

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
    scaled_sqe = kwargs.get("scaled_sqe", False)
    
    # Check for y_label keyword argument
    try:
        tsom.setYLabel(kwargs["y_label"])
    except KeyError:
        tsom.setYLabel("Counts")

    # Check for y_units keyword argument
    try:
        tsom.setYUnits(kwargs["y_units"])
    except KeyError:
        if inst_name == "BSS":
            if scaled_sqe:
                tsom.setYUnits("Counts / ueV A^-1 ster")
            else:
                tsom.setYUnits("Counts / ueV A^-1")
        else:
            tsom.setYUnits("Counts / meV A^-1")

    # Check for x_labels keyword argument
    try:
        tsom.setAllAxisLabels(kwargs["x_labels"])
    except KeyError:
        tsom.setAllAxisLabels(["Momentum transfer", "Energy transfer"])

    # Check for x_units keyword argument
    try:
        tsom.setAllAxisUnits(kwargs["x_units"])
    except KeyError:
        if inst_name == "BSS":
            tsom.setAllAxisUnits(["A^-1", "ueV"])
        else:
            tsom.setAllAxisUnits(["A^-1", "meV"])

    return tsom
