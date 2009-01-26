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

def create_Qvec_vs_E_dgs(som, E_i, conf, **kwargs):
    """
    This function starts with the energy transfer axis from DGS reduction and
    turns this into a 4D spectra with Qx, Qy, Qz and Et axes.

    @param som: The input object with initial IGS wavelength axis
    @type som: C{SOM.SOM}

    @param E_i: The initial energy for the given data.
    @type E_i: C{tuple}

    @param conf: Object that contains the current setup of the driver.
    @type conf: L{hlr_utils.Configure}

    @param kwargs: A list of keyword arguments that the function accepts:

    @keyword timer: Timing object so the function can perform timing estimates.
    @type timer: C{sns_timer.DiffTime}

    @keyword corner_geom: The filename that contains the corner geometry
                          information.
    @type corner_geom: C{string}

    @keyword use_file: A flag that turns on writing the information to a file.
    @type use_file: C{boolean}

    @keyword output: The output filename and or directory.
    @type output: C{string}
    """
    import array_manip
    import axis_manip
    import common_lib
    import hlr_utils

    import os
    
    # Check keywords
    try:
        t = kwargs["timer"]
    except KeyError:
        t = None

    try:
        corner_geom = kwargs["corner_geom"]
    except KeyError:
        corner_geom = ""

    try:
        use_file = kwargs["use_file"]
    except KeyError:
        use_file = False

    try:
        output = kwargs["output"]
    except KeyError:
        output = None

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

    # Check for negative final energies which will cause problems with
    # wavelength conversion due to square root
    if E_f[0][-1] < 0:
        E_f[0].reverse()
        E_f[1].reverse()
        index = 0
        for E in E_f[0]:
            if E >= 0:
                break
            index += 1
        E_f[0].__delslice__(0, index)
        E_f[1].__delslice__(0, index)
        E_f[0].reverse()
        E_f[1].reverse()

    len_E = len(E_f[0]) - 1

    # Now we can get the final wavevector
    l_f = axis_manip.energy_to_wavelength(E_f[0], E_f[1])
    k_f = axis_manip.wavelength_to_scalar_k(l_f[0], l_f[1])

    # Grab the instrument from the som
    inst = som.attr_list.instrument

    # Get the corner geoemetry information
    if t is not None:
        t.getTime(False)
        
    corner_angles = hlr_utils.get_corner_geometry(corner_geom)
    if use_file:
        import SOM
        fixed_grid = {}
        for key in corner_angles:
            so_id = SOM.NeXusId.fromString(key).toTuple()
            try:
                pathlength = inst.get_secondary(so_id)[0]
                points = []
                for j in range(4):
                    points.extend(__calc_xyz(pathlength,
                                          corner_angles[key].getPolar(j),
                                          corner_angles[key].getAzimuthal(j)))
                fixed_grid[key] = points
            except KeyError:
                # Pixel ID is not in instrument geometry
                pass

    if t is not None:
        t.getTime(msg="After reading in corner geometry information ")

    CNT = {}
    ERR2 = {}
    V1 = {}
    V2 = {}
    V3 = {}
    V4 = {}

    if t is not None:
        t.getTime(False)

    # Iterate though the data
    len_som = hlr_utils.get_length(som)
    for i in xrange(len_som):
        map_so = hlr_utils.get_map_so(som, None, i)

        yval = hlr_utils.get_value(som, i, "SOM", "y")
        yerr2 = hlr_utils.get_err2(som, i, "SOM", "y")

        CNT[str(map_so.id)] = yval
        ERR2[str(map_so.id)] = yerr2

        polar = hlr_utils.get_parameter("polar", map_so, inst)
        azi = hlr_utils.get_parameter("azimuthal", map_so, inst)

        cangles = corner_angles[str(map_so.id)]

        (Qx1, Qx1_err2,
         Qy1, Qy1_err2,
         Qz1, Qz1_err2) = axis_manip.init_scatt_wavevector_to_Q(k_i[0], k_i[1],
                                                       k_f[0], k_f[1],
                                                       cangles.getAzimuthal(0),
                                                       0.0,
                                                       cangles.getPolar(0),
                                                       0.0)
        V1[str(map_so.id)] = {}
        V1[str(map_so.id)]["x"] = Qx1
        V1[str(map_so.id)]["y"] = Qy1
        V1[str(map_so.id)]["z"] = Qz1
        

        (Qx2, Qx2_err2,
         Qy2, Qy2_err2,
         Qz2, Qz2_err2) = axis_manip.init_scatt_wavevector_to_Q(k_i[0], k_i[1],
                                                       k_f[0], k_f[1],
                                                       cangles.getAzimuthal(1),
                                                       0.0,
                                                       cangles.getPolar(1),
                                                       0.0)

        V2[str(map_so.id)] = {}
        V2[str(map_so.id)]["x"] = Qx2
        V2[str(map_so.id)]["y"] = Qy2
        V2[str(map_so.id)]["z"] = Qz2
        
        (Qx3, Qx3_err2,
         Qy3, Qy3_err2,
         Qz3, Qz3_err2) = axis_manip.init_scatt_wavevector_to_Q(k_i[0], k_i[1],
                                                       k_f[0], k_f[1],
                                                       cangles.getAzimuthal(2),
                                                       0.0,
                                                       cangles.getPolar(2),
                                                       0.0)
        V3[str(map_so.id)] = {}
        V3[str(map_so.id)]["x"] = Qx3
        V3[str(map_so.id)]["y"] = Qy3
        V3[str(map_so.id)]["z"] = Qz3
        
        (Qx4, Qx4_err2,
         Qy4, Qy4_err2,
         Qz4, Qz4_err2) = axis_manip.init_scatt_wavevector_to_Q(k_i[0], k_i[1],
                                                       k_f[0], k_f[1],
                                                       cangles.getAzimuthal(3),
                                                       0.0,
                                                       cangles.getPolar(3),
                                                       0.0)

        V4[str(map_so.id)] = {}
        V4[str(map_so.id)]["x"] = Qx4
        V4[str(map_so.id)]["y"] = Qy4
        V4[str(map_so.id)]["z"] = Qz4

        del Qx1_err2, Qy1_err2, Qz1_err2, Qx2_err2, Qy2_err2, Qz2_err2
        del Qx3_err2, Qy3_err2, Qz3_err2, Qx4_err2, Qy4_err2, Qz4_err2

    if t is not None:
        t.getTime(msg="After calculating verticies ")

    # Form the messages
    if t is not None:
        t.getTime(False)

    jobstr = 'MR' + hlr_utils.create_binner_string(conf) + 'JH'
    num_lines = len(CNT) * len_E
    linestr = str(num_lines)
    gridstr='FV '
    if conf.Qx_bins is not None and conf.Qy_bins is not None and \
           conf.Qz_bins is not None:
        axis_info = []
        axis_info.append(str(conf.Qx_bins.getMinimum()))
        axis_info.append(str(conf.Qy_bins.getMinimum()))
        axis_info.append(str(conf.Qz_bins.getMinimum()))
        
        axis_info.append(str(conf.Qx_bins.getMaximum()))
        axis_info.append(str(conf.Qy_bins.getMinimum()))
        axis_info.append(str(conf.Qz_bins.getMinimum()))
        
        axis_info.append(str(conf.Qx_bins.getMaximum()))
        axis_info.append(str(conf.Qy_bins.getMaximum()))
        axis_info.append(str(conf.Qz_bins.getMinimum()))
        
        axis_info.append(str(conf.Qx_bins.getMinimum()))
        axis_info.append(str(conf.Qy_bins.getMaximum()))
        axis_info.append(str(conf.Qz_bins.getMinimum()))
        
        axis_info.append(str(conf.Qx_bins.getMinimum()))
        axis_info.append(str(conf.Qy_bins.getMinimum()))
        axis_info.append(str(conf.Qz_bins.getMaximum()))
        
        axis_info.append(str(conf.Qx_bins.getMaximum()))
        axis_info.append(str(conf.Qy_bins.getMinimum()))
        axis_info.append(str(conf.Qz_bins.getMaximum()))
        
        axis_info.append(str(conf.Qx_bins.getMaximum()))
        axis_info.append(str(conf.Qy_bins.getMaximum()))
        axis_info.append(str(conf.Qz_bins.getMaximum()))
        
        axis_info.append(str(conf.Qx_bins.getMinimum()))
        axis_info.append(str(conf.Qy_bins.getMaximum()))
        axis_info.append(str(conf.Qz_bins.getMaximum()))
        
        axis_info.append(str(len(conf.Qx_bins.toNessiList()) - 1))
        axis_info.append(str(len(conf.Qy_bins.toNessiList()) - 1))
        axis_info.append(str(len(conf.Qz_bins.toNessiList()) - 1))
        gridstr += " ".join(axis_info)
    else:
        # No final axis information, do nothing
        pass
    gridstr += ' FV'
        
    if use_file:
        if output is not None:
            outdir = os.path.dirname(output)
            if outdir != '':
                if outdir.rfind('.') != -1:
                    outdir = ""
        else:
            outdir = ""

        topdir = os.path.join(outdir, 
                              str(som.attr_list["data-run_number"].getValue()\
                                  + "-mesh"))
        try:
            os.mkdir(topdir)
        except OSError:
            pass

        outtag = os.path.basename(output)
        if outtag.rfind('.') == -1:
            outtag = ""
        else:
            outtag = outtag.split('.')[0]

        if outtag != "":
            filehead = outtag + "_bmesh"
            filehead1 = outtag + "_fgrid"
        else:
            filehead = "bmesh"
            filehead1 = "fgrid"

        hfile = open(os.path.join(topdir, "conf.in"), "w")
        print >> hfile, jobstr
        print >> hfile, linestr
        print >> hfile, gridstr
        hfile.close()

    for k in xrange(len_E):
        if use_file:
            ofile = open(os.path.join(topdir, "%s%04d.in" % (filehead, k)),
                         "w")
            ofile1 = open(os.path.join(topdir, "%s%04d.in" % (filehead1, k)),
                          "w")
        for id in CNT:
            result = []
            result.append(str(k))
            result.append(str(CNT[id][k]))
            result.append(str(ERR2[id][k]))
            __get_coords(V1, id, k, result)
            __get_coords(V2, id, k, result)
            __get_coords(V3, id, k, result)
            __get_coords(V4, id, k, result)
            __get_coords(V1, id, k+1, result)
            __get_coords(V2, id, k+1, result)
            __get_coords(V3, id, k+1, result)
            __get_coords(V4, id, k+1, result)

            if use_file:
                print >> ofile, " ".join(result)
                result1 = []
                result1.append(str(k))
                result1.append(str(CNT[id][k]))
                result1.append(str(ERR2[id][k]))
                result1.extend([str(x) for x in fixed_grid[id]])
                print >> ofile1, " ".join(result1)

        if use_file:
            ofile.close()
            ofile1.close()

    if t is not None:
        t.getTime(msg="After creating messages ")
            
def __get_coords(coords, id, index, output):
    output.append(str(coords[id]["x"][index]))
    output.append(str(coords[id]["y"][index]))
    output.append(str(coords[id]["z"][index]))

def __calc_xyz(r, theta, phi):
    import math
    x = r * math.sin(theta) * math.sin(phi)
    y = r * math.sin(theta) * math.cos(phi)
    z = r * math.cos(theta)
    return (x, y, z)
