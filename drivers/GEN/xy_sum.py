#!/usr/bin/env python

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
This program reads a TOF U{NeXus<www.nexusformat.org>} file and creates a
summed value for every pixel in the given detector bank(s).
"""

def run(config):
    """
    This method is where the processing is done.

    @param config: Object containing the driver configuration information.
    @type config: L{hlr_utils.Configure}
    """
    if config.data is None:
        raise RuntimeError("Need to pass a data filename to the driver "\
                           +"script.")

    so_axis = "time_of_flight"
        
    if config.verbose:
        print "Reading data file"

    d_som1 = dr_lib.add_files(config.data, 
                              Data_Paths=config.data_paths.toPath(), 
                              SO_Axis=so_axis, 
                              Verbose=config.verbose)[0] 
  
    # Use start and end keywords to make slices (see online docs)
    d_som2 = dr_lib.integrate_spectra(d_som1, start=config.start,
                                      end=config.end, bin_index=config.bin)

    del d_som1

    hlr_utils.write_file(config.output, "text/num-info", d_som2, 
                         output_ext="xys", 
                         data_ext=config.ext_replacement, 
                         path_replacement=config.path_replacement, 
                         verbose=config.verbose, 
                         message="xy sums", 
                         tag="Integral", units="counts") 
    

if __name__ == "__main__":
    import dr_lib
    import hlr_utils

    # Make description for driver
    result = []
    result.append("This driver reads a TOF NeXus file and creates a *.xys")
    result.append("file containing a numeric sum of count values for each")
    result.append("pixel present in the provided detector bank.")
    
    # set up the options available
    parser = hlr_utils.InstOptions("usage: %prog [options] <datafile>", None, 
                                   None, hlr_utils.program_version(), 'error')
                                  
    parser.set_defaults(data_paths="/entry/bank1,1")

    parser.add_option("-s", "--start", dest="start", type="float",
                      help="Specify the starting TOF for the sum.")

    parser.add_option("-e", "--end", dest="end", type="float",
                      help="Specify the ending TOF for the sum.")

    parser.add_option("-b", "--bin", dest="bin", action="store_true",
                      help="Flag to specify that start and end values are "\
                      +"bin indicies.")
    parser.set_defaults(bin=False)
    
    (options, args) = parser.parse_args()

    # set up the configuration
    configure = hlr_utils.Configure()

    # Call the configuration setter for InstOptions
    hlr_utils.InstConfiguration(parser, configure, options, args)

    # Set the starting TOF value
    configure.start = options.start

    # Set the ending TOF value
    configure.end = options.end    

    # Set the bin index flag
    configure.bin = options.bin

    # run the program
    run(configure)
        
