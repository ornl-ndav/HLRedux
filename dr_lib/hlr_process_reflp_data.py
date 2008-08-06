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

def process_reflp_data(datalist, conf, roi_file):
    """
    This function combines Steps 1 through 5 in section 2.4.6.1 of the data
    reduction process for Reduction from TOF to lambda_T as specified by
    the document at
    U{http://neutrons.ornl.gov/asg/projects/SCL/reqspec/DR_Lib_RS.doc}. The
    function takes a list of file names, a L{hlr_utils.Configure} object,
    region-of-interest (ROI) file for the normalization dataset and processes
    the data accordingly.

    @param datalist: The filenames of the data to be processed
    @type datalist: C{list} of C{string}s

    @param conf: Object that contains the current setup of the driver
    @type conf: L{hlr_utils.Configure}

    @param roi_file: The file containing the list of pixel IDs for the region
                     of interest. This only applies to normalization data. 
    @type roi_file: C{string}


    @return: Object that has undergone all requested processing steps
    @rtype: C{SOM.SOM}
    """
    pass
