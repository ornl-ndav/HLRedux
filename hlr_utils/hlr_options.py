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

import optparse

import hlr_utils

class BasicOptions(optparse.OptionParser):
    """
    This class provides a basic set of options for programs. It provides the
    ability for communicating information from the program, prodviding data
    to the program and providing output from the program.
    """
    
    def __init__(self, usage=None, option_list=None, option_class=None,
                 version=None, conflict_handler='error', description=None,
                 **kwarg):
        """
        Constructor for BasicOptions

        Parameters:
        ----------
        -> usage (OPTIONAL) is a string that will print the correct usage of
                 program in which the option class is used
        -> option_list (OPTIONAL) is a list containing the alternative method
                       of providing options
        """
        # parent constructor
        optparse.OptionParser.__init__(self, usage, option_list,
                                       optparse.Option, version,
                                       conflict_handler, description)

        # options for debug printing
        self.add_option("-v", "--verbose", action="store_true", dest="verbose",
                        help="Enable verbose print statements")
        self.set_defaults(verbose=False)
        
        self.add_option("-q", "--quiet", action="store_false", dest="verbose",
                        help="Disable verbose print statements")
        
        # output options
        self.add_option("-o", "--output", help="Specify a new output file "\
                        +"name, a new data directory or a new directory plus "\
                        +"output file name. The new directory must exist. "\
                        +"All intermediate files will be based off of the "\
                        +"provided file name. The default is to use the "\
                        +"current working directory and the first data file "\
                        +"as the basis for the output file names.")

        # specifying data sets
        self.add_option("", "--data", help="Specify the data file")

def BasicConfiguration(parser, configure, options, args):
    """
    This function sets the incoming Configure object with all the options that
    have been specified via the BasicOptions object.

    Parameters:
    ----------
    -> parser is the BasicOptions parser object unless from inherited class
    -> configure is the Configure object
    -> options is the parsed options from BasicOptions
    -> args is the parsed arguments from BasicOptions
    """

    # Set the verbosity
    configure.verbose = options.verbose

    # Get the datafile name and check it
    if options.data is not None:
        configure.data = hlr_utils.determine_files(options.data,
                                                   configure.inst,
                                                   stop_on_none=True)
    elif len(args) > 0:
        configure.data = hlr_utils.determine_files(args, configure.inst,
                                                   stop_on_none=True)
    else:
        parser.error("Did not specify a datafile")
        

    import os
    # Deal with file or directory from output option
    if options.output:
        filepath = hlr_utils.fix_filename(options.output)
        if os.path.exists(filepath):
            if os.path.isdir(filepath):
                outfile = os.path.basename(configure.data[0])
                path = os.path.join(filepath, outfile)
                configure.output = hlr_utils.ext_replace(path, "nxs", "txt")
                configure.path_replacement = filepath
                configure.ext_replacement = "txt"

            elif os.path.isfile(filepath):
                configure.output = filepath
                configure.path_replacement = os.path.dirname(filepath)
                configure.ext_replacement = filepath.split('.')[-1]

            else:
                parser.error("Cannot handle %s in output option" % filepath)
        else:
            # Assume that this is a file and hope that the directory exists
            directory = os.path.dirname(filepath)
            if directory != "":
                if not os.path.exists(directory):
                    raise RuntimeError("The directory %s must exist!" \
                                       % directory)
                else:
                    pass
            else:
                directory = None
            configure.output = filepath
            configure.path_replacement = directory
            configure.ext_replacement = filepath.split('.')[-1]
            
    # Create the output file name if there isn't one supplied
    else:
        outfile = os.path.basename(configure.data[0])
        path = os.path.join(os.getcwd(), outfile)
        configure.output = hlr_utils.ext_replace(path, "nxs", "txt")
        configure.path_replacement = None
        configure.ext_replacement = "txt"

    if configure.verbose:
        print "Using %s as output file" % configure.output

class SNSOptions(BasicOptions):
    """
    This class provides options more inline with neutron scattering data.
    It provides various instrument characterization options that can be
    tailored to the various instrument classes by using keyword arguments.
    """
    
    def __init__(self, usage=None, option_list=None, option_class=None,
                 version=None, conflict_handler='error', description=None,
                 **kwargs):
        """
        Constructor for SNSOptions

        Parameters:
        ----------
        -> usage (OPTIONAL) is a string that will print the correct usage of
                 program in which the option class is used
        -> option_list (OPTIONAL) is a list containing the alternative method
                       of providing options
        -> kwargs is a list of keyword arguments that the function accepts
           inst=<string> is a string containing the type name of the
                         instrument. Current names are DGS, IGS, PD, REF, SAS,
                         SCD.
        """
        # parent constructor
        BasicOptions.__init__(self, usage, option_list, optparse.Option,
                              version, conflict_handler, description)

        # check for keywords
        try:
            instrument = kwargs["inst"]
        except KeyError:
            instrument = ""

        # General instrument driver options

        self.add_option("", "--inst-geom", dest="inst_geom",
                        metavar="FILENAME",
                        help="Specify the instrument geometry file")

        self.add_option("", "--data-paths", dest="data_paths",
                        help="Specify the comma separated list of detector "\
                        +"data paths and signals.")

        self.add_option("", "--inst", dest="inst",
                        help="Specify the short name for the instrument.")

        # Instrument characterization file options
        self.add_option("", "--norm", help="Specify the normalization file")
        
        if instrument == "IGS":
            self.add_option("", "--ecan",
                            help="Specify the empty sample container file")
        
            self.add_option("", "--back",
                            help="Specify the background (empty instrument) "\
                            +"file")

        else:
            pass

def SnsConfiguration(parser, configure, options, args, **kwargs):
    """
    This function sets the incoming Configure object with all the options that
    have been specified via the SNSOptions object.

    Parameters:
    ----------
    -> parser is the SNSOptions parser object unless from inherited class
    -> configure is the Configure object
    -> options is the parsed options from SNSOptions
    -> args is the parsed arguments from SNSOptions
    """

    # Check for keywords
    try:
        instrument = kwargs["inst"]
    except KeyError:
        instrument = ""

    # Define instrument short name first as stuff below depends on it
    if options.inst is None:
        import sns_inst_utils
        configure.inst = sns_inst_utils.getInstrument()
    else:
        configure.inst = options.inst

    # Call the configuration setter for BasicOptions
    BasicConfiguration(parser, configure, options, args)

    # Set the instrument geometry file
    configure.inst_geom = hlr_utils.determine_files(options.inst_geom,
                                                    one_file=True)

    # Set the data paths
    configure.data_paths = hlr_utils.create_data_paths(options.data_paths)

    # Set the normalization file list
    configure.norm = hlr_utils.determine_files(options.norm, configure.inst)

    if instrument == "IGS":
        # Set the empty can file list
        configure.ecan = hlr_utils.determine_files(options.ecan,
                                                   configure.inst)
        # Set the background file list
        configure.back = hlr_utils.determine_files(options.back,
                                                   configure.inst)
    else:
        pass

