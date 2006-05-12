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

def file_exists(filename):
    """
    This function accepts a filename as a string and queries the file system
    for the existence of the file.

    Parameters:
    ----------
    -> filename is a string object containing the file name

    Returns:
    -------
    <- A boolean which is True if the file exists and False if is does not
    """
    
    import os.path

    if filename.startswith("~"):
        filename = os.path.expanduser(filename)
    elif filename.startswith("$"):
        filename = os.path.expandvars(filename)

    return os.path.isfile(filename)


def ext_replace(name, ext_out, ext_in):
    """
    This function takes a filename and an extension (without the dot) and
    replaces that extension with new given extension (again without the dot).

    Parameters:
    ----------
    -> name is a string object containing a filename
    -> ext_out is a string object containing the extension being replaced
    -> ext_in is a string object containing the replacing extension

    Returns:
    -------
    <- A string object containing the new filename
    """

    import re
    expression = r'\.'+ext_out+'$'
    myre=re.compile(expression)
    return myre.sub("", name)+'.'+ext_in


def split_values(thing):
    """
    This function takes a string object that has the form value,err^2,units or
    value,err^2 or value,units. If the latter version is given, a default
    value of 0.0 will be given for err^2.

    Parameters:
    ----------
    -> thing is a string object of the form value,err^2 or value,err^2,units
       or value,units

    Returns:
    -------
    <- A tuple of (value,err^2) or (value,err^2,units)
    """

    mylist = thing.split(',')
    try:
        return (float(mylist[0]), float(mylist[1]), mylist[2])
    except IndexError:
        pass
    
    try:
        return (float(mylist[0]), float(mylist[1]))
    except ValueError:
        return (float(mylist[0]), 0.0, mylist[1])
    

def make_axis(min, max, delta, **kwargs):
    """
    This function takes a minimum, maximum and a delta value and converts
    those numbers into an axis.

    Parameters:
    ----------
    -> min is the minimum value of the axis
    -> max is the maximum value of the axis
    -> delta is the bin width for the axis
    -> kwargs is a list of key word arguments that the function accepts:
          type= a string containing the type of axis desired. Type can be
                histogram, coordinate or density. If type is not provided the
                default is histogram

    Returns:
    -------
    <- A NessiList that contains the axis

    Exceptions:
    ----------
    <- RuntimeError is raised if the type provided via kwarg type is not
       histogram or density or coordinate
    """

    import math
    import nessi_list

    n_bins = int(math.fabs(max - min) / delta)

    axis = nessi_list.NessiList()

    for i in range(n_bins):
        axis.append(min + i * delta)

    try:
        if(kwargs["type"] == "histogram"):
            axis.append(max)
        elif(kwargs["type"] == "density" or kwargs["type"] == "coordinate"):
            pass
        else:
            raise RuntimeError, "Do not understand type: %s" % kwargs["type"]
        
    except KeyError:
        axis.append(max)

    return axis

