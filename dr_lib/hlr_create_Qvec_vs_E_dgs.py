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

    @keyword corner_angles: The object that contains the corner geometry
                            information.
    @type corner_angles: C{dict}

    @keyword make_fixed: A flag that turns on writing the fixed grid mesh
                         information to a file.
    @type make_fixed: C{boolean}

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

    corner_angles = kwargs["corner_angles"]

    try:
        make_fixed = kwargs["make_fixed"]
    except KeyError:
        make_fixed = False

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

    if make_fixed:
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

    CNT = {}
    ERR2 = {}
    V1 = {}
    V2 = {}
    V3 = {}
    V4 = {}
    # Output positions for Qx, Qy, Qz coordinates
    X = 0
    Y = 2
    Z = 4

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

        cangles = corner_angles[str(map_so.id)]

        Q1 = axis_manip.init_scatt_wavevector_to_Q(k_i[0], k_i[1],
                                                   k_f[0], k_f[1],
                                                   cangles.getAzimuthal(0),
                                                   0.0,
                                                   cangles.getPolar(0),
                                                   0.0)
        V1[str(map_so.id)] = {}
        V1[str(map_so.id)]["x"] = Q1[X]
        V1[str(map_so.id)]["y"] = Q1[Y]
        V1[str(map_so.id)]["z"] = Q1[Z]
        

        Q2 = axis_manip.init_scatt_wavevector_to_Q(k_i[0], k_i[1],
                                                   k_f[0], k_f[1],
                                                   cangles.getAzimuthal(1),
                                                   0.0,
                                                   cangles.getPolar(1),
                                                   0.0)

        V2[str(map_so.id)] = {}
        V2[str(map_so.id)]["x"] = Q2[X]
        V2[str(map_so.id)]["y"] = Q2[Y]
        V2[str(map_so.id)]["z"] = Q2[Z]
        
        Q3 = axis_manip.init_scatt_wavevector_to_Q(k_i[0], k_i[1],
                                                   k_f[0], k_f[1],
                                                   cangles.getAzimuthal(2),
                                                   0.0,
                                                   cangles.getPolar(2),
                                                   0.0)
        V3[str(map_so.id)] = {}
        V3[str(map_so.id)]["x"] = Q3[X]
        V3[str(map_so.id)]["y"] = Q3[Y]
        V3[str(map_so.id)]["z"] = Q3[Z]
        
        Q4 = axis_manip.init_scatt_wavevector_to_Q(k_i[0], k_i[1],
                                                   k_f[0], k_f[1],
                                                   cangles.getAzimuthal(3),
                                                   0.0,
                                                   cangles.getPolar(3),
                                                   0.0)

        V4[str(map_so.id)] = {}
        V4[str(map_so.id)]["x"] = Q4[X]
        V4[str(map_so.id)]["y"] = Q4[Y]
        V4[str(map_so.id)]["z"] = Q4[Z]

    if t is not None:
        t.getTime(msg="After calculating verticies ")

    # Form the messages
    if t is not None:
        t.getTime(False)

    jobstr = 'MR' + hlr_utils.create_binner_string(conf) + 'JH'
    num_lines = len(CNT) * len_E
    linestr = str(num_lines)

    if output is not None:
        outdir = os.path.dirname(output)
        if outdir != '':
            if outdir.rfind('.') != -1:
                outdir = ""
    else:
        outdir = ""

    value = str(som.attr_list["data-run_number"].getValue()).split('/')

    topdir = os.path.join(outdir, value[0].strip() + "-mesh")
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
        if make_fixed:
            filehead1 = outtag + "_fgrid"
        filehead2 = outtag + "_conf"
    else:
        filehead = "bmesh"
        if make_fixed:    
            filehead1 = "fgrid"
        filehead2 = "conf"

    hfile = open(os.path.join(topdir, "%s.in" % filehead2), "w")
    print >> hfile, jobstr
    print >> hfile, linestr
    hfile.close()

    for k in xrange(len_E):
        ofile = open(os.path.join(topdir, "%s%04d.in" % (filehead, k)), "w")
        if make_fixed:
            ofile1 = open(os.path.join(topdir, "%s%04d.in" % (filehead1, k)),
                          "w")
        for pid in CNT:
            result = []
            result.append(str(k))
            result.append(str(E_t[k]))
            result.append(str(E_t[k+1]))
            result.append(str(CNT[pid][k]))
            result.append(str(ERR2[pid][k]))
            __get_coords(V1, pid, k, result)
            __get_coords(V2, pid, k, result)
            __get_coords(V3, pid, k, result)
            __get_coords(V4, pid, k, result)
            __get_coords(V1, pid, k+1, result)
            __get_coords(V2, pid, k+1, result)
            __get_coords(V3, pid, k+1, result)
            __get_coords(V4, pid, k+1, result)


            print >> ofile, " ".join(result)

            if make_fixed:
                result1 = []
                result1.append(str(k))
                result1.append(str(E_t[k]))
                result1.append(str(E_t[k+1]))
                result1.append(str(CNT[pid][k]))
                result1.append(str(ERR2[pid][k]))
                result1.extend([str(x) for x in fixed_grid[pid]])
                print >> ofile1, " ".join(result1)

        ofile.close()
        if make_fixed:
            ofile1.close()

    if t is not None:
        t.getTime(msg="After creating messages ")
            
def __get_coords(coords, pid, index, output):
    output.append(str(coords[pid]["x"][index]))
    output.append(str(coords[pid]["y"][index]))
    output.append(str(coords[pid]["z"][index]))

def __calc_xyz(r, theta, phi):
    import math
    x = r * math.sin(theta) * math.cos(phi)
    y = r * math.sin(theta) * math.sin(phi)
    z = r * math.cos(theta)
    return (x, y, z)
