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
import pylab

def plot_2D_so(som, **kwargs):
    """
    This function plots a 2D dataset that is held in a single C{SOM.SO} inside
    of a C{SOM.SOM}. NOTE: This
    function only creates the plot. Viewing the actual plot requires invoking
    I{pylab.show()}.

    @param som: The object containing the data to plot.
    @type som: C{SOM.SOM}
    """
    info = som.toXY()

    x = info[0][0]
    y = info[0][1]

    # Get dimensions of data
    Nx = x.size
    Ny = y.size

    # z values are filtered since plotting has trouble with NaNs
    z = numpy.reshape(numpy.nan_to_num(info[0][2]), (Nx, Ny))

    # Set plot attributes
    xlabel = som.getAxisLabel(0) + " [" + som.getAxisUnits(0) + "]"
    ylabel = som.getAxisLabel(1) + " [" + som.getAxisUnits(1) + "]"

    import drplot
    drplot.plot_2D_arr(x, y, z, xlabel=xlabel, ylabel=ylabel, **kwargs)

def plot_2D_arr(x, y, z, **kwargs):
    """
    This function plots a 2D dataset consisting of the given arrays. NOTE: This
    function only creates the plot. Viewing the actual plot requires invoking
    I{pylab.show()}.

    @param x: The first independent axis
    @type x: C{NumPy} array

    @param y: The second independent axis
    @type y: C{NumPy} array

    @param z: The dependent axis
    @type z: C{NumPy} array

    @kwargs: A list of keyword arguments that the function accepts.

    @keyword colormap: A I{matplotlib} colormap for plotting the data. The
                       default is I{cm.hot}.
    @type colormap: C{matplotlib.cm}

    @keyword xlabel: The label for the independent axis.
    @type xlabel: C{string}

    @keyword ylabel: The label for the dependent axis.
    @type ylabel: C{string}

    @keyword title: The title for the plot
    @type title: C{string}
    """
    # Lookup all the keywords

    try:
        xlabel = kwargs["xlabel"]
    except KeyError:
        xlabel = ""

    try:
        ylabel = kwargs["ylabel"]
    except KeyError:
        ylabel = ""        

    try:
        title = kwargs["title"]
    except KeyError:
        title = ""

    try:
        colormap = kwargs["colormap"]
    except KeyError:
        import matplotlib
        colormap = matplotlib.cm.hot
