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

class SNSOptions(optparse.OptionParser):
    def __init__(self,usage=None,option_list=None):
        # parent constructor
        optparse.OptionParser.__init__(self,usage,option_list)

        # options for debug printing
        self.add_option("-v","--verbose",action="store_true",default=False,
                        dest="verbose",
                        help="Enable verbose print statements")
        self.add_option("-q","--quiet",action="store_false",dest="verbose",
                        help="Disable verbose print statements")
        
        # output options
        self.add_option("-o","--output",default=None,
                        help="Specify the output file name (the '.srf' file)")

        # specifying data sets
        self.add_option("","--data",default=None,
                        help="Specify the data file")
        self.add_option("","--ecan",default=None,
                        help="Specify the empty container file")
        self.add_option("","--norm",default=None,
                        help="Specify the normalization file")
        self.add_option("","--data-bkg",default=None,
                        help="Specify the data background file")
        self.add_option("","--ecan-bkg",default=None,
                        help="Specify the empty container background file")
        self.add_option("","--norm-bkg",default=None,
                        help="Specify the normalization background file")
        self.add_option("","--dark-count",default=None,
                        help="Specify the dark count file")
        
