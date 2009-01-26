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
                 **kwargs):
        """
        Constructor for C{BasicOptions}

        @param usage: (OPTIONAL) The correct usage of program in which the
                      option class is used
        @type usage: C{string}
        
        @param option_list: (OPTIONAL) A list containing the alternative method
                            of providing options
        @type option_list: C{list}

        @param option_class: (OPTIONAL) The options class type
        @type option_class: C{optparse.Option}
        
        @param version: (OPTIONAL) The program version
        @type version: C{string}

        @param conflict_handler: (OPTIONAL) How the parser handles conflicts
                                 between options.
        @type conflict_handler: C{string}

        @param description: (OPTIONAL) The program description
        @type description: C{string}
        
        @param kwargs: A list of keyword arguments that the function accepts:
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

        # specify the instrument
        self.add_option("-i", "--inst", dest="inst",
                        help="Specify the short name for the instrument.")

        # specify the facility
        self.add_option("-f", "--facility", dest="facility",
                        help="Specify the short name for the facility.")

        # specift the desired proposal
        self.add_option("-p", "--proposal", dest="proposal",
                        help="Specify the proposal for the requested data "\
                        +"if a run number is being provided.")
        
        # specifying data sets
        self.add_option("", "--data", help="Specify the data file")

        # specify a configuration file
        self.add_option("", "--config", dest="config",
                        help="Specify a configuration file (*.rmd)")

def BasicConfiguration(parser, configure, options, args):
    """
    This function sets the incoming C{Configure} object with all the options
    that have been specified via the C{BasicOptions} object.

    @param parser: The parser object
    @type parser: L{hlr_utils.BasicOptions}
    
    @param configure: The configuration object
    @type configure: L{hlr_utils.Configure}
    
    @param options: The parsed options from C{BasicOptions}
    @type options: C{Option}

    @param args: The parsed arguments from C{BasicOptions}
    @type args: C{list}
    """

    # Set from a configuration file first
    if options.config is not None:
        import xml.dom.minidom
        conf_doc = xml.dom.minidom.parse(options.config)
        configure = hlr_utils.ConfigFromXml(conf_doc, configure)

    # Now override options provided on command-line

    # Set the verbosity, if present on command-line
    if not configure.verbose:
        configure.verbose = options.verbose 
    else: 
        # Got the verbosity from the config file, but check CLI 
        if hlr_utils.cli_checker("-v", "-q"): 
            # Override option 
            configure.verbose = options.verbose 
        else: 
            # No flags present, do nothing
            pass 

    # Define instrument short name first as stuff below depends on it
    if hlr_utils.cli_provide_override(configure, "inst", "--inst"):
        configure.inst = options.inst

    # Define facility short name as stuff below depends on it
    if hlr_utils.cli_provide_override(configure, "facility", "--facility"):
        configure.facility = options.facility        

    # Define proposal as stuff below depends on it.
    if hlr_utils.cli_provide_override(configure, "proposal", "--proposal"):
        configure.proposal = options.proposal
        
    # Get the datafile name and check it
    if options.data is not None:
        configure.data = hlr_utils.determine_files(options.data,
                                                   configure.inst,
                                                   configure.facility,
                                                   configure.proposal,
                                                   stop_on_none=True)
    elif len(args) > 0:
        configure.data = hlr_utils.determine_files(args, configure.inst,
                                                   configure.facility,
                                                   configure.proposal,
                                                   stop_on_none=True)
    elif configure.data:
        # We have data from the config file, so everything is OK.
        pass
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

    elif configure.output:
        # We have an output file, so no need to do anything else
        try:
            configure.path_replacement
        except AttributeError:
            configure.path_replacement = None
    # Create the output file name if there isn't one supplied
    else:
        outfile = os.path.basename(configure.data[0])
        path = os.path.join(os.getcwd(), outfile)
        configure.output = hlr_utils.ext_replace(path, "nxs", "txt")
        configure.path_replacement = None
        configure.ext_replacement = "txt"

    if configure.verbose and options.output:
        print "Using %s as output file" % configure.output

class InstOptions(BasicOptions):
    """
    This class provides options more in line with neutron scattering data.
    It provides various instrument characterization options that can be
    tailored to the various instrument classes by using keyword arguments.
    """
    
    def __init__(self, usage=None, option_list=None, option_class=None,
                 version=None, conflict_handler='error', description=None,
                 **kwargs):
        """
        Constructor for C{InstOptions}

        @param usage: (OPTIONAL) The correct usage of program in which the
                                 option class is used
        @type usage: C{string}
        
        @param option_list: (OPTIONAL) A list containing the alternative method
                                       of providing options
        @type option_list: C{list}

        @param option_class: (OPTIONAL) The options class type
        @type option_class: C{optparse.Option}
        
        @param version: (OPTIONAL) The program version
        @type version: C{string}

        @param conflict_handler: (OPTIONAL) How the parser handles conflicts
                                            between options.
        @type conflict_handler: C{string}

        @param description: (OPTIONAL) The program description
        @type description: C{string}
        
        @param kwargs: A list of keyword arguments that the function accepts:

        @keyword inst: The classification type name of the instrument. Current
                       names are I{DGS}, I{IGS}, I{PD}, I{REF}, I{SAS}, I{SCD}.
        @type inst: C{string}
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

        # Instrument characterization file options
        self.add_option("", "--norm", help="Specify the normalization file")
        
        if instrument == "IGS":
            self.add_option("", "--ecan",
                            help="Specify the empty sample container file")
        
            self.add_option("", "--back",
                            help="Specify the background (empty instrument) "\
                            +"file")

            self.add_option("", "--dsback",
                            help="Specify the direct scattering background "\
                            +"(sample data at baseline temperature) file") 

        elif instrument == "SAS":
            self.add_option("", "--ecan",
                            help="Specify the empty sample container file")

            self.add_option("", "--solv",
                            help="Specify the solvent/buffer only file")

            self.add_option("", "--open",
                            help="Specify the open beam file")

            self.add_option("", "--dkcur",
                            help="Specify the dark current file")

        elif instrument == "DGS":
            self.add_option("", "--ecan",
                            help="Specify the empty sample container file")

            self.add_option("", "--bcan",
                            help="Specify the black sample container file")

            self.add_option("", "--dkcur",
                            help="Specify the dark current file")

        else:
            pass

