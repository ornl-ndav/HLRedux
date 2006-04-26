def create_2D_dist(som,*args,**kwargs):
    """

    """

    import common_lib
    import hlr_utils
    import nessi_list
    import SOM

    dim = 2
    N_y = []
    N_tot = 1
    N_args = len(args)

    try:
        kwargs["withXVar"]
        xvar = True
    except KeyError:
        xvar = False

    so_dim = SOM.SO(dim)
    if not xvar:
        for i in range(dim):
            so_dim.axis[i].val = args[dim-i-1]
            N_y.append(len(args[dim-i-1]) - 1)
            N_tot = N_tot * N_y[-1]

    so_dim.y = nessi_list.NessiList(N_tot)
    so_dim.var_y = nessi_list.NessiList(N_tot)

    som1 = common_lib.rebin_axis_1D(som, args[0])

    if som != None:
        som = None

    del som

    inst = som1.attr_list.instrument

    for i in range(hlr_utils.get_length(som1)):
        so = hlr_utils.get_value(som1,i,"SOM","all")
        angle,angle_err2 = hlr_utils.get_parameter("polar",so,inst)

        for j in range(N_y[0]):
            if angle >= args[1][j] and angle < args[1][j+1]:
                index = j
                break

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
        comb_som.setYLabel("")

    if kwargs.has_key("y_units"):
        comb_som.setYUnits(kwargs["y_units"])
    else:
        comb_som.setYUnits("")

    if kwargs.has_key("x_labels"):
        comb_som.setAllAxisLabels(kwargs["x_labels"])
    else:
        comb_som.setAllAxisLabels(["",""])

    if kwargs.has_key("x_units"):
        comb_som.setAllAxisUnits(kwargs["x_units"])
    else:
        comb_som.setAllAxisUnits(["",""])

    comb_som.append(so_dim)

    return comb_som


if __name__=="__main__":
    import hlr_test
    import hlr_utils
    import SOM

    som1 = hlr_test.generate_som("histogram",1,3)
    som1.attr_list.instrument = SOM.ASG_Instrument()

    axis = hlr_utils.make_axis(0,1,0.25)

    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1]
    print "* ",som1[2]

    print "********** create_2D"
    print " som :",create_2D_dist(som1,som1[0].axis[0].val,axis)
