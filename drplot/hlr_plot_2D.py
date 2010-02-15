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

    # Set plot attributes, take overrides if provided
    try:
        xlabel = kwargs["xlabel"]
        del kwargs["xlabel"]
    except KeyError:
        xlabel = som.getAxisLabel(1) + " [" + som.getAxisUnits(1) + "]"

    try:
        ylabel = kwargs["ylabel"]
        del kwargs["ylabel"]
    except KeyError:
        ylabel = som.getAxisLabel(0) + " [" + som.getAxisUnits(0) + "]"

    # Add labels back into keyword dictionary
    kwargs["xlabel"] = xlabel
    kwargs["ylabel"] = ylabel

    drplot.plot_2D_arr(y, x, z, **kwargs)

def plot_2D_arr(x, y, z, **kwargs):
    """
    This function plots a 2D dataset consisting of the given arrays. NOTE: This
    function only creates the plot. Viewing the actual plot requires invoking
    I{pylab.show()}.

    @param x: The first independent axis
    @type x: C{NumPy.array}

    @param y: The second independent axis
    @type y: C{NumPy.array}

    @param z: The dependent axis
    @type z: C{NumPy.array}

    @param kwargs: A list of keyword arguments that the function accepts.

    @keyword colormap: A I{matplotlib} colormap for plotting the data. The
                       default is I{cm.hot}.
    @type colormap: C{matplotlib.cm}

    @keyword logz: A flag that sets the z-axis on a logarithmic scale.
    @type logz: C{boolean}

    @keyword nocb: A flag that turns of the colorbar for the plot.
    @type nocb: C{boolean}

    @keyword xlabel: The label for the independent axis.
    @type xlabel: C{string}

    @keyword ylabel: The label for the dependent axis.
    @type ylabel: C{string}

    @keyword title: The title for the plot
    @type title: C{string}
    """
    import matplotlib
    
            
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
        colormap = matplotlib.cm.hot

    try:
        logz = kwargs["logz"]
    except KeyError:
        logz = False

    try:
        nocb = kwargs["nocb"]
    except KeyError:
        nocb = False        

    if logz:
        lognorm = drplot.log_for_pcolor(z)
    else:
        lognorm = None

    pylab.pcolor(x, y, z, cmap=colormap, norm=lognorm)
    pylab.xlabel(xlabel)
    pylab.ylabel(ylabel)
    pylab.title(title)

    # Add the color scale
    if not nocb:
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

    try:
        xlabel = kwargs["xlabel"]
        del kwargs["xlabel"]
    except KeyError:
        xlabel = None

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
        sx = __get_slice(xslice, Nx)
        sy = __get_slice(yslice, Ny)
    else:
        x_min = __find_index(x, xslice[0])
        x_max = __find_index(x, xslice[1])
        y_min = __find_index(y, yslice[0])
        y_max = __find_index(y, yslice[1])        
            
        sx = __get_slice((x_min, x_max), Nx)
        sy = __get_slice((y_min, y_max), Ny)

    # Setup axis specific values
    if axis == "y":
        naxis = 0
        if xlabel is None:
            xlabel = som.getAxisLabel(1) + " [" + som.getAxisUnits(1) + "]"
        xp = y[sy]
    elif axis == "x":
        naxis = 1
        if xlabel is None:
            xlabel = som.getAxisLabel(0) + " [" + som.getAxisUnits(0) + "]"
        xp = x[sx]
    else:
        raise RuntimeError("Only understand x or y for axis and not: %s" \
                           % axis)

    yp = z[sx, sy].sum(axis=naxis)
    var_yp = var_z[sx, sy].sum(axis=naxis)

    drplot.plot_1D_arr(xp, yp, var_yp, xlabel=xlabel, **kwargs)

def plot_1D_slices(som, axis, arange, **kwargs):
    """
    This function plots multiple 1D slices from a 2D spectrum. The function
    requires the axis to project onto and a range of slices to view. NOTE: This
    function only creates the plot. Viewing the actual plot requires invoking
    I{pylab.show()}.

    @param som: The object containing the data to plot.
    @type som: C{SOM.SOM}

    @param axis: The particular axis to clean. This is either I{x} or I{y}.
    @type axis: C{string}

    @param arange: A set of axis values that determines the slices to view in
                  the format of (min, max).
    @type arange: C{tuple} of two numbers

    @param kwargs: A list of keyword arguments that the function accepts. The
                   function also takes keywords for L{drplot.plot_1D_slice}.

    @keyword clip: A set of numbers that specify the range to plot on the axis
                   chosen for the slice or projection. Both the minimum and
                   maximum range values must be specified.
    @type clip: C{tuple} of two numbers
    """

    aclip = kwargs.get("clip", (None, None))
    
    if axis == "y":
        iaxis = 0
        yslice = (__find_index(som[0].axis[1].val.toNumPy(), aclip[0]),
                  __find_index(som[0].axis[1].val.toNumPy(), aclip[1]))
    elif axis == "x":
        iaxis = 1
        xslice = (__find_index(som[0].axis[0].val.toNumPy(), aclip[0]),
                  __find_index(som[0].axis[0].val.toNumPy(), aclip[1]))
    else:
        raise RuntimeError("Only understand x or y for axis and not: %s" \
                           % axis)

    saxis = som[0].axis[iaxis].val
    ilabel = som.getAxisLabel(iaxis)
    iunits = som.getAxisUnits(iaxis)
    sidx = __find_index(saxis.toNumPy(), arange[0])
    eidx = __find_index(saxis.toNumPy(), arange[1])

    if sidx is None and eidx is None:
        slice_range = (0, len(saxis))
    elif sidx is None and eidx is not None:
        slice_range = (0, eidx)
    elif sidx is not None and eidx is None:
        slice_range = (sidx, len(saxis))
    else:
        slice_range = (sidx, eidx)

    for i in xrange(slice_range[0], slice_range[1]):
        if axis == "y":
            xslice = (i, i+1)
        elif axis == "x":
            yslice = (i, i+1)

        nlabel = ilabel + " = %f %s" % (saxis[i], iunits)

        try:
            drplot.plot_1D_slice(som, axis, xslice, yslice, index=True,
                                 llabel=nlabel, **kwargs)
        except ValueError:
            # All data got filtered
            pass

    pylab.legend(numpoints=1)

def __find_index(arr, val):
    """
    This helper function searches an array for a particular value returning
    the index where the value could be inserted into the array.

    @param arr: The object containing the information to be searched
    @type arr: C{NumPy.array}

    @param val: The value to search the array for
    @type val: C{float} or C{int}


    @return: The index where the value could be inserted into the array
    @rtype: C{int}
    """
    if val is not None:
        return numpy.searchsorted(arr, val)
    else:
        return val

def __get_slice(islice, isize):
    """
    This helper function creates a slice based on a tuple of two numbers. If
    the extremes of the slice are desired, use I{None} to signify that request.

    @param islice: The object containing the requested slice
    @type islice: C{tuple} of two C{int}s
    
    @param isize: The total size of the array being sliced
    @type isize: C{int}
    

    @return: The slice based on the requested information
    @rtype: C{slice}
    """
    if islice[0] is None:
        if islice[1] is None:
            return slice(isize)
        else:
            return slice(islice[1])
    else:
        if islice[1] is None:
            return slice(islice[0], isize)
        else:
            return slice(islice[0], islice[1])
