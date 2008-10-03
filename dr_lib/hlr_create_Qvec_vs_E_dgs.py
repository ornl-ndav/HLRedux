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

def create_Qvec_vs_E_dgs(som, E_i):
    """
    This function starts with the energy transfer axis from DGS reduction and
    turns this into a 4D spectra with Qx, Qy, Qz and Et axes.

    @param som: The input object with initial IGS wavelength axis
    @type som: C{SOM.SOM}

    @param E_i: The initial energy for the given data.
    @type E_i: C{tuple}
    """
    import common_lib
    import hlr_utils

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

    E_f = common_lib.sub_ncerr(E_i, (E_t, E_t_err2))
    
    # Now we can get the final wavevector
    l_f = common_lib.energy_wavelength(E_f)
    k_f = common_lib.wavelength_to_scalar_k(l_f)

    # Iterate though the data
    len_som = hlr_utils.get_length(som)
    for i in xrange(len_som):
        pass
