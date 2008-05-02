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

def plot_numinfo(som):
    """
    This function allows one to plot data that is the result of integrating
    a C{SOM.SOM} via a function like L{dr_lib.integrate_spectra}. NOTE: This
    function only creates the plot. Viewing the actual plot requires invoking
    I{pylab.show()}.

    @param som: The object containing the data to plot.
    @type som: C{SOM.SOM}
    """
    info = som.toXY(withYvar=True)

    # Data is stored as floats and pixel IDs, so everything needs conversion
    x = numpy.arange(len(info))
    y = numpy.array([s[1] for s in info])
    ey = numpy.sqrt([s[2] for s in info])
    pid = numpy.array([str(s[0]) for s in info])

    pylab.errorbar(x, y, ey, fmt='o', mec='b', ls='None')

    pylab.xticks(x, pid, rotation='vertical')
    pylab.ylabel(som.getYLabel() + " [" + som.getYUnits() + "]")

