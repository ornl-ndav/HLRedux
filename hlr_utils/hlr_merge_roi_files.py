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

def merge_roi_files(filelist):
    """
    This function takes a set of ROI files and combines them into a new ROI
    file.

    @param filelist: The set of ROI file names.
    @type filelist: C{list}


    @return: The filename of the combined ROI
    @rtype: C{string}
    """
    import hlr_utils
    # Get first set of pixel IDs
    rfile = open(filelist[0], 'r')
    roi_set = set([id.strip() for id in rfile])
    rfile.close()

    # Merge each of the other sets of pixel IDs
    for filename in filelist[1:]:
        rfile = open(filename, 'r')
        for id in rfile:
            roi_set.add(id.strip())
        rfile.close()

    # Create new ROI file from combined information
    ofilename = hlr_utils.add_tag(filelist[0], "comb")
    ofile = open(ofilename, 'w')
    for id in roi_set:
        print >> ofile, id
    ofile.close()
    
    return ofilename
