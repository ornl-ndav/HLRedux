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
    @type args: C{NumPy.array}s
    

    @return: The cleaned arrays. The order is I{(x, y, var_y, var_x)}.
    @rtype: C{tuple} of C{NumPy.array}s


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

def log_for_pcolor(data):
    """
    This utility function parses a list of data looking for the maximum and
    minimum non-negative, non-zero values and create an object that will handle
    creating a C{matplotlib.colors.LogNorm} object for a logarithmic z axis for
    the C{pylab.pcolor} plotting function.
    
    @param data: The list of data to search
    @type data: C{NumPy.array}
    
    
    @return: The object for handling logarithmic colors
    @rtype: C{matplotlib.colors.LogNorm}
    """
    import matplotlib.colors
    
    idxs = numpy.nonzero(data)
    import itertools
    data_min = 1.0e+302
    for (i, j) in itertools.izip(idxs[0],idxs[1]):
        if data[i][j] < 0.0:
            continue
        else:
            if data[i][j] < data_min:
                data_min = data[i][j]

    return matplotlib.colors.LogNorm(vmin=data_min)

def grid_setter(axis="x", which="major", linestyle="-", locator=None,
                ticklabels=None, rotation=None):
    """
    This utility function sets the major properties for grid lines on plots.

    @param axis: This specifies which axis gets gridlines. The defaults is
                 the x-axis.
    @type axis: C{string}

    @param which: This specifies the ticks that get grid lines. The default is
                  to set grid lines on the major ticks.
    @type which: C{string}

    @param linestyle: This specifies the line style for the grid lines. The
                      default is solid lines (-).
    @type linestyle: C{string}

    @param locator: This sets the number of grid lines visible on the plot.
    @type locator: C{int}

    @param ticklabels: This allows one to set the tick labels for the given
                       axis.
    @type ticklabels: C{list} of C{string}s

    @param rotation: This allows for the tick labels to be rotated. The value
                     can be a number or the words I{vertical} or I{horizontal}.
    @type rotation: C{string}


    @raise RuntimeError: if the axis specified is not x, y or z.
    """
    import pylab
    
    axis_vals = ["x", "y", "z"]

    if axis not in axis_vals:
        raise RuntimeError("Cannot handle axis %s" % axis)

    if axis == "x":
        axiso = pylab.gca().xaxis
    elif axis == "y":
        axiso = pylab.gca().yaxis
    elif axis == "z":
        axiso = pylab.gca().zaxis

    axiso.grid(True, which=which, linestyle=linestyle)

    if locator is not None:
        import matplotlib.ticker
        axiso.set_major_locator(matplotlib.ticker.MaxNLocator(locator))

    if ticklabels is not None:
        axiso.set_ticklabels(ticklabels, rotation=rotation)

    
