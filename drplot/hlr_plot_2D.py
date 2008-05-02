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

import drplot

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

    # Get the independent axes
    x = info[0][0]
    y = info[0][1]

    # Get dimensions of data
    Nx = x.size
    Ny = y.size

    # z values are filtered since plotting has trouble with NaNs. The
    # I{nan_to_num} function zeros NaNs and sets (-)Inf to the largest
    # (negative) positive value.
    z = numpy.reshape(numpy.nan_to_num(info[0][2]), (Nx, Ny))

    # Matplotlib and NumPy don't agree on how our 2D data is actually
    # distributed. We use the notion that the fastest running index is the
    # y axis for a given data set. NumPy creates a 2D array that has
    # Nrows = Nx and Ncols = Ny which agrees with our designation. However,
    # Matplotlib requires that Ncols is actually the x direction for the plot.
    # This means the labels are created in reverse order and the original x
    # and y arrays are plotted in reverse. 

    # Set plot attributes
    xlabel = som.getAxisLabel(1) + " [" + som.getAxisUnits(1) + "]"
    ylabel = som.getAxisLabel(0) + " [" + som.getAxisUnits(0) + "]"

    drplot.plot_2D_arr(y, x, z, xlabel=xlabel, ylabel=ylabel, **kwargs)

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

    pylab.contourf(x, y, z, cmap=colormap)
    pylab.xlabel(xlabel)
    pylab.ylabel(ylabel)
    pylab.title(title)

    # Add the color scale
    pylab.colorbar()

def plot_1D_slice(som, axis, xslice, yslice, **kwargs):
    """
    This function plots a 1D slice from a 2D spectrum. The function requires
    the axis to project onto and a set of slice ranges. NOTE: This
    function only creates the plot. Viewing the actual plot requires invoking
    I{pylab.show()}.

    @param som: The object containing the data to plot.
    @type som: C{SOM.SOM}

    @param axis: The particular axis to clean. This is either I{x} or I{y}.
    @type axis: C{string}

    @param xslice: A set of axis values that determine the x-axis values to
                   get the slice over in the format of (min, max). Passing
                   I{None} for either min or max gets the first or last bin
                   respectively.
    @type xslice: C{tuple} of two numbers

    @param yslice: A set of axis values that determine the y-axis values to
                   get the slice over in the format of (min, max). Passing
                   I{None} for either min or max gets the first or last bin
                   respectively.
    @type yslice: C{tuple} of two numbers

    @param kwargs: A list of keyword arguments that the function accepts. The
                   function also takes keywords for L{drplot.plot_1D_arr}.
    
    @keyword index: A flag that tells the function that the slice ranges are
                    indicies and not axis values. The default is I{False}.
    @type index: C{boolean}


    @raise RuntimeError: The axis value is not recognized
    """
    # Lookup all the keywords
    try:
        index = kwargs["index"]
    except KeyError:
        index = False

    [(x, y, z, var_z)] = som.toXY(withYvar=True)

    # Get dimensions of data
    Nx = x.size
    Ny = y.size

    # z values are filtered since plotting has trouble with NaNs. The
    # I{nan_to_num} function zeros NaNs and sets (-)Inf to the largest
    # (negative) positive value.
    z = numpy.reshape(numpy.nan_to_num(z), (Nx, Ny))
    var_z = numpy.reshape(numpy.nan_to_num(var_z), (Nx, Ny))

    # Find the x and y slice ranges in terms of array indicies
    if index:
        if xslice[0] is None:
            if xslice[1] is None:
                sx = slice(Nx)
            else:
                if Nx == xslice[1]:
                    sx = slice(xslice[1])
                else:
                    sx = slice(xslice[1] + 1)
        else:
            if xslice[1] is None:
                sx = slice(xslice[0], Nx)
            else:
                if Nx == xslice[1]:
                    sx = slice(xslice[0], xslice[1])
                else:
                    sx = slice(xslice[0], xslice[1] + 1)

        if yslice[0] is None:
            if yslice[1] is None:
                sy = slice(Ny)
            else:
                if Ny == yslice[1]:
                    sy = slice(yslice[1])
                else:
                    sy = slice(yslice[1] + 1)
        else:
            if yslice[1] is None:
                sy = slice(yslice[0], Ny)
            else:
                if Ny == yslice[1]:
                    sy = slice(yslice[0], yslice[1])
                else:
                    sy = slice(yslice[0], yslice[1] + 1)                    
                    
    else:
        pass

    # Setup axis specific values
    if axis == "y":
         naxis = 0
         xlabel = som.getAxisLabel(1) + " [" + som.getAxisUnits(1) + "]"
         xp = y[sy]
    elif axis == "x":
        naxis = 1
        xlabel = som.getAxisLabel(0) + " [" + som.getAxisUnits(0) + "]"
        xp = x[sx]
    else:
        raise RuntimeError("Only understand x or y for axis and not: %s" \
                           % axis)

    yp = z[sx, sy].sum(axis=naxis)
    var_yp = var_z[sx, sy].sum(axis=naxis)

    drplot.plot_1D_arr(xp, yp, var_yp, xlabel=xlabel, **kwargs)
