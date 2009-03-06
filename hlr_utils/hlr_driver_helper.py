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

    @param filename: The filename to check existence
    @type filename: C{string}

    
    @return: I{True} if the file exists and I{False} if is does not
    @rtype: C{boolean}
    """
    
    import os.path

    return os.path.isfile(fix_filename(filename))


def ext_replace(name, ext_out, ext_in):
    """
    This function takes a filename and an extension (without the dot) and
    replaces that extension with new given extension (again without the dot).

    @param name: The filename for extension replacement
    @type name: C{string}
    
    @param ext_out: The extension being replaced
    @type ext_out: C{string}
    
    @param ext_in: The replacing extension
    @type ext_in: C{string}

    @return: The old filename with the extension replaced
    @rtype: C{string}
    """

    import re
    expression = r'\.'+ext_out+'$'
    myre = re.compile(expression)

    return myre.sub("", name) + '.' + ext_in

def add_tag(filename, tag):
    """
    This function takes a filename, splits it at the extension and appends a
    tag in front of the extension.

    @param filename: The filename to which to add the tag
    @type filename: C{string}

    @param tag: Tag that will be placed before the file extension
    @type tag: C{string}
    

    @return: The new filename with the tag inserted
    @rtype: C{string}
    """
    
    index = filename.rfind('.')
    return filename[0:index] + "_" + tag + filename[index:]

def split_values(thing):
    """
    This function takes a string object that has the form value,err^2,units or
    value,err^2 or value,units. If the latter version is given, a default
    value of 0.0 will be given for err^2.
    
    @param thing: Comma-separated list of the form value,err^2 or
                  value,err^2,units or value,units
    @type thing: C{string}

    
    @return: Object of the form C{(value,err^2,units)}
    @rtype: C{tuple}
    """

    if thing is None:
        return thing
    
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

    @param axis_min: The minimum value of the axis
    @type axis_min: C{float}
    
    @param axis_max: The maximum value of the axis
    @type axis_max: C{float}
    
    @param delta: The bin width for the axis
    @type delta: C{float}
    
    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword type: The type of axis desired. Type can be I{histogram},
                   I{coordinate} or I{density} (the last two are synonyms).
                   If type is not provided the default is I{histogram}
    @type type: C{string}

    
    @return: The axis generated from the file information
    @rtype: C{nessi_list.NessiList}


    @raise RuntimeError: The type provided via kwarg type is not I{histogram}
                         or I{density} or I{coordinate}
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

    @param filename: Name of the file containing the axis values
    @type filename: C{string}
    
    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword type: The type of axis desired. Type can be I{histogram},
                   I{coordinate} or I{density} (the last two are synonyms).
                   If type is not provided the default is I{histogram}
    @type type: C{string}

    
    @return: The axis generated from the file information
    @rtype: C{nessi_list.NessiList}


    @raise RuntimeError: The type provided via kwarg type is not I{histogram}
                         or I{density} or I{coordinate}
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

    @param filename: The filename to be fixed
    @type filename: C{string}

    
    @return: The filename with special cases expanded
    @rtype: C{string}
    """
    
    import os

    if filename is not None:
        filename = os.path.expanduser(filename)
        filename = os.path.expandvars(filename)
    # Filename is a None type, just pass it back
    else:
        pass

    return filename


