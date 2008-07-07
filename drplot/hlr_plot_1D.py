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

import numpy
import pylab

import drplot

def plot_1D_so(som, pix_id, **kwargs):
    """
    This function allows one to plot the data in a C{SOM.SO}. This happens by
    passing the C{SOM.SOM} and a pixel ID. The pixel ID is searched in the
    C{SOM.SOM} and the returned C{SOM.SO} is plotted. The C{SOM.SOM} is passed
    since it contains the metadata information. NOTE: This function only
    creates the plot. Viewing the actual plot requires invoking
    I{pylab.show()}.

    @param som: The object containing the data to plot.
    @type som: C{SOM.SOM}

    @param pix_id: The pixel ID for the C{SOM.SO} to plot.
    @type pix_id: various
    """
    # Retrieve the SO
    so = som.getSO(pix_id)
    
    # Get the data type
    dataset_type = som.getDataSetType()

    # Get data arrays
    if dataset_type == "histogram":
        x = so.axis[0].val.toNumPy(True)
    else:
        x = so.axis[0].val.toNumPy()
    y = so.y.toNumPy()
    var_y = so.var_y.toNumPy()
    try:
        var_x = so.axis[0].var.toNumPy()
    except AttributeError:
        var_x = None

    # Set plot attributes
    try:
        xlabel = kwargs["xlabel"]
        del kwargs["xlabel"]
    except KeyError:
        xlabel = som.getAxisLabel(0) + " [" + som.getAxisUnits(0) + "]"

    try:
        ylabel = kwargs["ylabel"]
        del kwargs["ylabel"]
    except KeyError:
        ylabel = som.getYLabel() + " [" + som.getYUnits() + "]"
        
    try:
        title = kwargs["title"]
        del kwargs["title"]
    except KeyError :       
        title = str(pix_id)

    # Make 1D plot
    drplot.plot_1D_arr(x, y, var_y, var_x, xlabel=xlabel, ylabel=ylabel,
                       title=title, **kwargs)

def plot_1D_arr(x, y, var_y=None, var_x=None, **kwargs):
    """
    This function plots the data given by the provided arrays. The
    uncertainties in the x-axis and y-axis are not required to make a plot.
    Since this function is most likely run from command-line and the data
    reduction software carries around squares for the uncertainties, the
    uncertainty arrays will be square-rooted before plotting. NOTE: This
    function only creates the plot. Viewing the actual plot requires invoking
    I{pylab.show()}.

    @param x: The independent axis
    @type x: C{NumPy} array

    @param y: The dependent axis
    @type y: C{NumPy} array

    @param var_y: The uncertainty of the dependent axis
    @type var_y: C{NumPy} array

    @param var_x: The uncertainty of the independent axis
    @type var_x: C{NumPy} array

    @param kwargs: A list of keyword arguments that the function accepts.

    @keyword xlabel: The label for the independent axis.
    @type xlabel: C{string}

    @keyword ylabel: The label for the dependent axis.
    @type ylabel: C{string}

    @keyword title: The title for the plot
    @type title: C{string}

    @keyword logy: Set the dependent axis to logarithmic
    @type logy: C{boolean}

    @keyword logx: Set the independent axis to logarithmic
    @type logx: C{boolean}

    @keyword llabel: Set the legend label for the plot
    @type llabel: C{string}
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
        logy = kwargs["logy"]
    except KeyError:
        logy = False

    try:
        logx = kwargs["logx"]
    except KeyError:
        logx = False

    try:
        llabel = kwargs["llabel"]
    except KeyError:
        llabel = ""

    # Square-root incoming uncertainty arrays
    if var_y is not None:
        var_y = numpy.sqrt(var_y)

    if var_x is not None:
        var_x = numpy.sqrt(var_x)        

    # Need to clean data if logarithimic scale is necessary
    if logy:
        (x, y, var_y, var_x) = drplot.clean_1D_data("nonzero", "y",
                                                    x, y, var_y, var_x)
    if logx:
        (x, y, var_y, var_x) = drplot.clean_1D_data("nonzero", "x",
                                                    x, y, var_y, var_x)

    # Set the axes to logarithimic scale, if necessary
    if logy or logx:
        ax = pylab.gca()
        if logy:
            ax.set_yscale("log")
        if logx:
            ax.set_xscale("log")

    pylab.errorbar(x, y, var_y, var_x, fmt='o', mec='b', ls='None',
                   label=llabel)
    pylab.xlabel(xlabel)
    pylab.ylabel(ylabel)
    pylab.title(title)