def InstConfiguration(parser, configure, options, args, **kwargs):
    """
    This function sets the incoming C{Configure} object with all the options
    that have been specified via the C{InstOptions} object.

    @param parser: The parser object
    @type parser: L{hlr_utils.InstOptions}
    
    @param configure: The configuration object
    @type configure: L{hlr_utils.Configure}
    
    @param options: The parsed options from C{InstOptions}
    @type options: C{Option}

    @param args: The parsed arguments from C{InstOptions}
    @type args: C{list}

    @param kwargs: A list of keyword arguments that the function accepts:

    @keyword inst: The classification type name of the instrument. Current
                   names are I{DGS}, I{IGS}, I{PD}, I{REF}, I{SAS}, I{SCD}.
    @type inst: C{string}
    """
    
    # Check for keywords
    try:
        instrument = kwargs["inst"]
    except KeyError:
        instrument = ""

    # Call the configuration setter for BasicOptions
    BasicConfiguration(parser, configure, options, args)

    # Set the instrument geometry file
    if hlr_utils.cli_provide_override(configure, "inst_geom", "--inst-geom"):
        configure.inst_geom = hlr_utils.determine_files(options.inst_geom,
                                                        one_file=True)

    # Set the data paths
    if hlr_utils.cli_provide_override(configure, "data_paths", "--data-paths"):
        configure.data_paths = hlr_utils.NxPath(options.data_paths)

    # Set the normalization file list
    if hlr_utils.cli_provide_override(configure, "norm", "--norm"):
        configure.norm = hlr_utils.determine_files(options.norm,
                                                   configure.inst,
                                                   configure.facility)

    if instrument == "IGS":
        # Set the empty can file list
        if hlr_utils.cli_provide_override(configure, "ecan", "--ecan"):
            configure.ecan = hlr_utils.determine_files(options.ecan,
                                                       configure.inst,
                                                       configure.facility)
        # Set the background file list
        if hlr_utils.cli_provide_override(configure, "back", "--back"):
            configure.back = hlr_utils.determine_files(options.back,
                                                       configure.inst,
                                                       configure.facility)

        # Set the direct scattering background file list
        if hlr_utils.cli_provide_override(configure, "dsback", "--dsback"):
            configure.dsback = hlr_utils.determine_files(options.dsback,
                                                         configure.inst,
                                                         configure.facility)
    elif instrument == "SAS":
        # Set the empty can file list
        if hlr_utils.cli_provide_override(configure, "ecan", "--ecan"):
            configure.ecan = hlr_utils.determine_files(options.ecan,
                                                       configure.inst,
                                                       configure.facility)
        # Set the empty can file list
        if hlr_utils.cli_provide_override(configure, "solv", "--solv"):
            configure.solv = hlr_utils.determine_files(options.solv,
                                                       configure.inst,
                                                       configure.facility)
        # Set the empty can file list
        if hlr_utils.cli_provide_override(configure, "open", "--open"):
            configure.open = hlr_utils.determine_files(options.open,
                                                       configure.inst,
                                                       configure.facility)

        # Set the empty can file list
        if hlr_utils.cli_provide_override(configure, "dkcur", "--dkcur"):
            configure.dkcur = hlr_utils.determine_files(options.dkcur,
                                                        configure.inst,
                                                        configure.facility)

    elif instrument == "DGS":
        # Set the empty can file list
        if hlr_utils.cli_provide_override(configure, "ecan", "--ecan"):
            configure.ecan = hlr_utils.determine_files(options.ecan,
                                                       configure.inst,
                                                       configure.facility)

        # Set the black can file list
        if hlr_utils.cli_provide_override(configure, "bcan", "--bcan"):
            configure.bcan = hlr_utils.determine_files(options.bcan,
                                                       configure.inst,
                                                       configure.facility)
        
        # Set the empty can file list
        if hlr_utils.cli_provide_override(configure, "dkcur", "--dkcur"):
            configure.dkcur = hlr_utils.determine_files(options.dkcur,
                                                        configure.inst,
                                                        configure.facility)
            
    else:
        pass

