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

    return os.path.isfile(fix_filename(filename))


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
    myre = re.compile(expression)

    return myre.sub("", name) + '.' + ext_in

def add_tag(filename, tag):
    """
    This function takes a filename, splits it at the extension and appends a
    tag in front of the extension.

    Parameters:
    ----------
    -> filename is a string object containing the file name
    -> tag is a string that will be placed before the file extension
    
    Returns:
    -------
    <- A string object containing the new filename
    """
    
    index = filename.rfind('.')
    return filename[0:index] + "_" + tag + filename[index:]

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
        try:
            return (float(mylist[0]), float(mylist[1]), None)
        except ValueError:
            return (float(mylist[0]), 0.0, mylist[1])
    

def make_axis(axis_min, axis_max, delta, **kwargs):
    """
    This function takes a minimum, maximum and a delta value and converts
    those numbers into an axis.

    Parameters:
    ----------
    -> axis_min is the minimum value of the axis
    -> axis_max is the maximum value of the axis
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

    n_bins = int(math.fabs(axis_max - axis_min) / delta)

    axis = nessi_list.NessiList()

    for i in range(n_bins):
        axis.append(axis_min + i * delta)

    try:
        if(kwargs["type"] == "histogram"):
            axis.append(axis_max)
        elif(kwargs["type"] == "density" or kwargs["type"] == "coordinate"):
            pass
        else:
            raise RuntimeError("Do not understand type: %s" % kwargs["type"])
        
    except KeyError:
        axis.append(axis_max)

    return axis

def make_axis_file(filename, **kwargs):
    """
    This function takes a file of minimum, maximum and a delta values and
    converts those numbers into an axis.

    Parameters:
    ----------
    -> filename is the name of the file containing the axis values
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

    axis = nessi_list.NessiList()

    ifile = open(filename, "r")

    alllines = ifile.readlines()

    for eachline in alllines:
        values = eachline.split(',')

        axis_min = float(values[0])
        axis_max = float(values[1])
        delta = float(values[2])

        n_bins = int(math.fabs(axis_max - axis_min) / delta)
    
        for i in range(n_bins):
            axis.append(axis_min + i * delta)

    axis_max = float(alllines[-1].split(',')[1])

    try:
        if(kwargs["type"] == "histogram"):
            axis.append(axis_max)
        elif(kwargs["type"] == "density" or kwargs["type"] == "coordinate"):
            pass
        else:
            raise RuntimeError("Do not understand type: %s" % kwargs["type"])
        
    except KeyError:
        axis.append(axis_max)

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

    for i in range(0, len(mylist), 2):
        if use_extend:
            data_paths.extend((mylist[i], int(mylist[i + 1])))
        else:
            data_paths.append((mylist[i], int(mylist[i + 1])))

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
    -> data is a SOM that contains the output to be written to fil
    -> kwargs is a list of key word arguments that the function accepts:
          message=<string> This is part of the message that will be printed
                  to STDOUT if verbose keyword is set to True. The default
                  message is \"output file\"
          data_ext=<string> This is the extension on the data file. This is
                   used in conjunction with output_ext and replace to convert
                   the data filename into an output filename. The default
                   value is \"nxs\".
          output_ext=<string> This is the extension to be used for the output
                     file. The default value is \"txt\".
          verbose=<True or False> This determines whether or not the print
                  statement is executed. The default value is False.
          replace_ext=<boolean> This determines whether or not the extension
                     on the incoming filename is replaced with output_ext.
                     The default behavior is True (replace extension)
          replace_path=<boolean> This determines whether or not the directory
                      path on the incoming filename is replaced with the
                      directory where the driver is running. The default
                      behavior is True (replace path)
          extra_tag=<string> This is a tag that will be inserted into the file
                             name just before the file extension.
       NOTE: Extra keyword arguments can be passed onto the DST instance via
             calling them in the kwargs list. Those arguments will not be
             processed by this function, but just pass them on.
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
        replace_path = kwargs["replace_path"]
    except KeyError:
        replace_path = True

    try:
        replace_ext = kwargs["replace_ext"]
    except KeyError:
        replace_ext = True        

    try:
        extra_tag = kwargs["extra_tag"]
    except KeyError:
        extra_tag = None

    try:
        arguments = kwargs["arguments"]
    except KeyError:
        arguments = None

    if replace_path:
        fixed_filename = os.path.join(os.getcwd(), os.path.basename(filename))
    else:
        fixed_filename = filename

    if replace_ext:
        fixed_filename = hlr_utils.ext_replace(fixed_filename, data_ext,
                                               output_ext)
    else:
        pass

    if extra_tag is not None:
        fixed_filename = hlr_utils.add_tag(fixed_filename, extra_tag)
        
    resource = open(fixed_filename, "w")
    output_dst = DST.getInstance(dst_type, resource, arguments, **kwargs)
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
    -> kwargs is a list of key word arguments that the function accepts:
         inc=<boolean> is a switch to increment the ending ids by 1

    Returns:
    -------
    <- A tuple or list of tuples of the pixel id pairs
    """

    try:
        increment = kwargs["inc"]
    except KeyError:
        increment = False

    mylist = pairs.split(',')
    length = len(mylist)

    if length % 2 != 0:
        raise RuntimeError("Expected an even number of Id pairs")
    else:
        pass

    size = len(paths.split(','))
    try:
        if int(paths.split(',')[1]) == 1:
            size = 1
    except TypeError:
        pass
    
    if length == 2 and length/2 == size:
        use_extend = True
    else:
        use_extend = False

    id_pairs = []

    # Must extend the end ids by one since the ids are given as inclusive
    # and python's range command treats the last number as exclusive
    if increment:
        offset = 1
    else:
        offset = 0
    
    for i in range(0, length, 2):
        if use_extend:
            id_pairs.extend((int(mylist[i]) + offset,
                             int(mylist[i + 1]) + offset))
        else:
            id_pairs.append((int(mylist[i]) + offset,
                             int(mylist[i + 1]) + offset))

    # The number of data paths and the number of id pairs is equal
    if length/2 == size:
        if length == 2:
            return tuple(id_pairs)
        else:
            return id_pairs
    # They are not equal. Fill in the id pairs with the last one until they
    # are the same
    else:
        last_pair = id_pairs[-1]
        additions = size / (length/2) - 1
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

def determine_files(inputlist, inst=None, **kwargs):
    """
    This function takes either a list of comma-separated file names or a list
    of runs in the syntax of findnexus. If the input list begins with /, ~, $
    or ., it will assume that this is a list of full file path names and will
    not use the findnexus utility. If the input list begins with a number, it
    will use the findnexus utility to locate the data files. Files not found
    by the system will be removed from the list.

    Parameters:
    ----------
    -> inputlist is a string containing either fully qualified filenames or
       run numbers
    -> inst is a string containing the name of the instrument for file lookup
    -> kwargs is a list of keyword arguments that the function accepts:
         stop_on_none=<boolean> is a flag that sets the priority for examining
                                the files. If this is set to true, it will
                                cause the driver to crash if it cannot find
                                any files. The default behavior is False.
         one_file=<boolean> is a flag that tells the function that there will
                            be only one file name associated with this call.
                            The default value is False.

    Returns:
    -------
    <- A list of fully qualified file names
    """

    # Check on keywords
    try:
        stop_on_none = kwargs["stop_on_none"]
    except KeyError:
        stop_on_none = False

    try:
        one_file = kwargs["one_file"]
    except KeyError:
        one_file = False

    # Kickout is inputlist is of NoneType
    if inputlist is None:
        return None

    try:
        if __check_for_path(inputlist):
            filelist = inputlist.split(',')
        elif __check_for_digit(inputlist):
            filelist = __run_findnexus(inputlist, inst)
        else:
            raise RuntimeError("Do not know how to interpret %s" % inputlist)
    except AttributeError:
        if __check_for_path(inputlist[0]):
            filelist = inputlist
        elif __check_for_digit(inputlist[0]):
            filelist = []
            for number in inputlist:
                filelist.extend(__run_findnexus(number, inst))
        else:
            raise RuntimeError("Do not know how to interpret %s" % inputlist)

    import copy
    tmplist = copy.deepcopy(filelist)
    counter = 0
    for infile in tmplist:
        if not file_exists(infile):
            print "Data file [%s] does not exist, removing from list" % \
                  infile
            filelist.remove(infile)
        else:
            filelist[counter] = fix_filename(infile)
        counter += 1
    del tmplist

    filelist_size = len(filelist)
    if filelist_size == 0 and stop_on_none:
        raise RuntimeError("No valid files are present. Reduction cannot "\
                           +"be run.")
    elif filelist_size > 0:
        if one_file:
            return filelist[0]
        else:
            return filelist
    else:
        return None

# Private Helper functions for determine_files function
     
def __check_for_digit(nums):
    """
    This function checks a string to see if the first value is a number.
    """
    return nums[0].isdigit()

def __check_for_path(path):
    """
    This function checks a string for full file path identifiers.
    """
    return path.startswith("/") or path.startswith("$") or \
           path.startswith(".") or path.startswith("~") or \
           path[0].isalpha()

def __clean_str(string):
    """
    This function strips whitespace and line breaks from the right side of a
    string
    """
    import os
    return string.rstrip().rstrip(os.linesep)

def __run_cmd(cmd, lines=True):
    """
    This function runs a command and provides the output back. Commands
    returning single lines of output need to set the second argument to False.
    """
    import os
    fin, fout = os.popen4(cmd)
    if lines:
        return fout.readlines()
    else:
        return fout.read()
        
def __run_findnexus(nums, inst):
    """
    This function runs the findnexus command and returns the discovered files.
    """
    cmd = "findnexus -s -i %s %s" % (inst, nums)
    filestring = __clean_str(__run_cmd(cmd, False))
    return filestring.split(' ')
    
def program_version():
    """
    This function returns a version string for an option parser.

    Returns:
    -------
    <- A string containing a place holder for the program name and the
       version string
    """
    from version import version as __version__
    
    ver_tag = []
    ver_tag.append("%prog")
    ver_tag.append(__version__)
    
    return " ".join(ver_tag)
