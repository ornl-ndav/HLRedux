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

class BasicOptions(optparse.OptionParser):
    """
    This class provides a basic set of options for programs. It provides the
    ability for communicating information from the program, prodviding data
    to the program and providing output from the program.
    """
    
    def __init__(self, usage=None, option_list=None):
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
        optparse.OptionParser.__init__(self, usage, option_list)

        # options for debug printing
        self.add_option("-v", "--verbose", action="store_true", dest="verbose",
                        help="Enable verbose print statements")
        self.set_defaults(verbose=False)
        
        self.add_option("-q", "--quiet", action="store_false", dest="verbose",
                        help="Disable verbose print statements")
        
        # output options
        self.add_option("-o", "--output", help="Specify the output file name")

        # specifying data sets
        self.add_option("", "--data", help="Specify the data file")


class SNSOptions(BasicOptions):
    """
    This class provides options more inline with neutron scattering data.
    It provides various instrument characterization options that can be
    tailored to the various instrument classes by using keyword arguments.
    """
    
    def __init__(self, usage=None, option_list=None, **kwargs):
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
        BasicOptions.__init__(self, usage, option_list)

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
