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

import pylab

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
    pass

def plot_1D_arr(x, y, var_y=None, var_x=None, **kwargs):
    """
    This function plots the data given by the provided arrays. The
    uncertainties in the x-axis and y-axis are not required to make a plot.
    Since this function is most likely run from command-line and the data
    reduction software carries around squares for the uncertainties, the
    uncertainty arrays will be square-rooted before plotting.

    @param x: The independent axis
    @type x: C{NumPy} array

    @param y: The dependent axis
    @type y: C{NumPy} array

    @param var_y: The uncertainty of the dependent axis
    @type var_y: C{NumPy} array

    @param var_x: The uncertainty of the independent axis
    @type var_x: C{NumPy} array

    @kwargs: A list of keyword arguments that the function accepts.

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
    """
    pass

    
