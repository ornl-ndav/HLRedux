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

def create_2D_dist(som,*args,**kwargs):
    """
    This function takes a SOM of single spectrum with energy transfer axes and
    rebins those axes to a given axis and converts the spectra into a single
    I(Q,E) spectrum.

    Parameters:
    ----------
    -> som is the input SOM with energy transfer axis SOs
    -> *args is a list of axes for rebinning.  There is a particulare order
       to them. They should be present in the following order:
       1. Energy transfer
       2. Momentum transfer
    -> **kwargs is a dictionary of keywords that pass information to the
       function. Here are the currently accepted keywords:
       - withXVar=True or False. If the keyword is not present, the default
                  value will be False
       - data_type=histogram or density or coordinate. If the keyword is not
                   present, the default value will be histogram

    Returns:
    -------
    <- A SOM with a single 2D SO with E and Q axes

    Exceptions:
    ----------
    <- RuntimeError is raised if the parameter given to the keyword argument
       withXVar is not True or False
    <- RuntimeError is raised if the parameter given to the keyword argument
       data_type is not histogram or density or coordinate
    """

    import common_lib
    import hlr_utils
    import nessi_list
    import SOM

    dim = 2
    N_y = []
    N_tot = 1
    N_args = len(args)

    # Check withXVar keyword argument
    try:
        value = kwargs["withXVar"]
        if value.lower() == "true":
            xvar = True
        elif value.lower() == "false":
            xvar = False
        else:
            raise RuntimeError, "Do not understand given parameter %s" % \
                  value
    except KeyError:
        xvar = False

    # Check dataType keyword argument. An offset will be set to 1 for the
    # histogram type and 0 for either density or coordinate
    try:
        type = kwargs["data_type"]
        if type.lower() == "histogram":
            offset = 1
        elif type.lower() == "density" or type.lower() == "coordinate":
            offset = 0
        else:
            raise RuntimeError, "Do not understand data type given: %s" % \
                  type
    # Default is offset for histogram
    except KeyError:
        offset = 1

    so_dim = SOM.SO(dim)
    if not xvar:
        for i in range(dim):
            so_dim.axis[i].val = args[dim-i-1]
            N_y.append(len(args[dim-i-1]) - offset)
            N_tot = N_tot * N_y[-1]

    so_dim.y = nessi_list.NessiList(N_tot)
    so_dim.var_y = nessi_list.NessiList(N_tot)

    som1 = common_lib.rebin_axis_1D(som, args[0])

    if som != None:
        som = None

    del som

    inst = som1.attr_list.instrument
    lambda_final = som1.attr_list["Wavelength_final"]

    import axis_manip
    
    for i in range(hlr_utils.get_length(som1)):
        so = hlr_utils.get_value(som1,i,"SOM","all")
        (angle,angle_err2) = hlr_utils.get_parameter("polar",so,inst)
        
        (Q,Q_err2) = axis_manip.wavelength_to_scalar_Q(lambda_final[0],
                                                       lambda_final[1],
                                                       angle/2.0,
                                                       angle_err2/2.0)

        index = -1
        for j in range(N_y[0]):
            if Q >= args[1][j] and Q < args[1][j+1]:
                index = j
                break

        if index != -1:
            start = index * N_y[1]
            finish = (index + 1) * N_y[1]
            
            so_temp = SOM.SO()
            so_temp.y.extend(so_dim.y[index*N_y[1]:(index+1)*N_y[1]])
            so_temp.var_y.extend(so_dim.var_y[index*N_y[1]:(index+1)*N_y[1]])
            
            so_temp = common_lib.add_ncerr(so, so_temp)
            
            q = 0
            for k in range(start,finish):
                so_dim.y[k] = so_temp.y[q]
                so_dim.var_y[k] = so_temp.var_y[q]
                q += 1

    if kwargs.has_key("so_id"):
        so_dim.id = kwargs["so_id"]
    else:
        so_dim.id = 0

    comb_som = SOM.SOM()
    comb_som.copyAttributes(som1)

    if kwargs.has_key("y_label"):
        comb_som.setYLabel(kwargs["y_label"])
    else:
        comb_som.setYLabel("Counts")

    if kwargs.has_key("y_units"):
        comb_som.setYUnits(kwargs["y_units"])
    else:
        comb_som.setYUnits("Counts / THz A^-1")

    if kwargs.has_key("x_labels"):
        comb_som.setAllAxisLabels(kwargs["x_labels"])
    else:
        comb_som.setAllAxisLabels(["Momentum transfer","Energy transfer"])

    if kwargs.has_key("x_units"):
        comb_som.setAllAxisUnits(kwargs["x_units"])
    else:
        comb_som.setAllAxisUnits(["A^-1","THz"])

    comb_som.append(so_dim)

    return comb_som


if __name__=="__main__":
    import hlr_test
    import hlr_utils
    import SOM

    som1 = hlr_test.generate_som("histogram",1,3)
    som1.attr_list["Wavelength_final"] = (1,1)
    som1.attr_list.instrument = SOM.ASG_Instrument()

    axis = hlr_utils.make_axis(4,5,0.25)

    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1]
    print "* ",som1[2]

    print "********** create_2D"
    print " som :",create_2D_dist(som1,som1[0].axis[0].val,axis)