def create_data_paths(thing):
    """
    This function takes in a string that contains NeXus path and signal pairs
    and turns them into a tuple (for one pair) or a list of tuples.

    @param thing: A comma-spearated list of NeXus path and signal pairs
    @type thing: C{string}

    
    @return: The NeXus path,signal pairs
    @rtype: C{tuple} or C{list} of C{tuple}s 
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
    a C{SOM}. B{NOTE}: Extra keyword arguments can be passed onto the C{DST}
    instance via calling them in the kwargs list. Those arguments will not be
    processed by this function, but just pass them on.

    @param filename: The name of the data file from which the output is
                     generated or the name of an output file
    @type filename: C{string}
    
    @param dst_type: The MIME type of the output formatter
    @type dst_type: C{string}
    
    @param data: Object that contains the output to be written to file
    @type data: C{SOM.SOM}
    
    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword message: This is part of the message that will be printed to
                      STDOUT if verbose keyword is set to True. The default
                      message is \"output file\"
    @type message: C{string}
    
    @keyword data_ext: This is the extension on the data file. This is used in
                       conjunction with output_ext and replace to convert the
                       data filename into an output filename. The default
                       value is \"nxs\".
    @type data_ext: C{string}
    
    @keyword output_ext: This is the extension to be used for the output file.
                         The default value is \"txt\".
    @type output_ext: C{string}
    
    @keyword verbose: This determines whether or not the print statement is
    executed. The default value is I{False}.
    @type verbose: C{boolean}
    
    @keyword replace_ext: This determines whether or not the extension on the
                          incoming filename is replaced with output_ext. The
                          default behavior is I{True} (replace extension)
    @type replace_ext: C{boolean}
    
    @keyword replace_path: This determines whether or not the directory path on
                           the incoming filename is replaced with the
                           directory where the driver is running. The default
                           behavior is I{True} (replace path)
    @type replace_path: C{boolean}
    
    @keyword path_replacement: This is a directory path that will be prepended
                               to the output filename. The default value is
                               C{None} and will cause the working directory to
                               be the prepended path.
    @type path_replacement: C{string}
    
    @keyword extra_tag: This is a tag that will be inserted into the file name
                        just before the file extension.
    @type extra_tag: C{string}


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
        path_replacement = kwargs["path_replacement"]
    except KeyError:
        path_replacement = None       

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
        if path_replacement is None:
            path_replacement = os.getcwd()
            
        fixed_filename = os.path.join(path_replacement,
                                      os.path.basename(filename))
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
    them into a C{tuple} (for one pair) or a C{list} of C{tuple}s. The function
    checks against the number of data paths requested. If the number of paths
    is not equal to the number of id pairs given, the last id pair is
    duplicated until the number of id pairs is the same as the number of data
    paths

    @param pairs: List of comma-separated pixel id pairs
    @type pairs: C{string}
    
    @param paths: List of comma-separated NeXus data paths and signal pairs
    @type paths: C{string}
    
    @param kwargs: A list of key word arguments that the function accepts:
    
    @keyword inc: A switch to increment the ending ids by 1
    @type inc: C{boolean}


    @return: The pixel id pair(s)
    @rtype: C{tuple} or C{list} of C{tuple}s
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
        temp = paths.split(',')[1]
        if int(temp) == 1:
            size = 1
    except IndexError:
        size = 1
    
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
        counter = 0
        while counter < additions:
            id_pairs.append(last_pair)
            counter += 1

        return id_pairs

def create_pixel_id(thing):
    """
    This function creates a pixel ID out of a comma-delimited list of three
    values, i.e.: bank3,3,63.

    @param thing: Object containing three pieces of information to create a
                  pixel ID
    @type thing: C{string}


    @return: Object containing the pixel ID
    @rtype: C{tuple} C{(\"bankN\", (int(x), int(y)))}


    @raise RuntimeError: 3 pieces of information are not provided to the
                         function
    """

    mylist = thing.split(',')

    if len(mylist) != 3:
        raise RuntimeError("Must provide three pieces of information to the "\
                           +"function")
    else:
        pass

    return (mylist[0], (int(mylist[1]), int(mylist[2])))

def determine_files(inputlist, inst=None, facility=None, proposal=None,
                    **kwargs):
    """
    This function takes either a list of comma-separated file names or a list
    of runs in the syntax of findnexus. If the input list begins with /, ~, $,
    . or character it will assume that this is a list of full file path names
    and will not use the B{findnexus} utility. If the input list begins with a
    number, it will use the B{findnexus} utility to locate the data files.
    Files not found by the system will be removed from the list.

    @param inputlist: Comma-separated fully qualified filenames or run numbers
    @type inputlist: C{string}
    
    @param inst: The name of the instrument for file lookup
    @type inst: C{string}

    @param facility: The name of the facility for file lookup
    @type facility: C{string}

    @param proposal: The name of the prposal for the desired data
    @type proposal: C{string}
    
    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword stop_on_none: Flag that sets the priority for examining the files.
                           If this is set to I{True}, it will cause the driver
                           to crash if it cannot find any files. The default
                           behavior is I{False}.
    @type stop_on_none: C{boolean}
    
    @keyword one_file: Flag that tells the function that there will be only one
                       file name associated with this call. The default value
                       is I{False}.
    @type one_file: C{boolean}


    @return: The fully qualified file names
    @rtype: C{list}
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
            filelist = __run_findnexus(inputlist, inst, facility, proposal)
        else:
            raise RuntimeError("Do not know how to interpret %s" % inputlist)
    except AttributeError:
        if __check_for_path(inputlist[0]):
            filelist = inputlist
        elif __check_for_digit(inputlist[0]):
            filelist = []
            for number in inputlist:
                filelist.extend(__run_findnexus(number, inst, facility,
                                                proposal))
        else:
            raise RuntimeError("Do not know how to interpret %s" % inputlist)

    # This is to convert a list of files making it in as one entry in a list.
    # This happens if arguments to the script (not options) are comma separated
    if len(filelist) == 1:
        filelist = filelist[0].split(',')

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
    # Returns a tuple: (STDIN, STDOUT+STDERR)
    streams = os.popen4(cmd)
    if lines:
        return streams[1].readlines()
    else:
        return streams[1].read()
        
def __run_findnexus(nums, inst, facility, proposal):
    """
    This function runs the findnexus command and returns the discovered files.
    """
    cmd = "findnexus -s -i %s" % inst
    if facility is not None:
        cmd += " -f %s" % facility
    if proposal is not None:
        cmd += " -p %s" % proposal
    cmd += " %s" % nums
        
    filestring = __clean_str(__run_cmd(cmd, False))
    return filestring.split(' ')
    
def program_version():
    """
    This function returns a version string for an option parser.

    @return: A place holder for the program name and the version string
    @rtype: C{string}
    """
    from HLR_version import version as __version__
    
    ver_tag = []
    ver_tag.append("%prog")
    ver_tag.append(__version__)
    
    return " ".join(ver_tag)

def cli_checker(opt1, opt2=None):
    """
    This function checks the command-line arguments against the requested
    options to see if they have been set.

    @param opt1: Option name (beginning with - or --) to search for on the CLI
    @type opt1: C{string}
    
    @param opt2: (OPTIONAL) Option name (beginning with - or --) to search for
                            on the CLI
    @type opt2: C{string}


    @return: I{True} if the option has been set or I{False} if it has not
    @rtype: C{boolean}
    """
    import sys

    if opt2 is not None:
        cli_options = [arg for arg in sys.argv if opt1 in arg or opt2 in arg]
    else:
        cli_options = [arg for arg in sys.argv if opt1 in arg]

    if len(cli_options) > 0:
        return True
    else:
        return False

def cli_provide_override(config, param, opt1, opt2=None):
    """
    This function checks the incoming parameter and uses cli_checker to
    determine if the parameter should be set using the appropriate setter
    function call.

    @param config: Object containing the configuration
    @type config: L{hlr_utils.Configure}
    
    @param param: The parameter name to check
    @type param: C{string}
    
    @param opt1: First CLI option to check
    @type opt1: C{string}
    
    @param opt2: (OPTIONAL) Second CLI option to check
    @type opt2: C{string}


    @return: I{True} if the parameter needs to be provided/overridden or
             I{False} if it should not
    @rtype: C{boolean}
    """
    try:
        if config.__dict__[param] and cli_checker(opt1, opt2):
            return True
        else:
            return False
    except KeyError:
        return True
        
def file_peeker(filename):
    """
    This function opens a file and reads out the first 2 bytes looking for the
    signature of a data reduction produced file. The signatures are I{# } for
    a C{Dave2dDST}, I{#F} for a C{Ascii3ColDST} and I{#I} for a C{NumInfoDST}.

    @param filename: The name of the file to peek into
    @type filename: C{string}


    @return: The DST type of the peeked file
    @rtype: C{string}


    @raise RuntimeError: If the file isn't data reduction produced
    @raise RuntimeError: If the file looks like a DR produced one, but still
                         isn't recognized
    """
    pfile = open(filename, "r")
    peek = pfile.read(2)
    pfile.close()

    if peek.startswith('#'):
        if peek[1] == " ":
            return "text/Dave2d"
        elif peek[1] == "F":
            return "text/Spec"
        elif peek[1] == "I":
            return "text/num-info"
        else:
            raise RuntimeError("Signature of second byte %s not recognized." \
                               % peek[1])
    else:
        raise RuntimeError("File %s is not a data reduction produced file." \
                           % filename)
