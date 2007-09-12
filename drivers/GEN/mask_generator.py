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

"""
This program creates a region-of-interest (ROI) or a masking file based on the
bank names and pixel ranges provided at the command-line. The resulting file is
a list of pixel IDs in the form of I{bankN_x_y}.
"""

def run(config):
    """
    This method is where the data reduction process gets done.

    @param config: Object containing the data reduction configuration
                   information.
    @type config: L{hlr_utils.Configure}
    """
    index = 0

    if config.append:
        option = "a"
    else:
        option = "w"

    resource = open(config.output, option)

    for pid in config.bank_ids:

        try:
            h_min = config.h_ranges[index][0]
        except TypeError:
            h_min = config.h_ranges[0]

        try:
            h_max = config.h_ranges[index][1]+1
        except TypeError:
            h_max = config.h_ranges[1]+1

        for i in xrange(h_min, h_max):

            try:
                v_min = config.v_ranges[index][0]
            except TypeError:
                v_min = config.v_ranges[0]
                
            try:
                v_max = config.v_ranges[index][1]+1
            except TypeError:
                v_max = config.v_ranges[1]+1    

            for j in xrange(v_min, v_max):

                print >> resource, "bank%s_%d_%d" % (pid, i, j) 
                
        index += 1

    resource.close()

if __name__ == "__main__":
    import hlr_utils

    # Make description for driver
    result = []
    result.append("This driver generates a pixel ID file that can be used as")
    result.append("a region-of-interest (ROI) or a masking file. The pixel")
    result.append("ID format in the resulting file is \"bankN_x_y\". The")
    result.append("default filename for the resulting file is pixel_mask.dat.")

    # set up the options available
    parser = hlr_utils.BasicOptions("usage: %prog [options] <datafile>", None,
                                    None, hlr_utils.program_version(), 'error',
                                  " ".join(result))

    parser.add_option("", "--bank-ids", dest="bank_ids",
                      help="Specify the comma separated list of bank IDs that"\
                      +" correspond to the pairs of pixel ranges that will "\
                      +"be in the --pixel-ranges flag")
    
    parser.add_option("", "--h-ranges", dest="h_ranges",
                      help="Specify the comma separated list of horizontal "\
                      +"pixel IDs. This list must contain "\
                      +"as many pairs as the number of bank IDs provided "\
                      +"via the --bank-ids flag. If not, the last pair will "
                      +"be used for the remaining bank IDs")

    parser.add_option("", "--v-ranges", dest="v_ranges",
                      help="Specify the comma separated list of vertical "\
                      +"pixel IDs. This list must contain "\
                      +"as many pairs as the number of bank IDs provided "\
                      +"via the --bank-ids flag. If not, the last pair will "
                      +"be used for the remaining bank IDs")

    parser.add_option("-a", "--append", action="store_true", dest="append",
                      help="Flag for turning on ability to append to mask "\
                      +"file")
    parser.set_defaults(append=False)

    (options, args) = parser.parse_args()

    # set up the configuration
    configure = hlr_utils.Configure()

    if options.output:
        configure.output = hlr_utils.fix_filename(options.output)
    else:
        configure.output = "pixel_mask.dat"

    # set the list of bank IDs
    if options.bank_ids is not None:
        configure.bank_ids = options.bank_ids.split(',')
    else:
        parser.error("Must provide a list of bank ids via the --bank-ids "\
                     +"flag.")

    # set the list of horizontal pixel range pairs
    if options.h_ranges is not None:
        configure.h_ranges = hlr_utils.create_id_pairs(\
            options.h_ranges,
            options.bank_ids)
    else:
        parser.error("Must provide a list of horizontal pixel ranges via the "\
                     +"--h-ranges flag.")

    # set the list of vertical pixel range pairs
    if options.v_ranges is not None:
        configure.v_ranges = hlr_utils.create_id_pairs(\
            options.v_ranges,
            options.bank_ids)
    else:
        parser.error("Must provide a list of vertical pixel ranges via the "\
                     +"--v-ranges flag.")

    configure.append = options.append

    run(configure)
