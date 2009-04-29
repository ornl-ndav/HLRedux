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

def subexp_eff(attenc, axis, scalec=None):
    """
    This function calculates an efficiency from a subtracted exponential of the
    form: c(1 - exp(-|k| * x)).

    @param attenc: The attentuation constant k in the exponential.
    @type attenc: L{hlr_utils.DrParameter}

    @param axis: The axis from which to calculate the efficiency
    @type axis: C{nessi_list.NessiList}

    @param scalec: The scaling constant c applied to the subtracted
                   exponential.
    @type scalec: L{hlr_utils.DrParameter}
    

    @return: The calculated efficiency
    @rtype: C{nessi_list.NessiList}
    """
    import array_manip
    import phys_corr
    import utils

    if scalec is None:
        import hlr_utils
        scalec = hlr_utils.DrParameter(1.0, 0.0)
    
    axis_bc = utils.calc_bin_centers(axis)
    temp = phys_corr.exp_detector_eff(axis_bc[0], scalec.getValue(),
                                      scalec.getError(), attenc.getValue())
    return array_manip.sub_ncerr(scalec.getValue(), scalec.getError(),
                                 temp[0], temp[1])
