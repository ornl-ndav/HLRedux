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

def create_param_vs_Y(som, param, param_func, param_axis, **kwargs):
    """
    This function takes a group of single spectrum with any given axes
    (wavelength, energy etc.). The function can optionally rebin those axes to
    a given axis. It then creates a 2D spectrum by using a parameter,
    parameter functiona and a given axis for the lookup locations and places
    each original spectrum in the found location.
    
    @param som: The input object with arbitrary (but same) axis spectra
    @type som: C{SOM.SOM}

    @param param: The parameter that will be used for creating the lookups.
    @type param: C{string}

    @param param_func: The function that will convert the parameter into the
                       values for lookups.
    @type param_func: C{string}

    @param param_axis: The axis that will be searched for the lookup values.
    @type param_axis: C{nessi_list.NessiList}

    @param kwargs: A list of keyword arguments that the function accepts:

    @keyword rebin_axis: An axis to rebin the given spectra to.
    @type rebin_axis: C{nessi_list.NessiList}


    @return: A two dimensional spectrum with the parameter as the x-axis and
             the given spectra axes as the y-axis.
    @rtype: C{SOM.SOM}
    """
    import common_lib
    import hlr_utils
    import nessi_list
    import SOM

    # Setup some variables 
    dim = 2
    N_y = []
    N_tot = 1
    N_args = len(args)

    # Create 2D spectrum object
    so_dim = SOM.SO(dim)

    # Create final 2D spectrum object container
    comb_som = SOM.SOM()
    
    comb_som.append(so_dim)

    del so_dim

    return comb_som
