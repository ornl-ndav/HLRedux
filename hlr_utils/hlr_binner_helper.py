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

def create_binner_string(config):
    """
    This function takes a L{hlr_utils.Configure} object, removes the
    elements from it that are not fundamental to a given run of the data
    reduction and create an MD5 sum ID from that configuration.

    @param config: The current data reduction configuration
    @type config: L{hlr_utils.Configure}


    @return: A unique string based off an MD5 sum of the amended configuration
    @rtype: C{string}
    """
    import copy
    import hashlib

    cconf = copy.deepcopy(config)

    # Remove certain aspects of configuration that do not constitute needing
    # a brand new 3D mesh.

    del cconf.__dict__["lambda_bins"]
    del cconf.__dict__["verbose"]
    del cconf.__dict__["path_replacement"]
    del cconf.__dict__["ext_replacement"]
    del cconf.__dict__["dsmon_path"]
    del cconf.__dict__["so_axis"]
    del cconf.__dict__["data_paths"]
    del cconf.__dict__["output"]
    if "file" in cconf.__dict__:
        del cconf.__dict__["file"]
    if "socket" in cconf.__dict__:
        del cconf.__dict__["socket"]
    if "dump_tof_comb" in cconf.__dict__:
        del cconf.__dict__["dump_tof_comb"]        
    if "dump_wave_comb" in cconf.__dict__:
        del cconf.__dict__["dump_wave_comb"]
    if "dump_et_comb" in cconf.__dict__:
        del cconf.__dict__["dump_et_comb"]

    # Get the keys, sort them and create the string. This should make a more
    # stable MD5 sum.
    
    ckeys = cconf.__dict__.keys()
    ckeys.sort()

    result = []
    for ckey in ckeys:
        result.append("%s:%s" % (ckey, str(cconf.__dict__[ckey])))

    output = " ".join(result)
    return hashlib.new("md5", output).hexdigest()

def make_binner_connection(conn_info):
    """
    This function takes a filename that contains the host name (or IP address)
    and port number of a rebinner server instance. From this it will create and
    make the socket connection between the DR instance and the rebinner server.
    The file consists of a single line with the host name (or IP address) and
    port number separated by a space.

    @param conn_info: Filename containing the host name (or IP address) and
                      port number information.
    @type conn_info: C{string}


    @return: A socket connection
    @rtype: C{socket}
    """
    import socket
    isocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Get the connection information

    cfile = open(conn_info, 'r')
    for line in cfile:
        hostname, portnum = line.split(' ')[:2]
    cfile.close()

    isocket.connect((hostname, int(portnum)))

    return isocket
