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
    value of 0.0 will be given for err^2. It produces a tuple of
    (value,err^2,units)

    Parameters:
    ----------
    -> thing is a string object of the form value,err^2 or value,err^2,units
       or value,units

    Returns:
    -------
    <- A tuple of (value,err^2,units)
    """

    mylist = thing.split(',')
    try:
        return (float(mylist[0]), float(mylist[1]), mylist[2])
    except IndexError:
        pass
    
    try:
        return (float(mylist[0]), float(mylist[1]), None)
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
                histogram, coordinate or density (the last two are synonyms).
                If type is not provided the default is histogram

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

def fix_filename(filename):
    """
    This function takes a filename contaning things like ~/ or $HOME and
    expands those into a proper filename. If a string contains no such
    references, nothing is no to the string

    Parameters:
    ----------
    -> filename is a string containing the filname to be fixed

    Returns:
    -------
    <- The filename with special cases expanded
    """
    
    import os

    if filename != None:
        try:
            filename.index('~')
            filename = os.path.expanduser(filename)
        except ValueError:
            pass
        
        try:
            filename.index('$')
            filename = os.path.expandvars(filename)
        except ValueError:
            pass

    # Filename is a None type, just pass it back
    else:
        pass

    return filename


def create_data_paths(thing):
    """
    This function takes in a string that contains NeXus path and signal pairs
    and turns them into a tuple (for one pair) or a list of tuples.

    Parameters:
    ----------
    -> things is a string containing a list of NeXus path and signal pairs

    Returns:
    -------
    <- A tuple or list of tuples of the NeXus path,signal pairs
    """
    
    mylist = thing.split(',')
    length = len(mylist)
   
    if length == 2:
        use_extend = True
    else:
        use_extend = False

    data_paths = []

    for i in range(0,len(mylist),2):
        if use_extend:
            data_paths.extend((mylist[i], int(mylist[i+1])))
        else:
            data_paths.append((mylist[i], int(mylist[i+1])))

    if len(mylist) == 2:
        return tuple(data_paths)
    else:
        return data_paths


def write_file(filename, dst_type, data, **kwargs):
    """
    This function performs the steps necessary to write an output file. One
    can pass a data filename or an output filename. If a data filename is
    passed, the data file extension, output file extension and the replace
    keyword must be passed. The expected data object to write to the file is
    a SOM.

    Parameters:
    ----------
    -> filename is a string containing the name of the data file from which
                the output is generated or the name of an output file
    -> dst_type is a string containing the MIME type of the output formatter
    -> data is a SOM that contains the output to be written to file
    -> kwargs is a list of key word arguments that the function accepts:
          message=<string> This is part of the message that will be printed
                  to STDOUT if verbose is switched on. The default message
                  is \"output file\"
          data_ext=<string> This is the extension on the data file. This is
                   used in conjunction with output_ext and replace to convert
                   the data filename into an output filename. The default
                   value is \"nxs\".
          output_ext=<string> This is the extension to be used for the output
                     file. The default value is \"txt\".
          verbose=<True or False> This determines whether or not the print
                  statement is executed. The default value is False.
          replace=<True or False> This determines whether or not the parameter
                  filename is modifed to produce the output filename
    """

    import os

    import DST
    import hlr_utils

    try:
        message = kwargs["message"]
    except KeyError:
        message = "output file"

    try:
        data_ext = kwargs["data_ext"]
    except KeyError:
        data_ext = "nxs"

    try:
        output_ext = kwargs["output_ext"]
    except KeyError:
        output_ext = "txt"

    try:
        verbose = kwargs["verbose"]
    except KeyError:
        verbose = False

    try:
        replace = kwargs["replace"]
    except KeyError:
        replace = True

    if replace:
        file = os.path.basename(filename)
        path = os.path.join(os.getcwd(), file)
        file = hlr_utils.ext_replace(path, data_ext, output_ext)
    else:
        file = filename
        
    resource = open(file, "w")
    output_dst = DST.getInstance(dst_type, resource)
    if verbose:
        print "Writing %s" % message

    output_dst.writeSOM(data)
    output_dst.release_resource()


def create_id_pairs(pairs, paths, **kwargs):
    """
    This function takes in a string that contains pairs of numbers and turns
    them into a tuple (for one pair) or a list of tuples. The function checks
    against the number of data paths requested. If the number of paths is not
    equal to the number of id pairs given, the last id pair is duplicated
    until the number of id pairs is the same as the number of data paths

    Parameters:
    ----------
    -> pairs is a string containing a list of pixel id pairs
    -> paths is a string containing a list of NeXus data paths and signal pairs

    Returns:
    -------
    <- A tuple or list of tuples of the pixel id pairs
    """

    mylist = pairs.split(',')
    length = len(mylist)

    if length == 2:
        use_extend = True
    else:
        use_extend = False

    size = len(paths.split(','))

    id_pairs = []

    index = -1
    for i in range(0, length, 2):
        if use_extend:
            id_pairs.extend((int(mylist[i]), int(mylist[i+1])))
        else:
            id_pairs.append((int(mylist[i]), int(mylist[i+1])))
        index = i

    # The number of data paths and the number of id pairs is equal
    if length == size:
        if length == 2:
            return tuple(id_pairs)
        else:
            return id_pairs
    # They are not equal. Fill in the id pairs with the last one until they
    # are the same
    else:
        last_pair = id_pairs[-1]
        additions = size / length - 1
        for j in range(additions):
            id_pairs.append(last_pair)

        return id_pairs

def create_pixel_id(thing):
    """
    This function creates a pixel ID out of a comma-delimited list of three
    values, i.e.: bank3,3,63.

    Parameters:
    ----------
    -> thing is a string containing three pieces of information to create a
             pixel ID

    Returns:
    -------
    <- A tuple containing the pixel ID

    Exceptions:
    ----------
    <- RuntimeError is raised if 3 pieces of information are not provided to
                    the function
    """

    mylist = thing.split(',')

    if len(mylist) != 3:
        raise RuntimeError("Must provide three pieces of information to the "\
                           +"function")
    else:
        pass

    return (mylist[0], (int(mylist[1]), int(mylist[2])))
