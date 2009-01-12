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

def filter_normalization(obj, threshold, config=None):
    """
    This function takes an object with normalization integration information
    and a threshold and creates a mask file containing the pixel IDs that do
    not make it above the threshold.

    @param obj: The object containing the normalization information
    @type obj: C{SOM.SOM}

    @param threshold: The upper bound for masked pixels
    @type threshold: C{float}

    @param config: The object holding the DR configuration
    @type config: L{hlr_utils.Configure}


    @raise TypeError: The incoming object is not a C{SOM}.
    """
    import hlr_utils

    o_descr = hlr_utils.get_descr(obj)
    if o_descr != "SOM":
        raise TypeError("Only SOMs are allowed in this function!")

    if config is None:
        # Make mask file name from object information
        instname = obj.attr_list.inst.get_name()
        runnum = obj.attr_list["run_number"]
        outfile = "%s_%s_mask.dat" % (instname, str(runnum))
    else:
        # Make mask file name from configuration information
        outfile = hlr_utils.ext_replace(config.output, config.ext_replacement,
                                        "dat")
        outfile = hlr_utils.add_tag(outfile, "mask")

    ofile = open(outfile, "w")

    import SOM
    import utils
    
    len_obj = hlr_utils.get_length(obj)
    for i in xrange(len_obj):
        norm = hlr_utils.get_value(obj, i, o_descr)
        if utils.compare(norm, threshold) <= 0:
            map_so = hlr_utils.get_map_so(obj, None, i)
            pix_id = SOM.NeXusId.fromString(str(map_so.id)).toJoinedStr()

            print >> ofile, pix_id

    ofile.close()
