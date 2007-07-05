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

def calc_deltat_over_t(axis, axis_err2=None, **kwargs):
    """
    This function takes a TOF axis and calculates the quantity Delta t / t
    for every element. 

    @param axis: The TOF axis from which Delta t / t will be calculated
    @type axis: C{nessi_list.NessiList}
    
    @param axis_err2: (OPTIONAL) The error^2 on the incoming TOF axis
    @type axis_err2: C{nessi_list.NessiList}


    @return: The calculated Delta t / t
    @rtype: C{SOM.SOM}
    """
    import nessi_list

    # Check to see if incoming is really a NessiList
    try:
        axis.__type__
    except AttributeError:
        raise RuntimeError("The object passed to this function needs to be a "\
                           +"NessiList. Do not understand how to deal with "\
                           +"%s" % type(axis))

    len_axis = len(axis)
    if axis_err2 is None:
        axis_err2 = nessi_list.NessiList(len_axis)

    deltat = nessi_list.NessiList()
    deltat_err2 = nessi_list.NessiList()
    
    # Calculate bin deltas, assume axis in ascending order
    for i in xrange(len_axis-1):
        deltat.append(axis[i+1] - axis[i])
        deltat_err2.append(axis_err2[i+1] - axis_err2[i])        

    # Calculate bin centers
    import utils
    (binc, binc_err2) = utils.calc_bin_centers(axis, axis_err2)

    # Calculate delta t / t
    import array_manip
    dtot = array_manip.div_ncerr(deltat, deltat_err2, binc, binc_err2)

    import SOM
    som = SOM.SOM()
    so = SOM.SO()
    so.y = dtot[0]
    so.var_y = dtot[1]
    som.append(so)

    som.setDataSetType("density")
    som.setYLabel("deltat_over_t")

    return som
    
if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som()

    print "************ SOM1"
    print "* ", som1[0]

    print "************ calc_deltat_over_t"
    print "* som1[0]:", calc_deltat_over_t(som1[0].axis[0].val)
