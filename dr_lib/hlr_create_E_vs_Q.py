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

def create_E_vs_Q(obj,E,k,px_separate=True,*args,**kwargs):
    """
    This functions takes a SOM with a wavelength axis, energy and wavevector
    tuples and turns the SOs contained in the SOM to 2D SOs with E and Q axes.

    Parameters:
    ----------
    -> obj is the input SOM
    -> E (E_f for IGS) is an energy tuple (value, err2)
    -> k (k_f for IGS) is an wavevector tuple (value, err2)

    Returns:
    -------
    <- A SOM containing 2D SOs with E and Q axes

    Exceptions:
    ----------
    <- RuntimeError is raised if anything other than a SOM is passed to the
       function
    <- RuntimeError is raised if an instrument is not contained in the SOM
    """

    import hlr_utils

    # set up for working through data
    (result,res_descr)=hlr_utils.empty_result(obj)
    (o_descr,d_descr)=hlr_utils.get_descr(obj)

    if o_descr != "SOM":
        raise RuntimeError, "This function only accepts SOMs"

    if o_descr == "SOM":
        try:
            obj.attr_list.instrument.get_primary()
            inst = obj.attr_list.instrument
        except RuntimeError:
            raise RuntimeError, "An instrument was not provided!"

    axis = hlr_utils.hlr_1D_units(obj, "Angstroms")

    result=hlr_utils.copy_som_attr(result,res_descr,obj,o_descr)
    result.setYLabel("counts")
    result.setYUnits("counts / (ueV * A^-1)")
    result.setAllAxisLabels(["Q transfer","energy transfer"])
    result.setAllAxisUnits(["A^-1","ueV"])

    # iterate through the values
    import array_manip
    import axis_manip
    import nessi_list
    import SOM

    y_len = len(obj[0])
    y2d_len = y_len * y_len

    for j in range(hlr_utils.get_length(obj)):

        xval = hlr_utils.get_value(obj,j,o_descr,"x",axis)
        xerr2 = hlr_utils.get_err2(obj,j,o_descr,"x",axis)

        k_j=axis_manip.wavelength_to_scalar_k(xval, xerr2)
        E_j=axis_manip.wavelength_to_energy(xval, xerr2)

        yval = hlr_utils.get_value(obj,j,o_descr,"y")
        yerr2 = hlr_utils.get_err2(obj,j,o_descr,"y")

        yval = axis_manip.reverse_array_cp(yval)
        yerr2 = axis_manip.reverse_array_cp(yerr2)

        so = hlr_utils.get_value(obj,j,o_descr,"all")
        (angle,angle_err2) = hlr_utils.get_parameter("polar",so,inst)

        E_t=axis_manip.energy_transfer(E_j[0], E_j[1], E[0], E[1])
        E_t=axis_manip.frequency_to_energy(E_t[0], E_t[1])
        E_t=array_manip.mult_ncerr(E_t[0], E_t[1], 1000.0, 0.0)
        
        Q=axis_manip.init_scatt_wavevector_to_scalar_Q(k_j[0], k_j[1],
                                                       k[0], k[1],
                                                       angle, angle_err2)

        so2 = SOM.SO(2)
        so2.id = so.id
        so2.y = nessi_list.NessiList(y2d_len)
        so2.var_y = nessi_list.NessiList(y2d_len)

        for m in range(y_len):
            so2.y[m*(y_len+1)] = yval[m]
            so2.var_y[m*(y_len+1)] = yerr2[m]
        
        so2.axis[0].val = Q[0]
        so2.axis[1].val = E_t[0]

        if so.axis[0].var != None:
            so2.axis[0].var = Q[1]
            so2.axis[1].var = E_t[1]
        # Do nothing
        else:
            pass

        hlr_utils.result_insert(result,res_descr,so2,None,"all")

    return result


if __name__=="__main__":

    import hlr_test
    import SOM

    som1=hlr_test.generate_som()
    som1.setAllAxisUnits(["Angstroms"])
    som1.attr_list.instrument = SOM.ASG_Instrument()

    E = (1,1)
    k = (1,1)
    
    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1]

    print "********** create_E_vs_Q"
    print "* som: ",create_E_vs_Q(som1,E,k)
