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

import numpy

def clean_1D_data(action, axis="y", *args):
    """
    This function cleans data for plotting.

    @param action: The type of cleaning to perform. The available options are:
                   - nonzero: Remove all zeros from the data array. This will
                              reduce the size of all arrays
    @type action: C{string}

    @param axis: The particular axis to clean. This is either I{x} or I{y}.
                 The default value is I{y}.
    @type axis: C{string}

    @param args: The list of data arrays to clean up. The arrays should be
                 listed in the following order:
                   1. Independent axis
                   2. Dependent axis
                   3. Uncertainty on the dependent axis
                   4. Uncertainty on the independent axis
    @type args: C{NumPy} arrays
    

    @return: The cleaned arrays. The order is I{(x, y, var_y, var_x)}.
    @rtype: C{tuple} of C{NumPy} arrays


    @raise RuntimeError: The requested action is not recognized
    @raise RuntimeError: The requested axis is not recognized
    """
    x = args[0]
    y = args[1]
    try:
        var_y = args[2]
    except IndexError:
        var_y = None
    try:
        var_x = args[3]
    except IndexError:
        var_x = None        

    if action == "nonzero":
        if axis == "y":
            indicies = y.nonzero()
        elif axis == "x":
            indicies = x.nonzero()
        else:
            raise RuntimeError("Cleaning only understands axis x or y and "\
                               +"not: %s" % axis) 
        x = x[indicies]
        y = y[indicies]
        if var_y is not None:
            var_y = var_y[indicies]
        if var_x is not None:
            var_x = var_x[indicies]                
    else:
        raise RuntimeError("Do not understand cleaning action: %s" % action)
    
    return (x, y, var_y, var_x)
