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

def run(config):
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
    d_som2 = dr_lib.integrate_spectra(d_som1, start=200, end=200, bin_index=True)

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
    
    # set up the options available
    parser = hlr_utils.InstOptions("usage: %prog [options] <datafile>", None, 
                                   None, hlr_utils.program_version(), 'error')
                                  
    parser.set_defaults(data_paths="/entry/bank1,1")
    
    (options, args) = parser.parse_args()

    # set up the configuration
    configure = hlr_utils.Configure()

    # Call the configuration setter for SnsOptions
    hlr_utils.InstConfiguration(parser, configure, options, args)

    # run the program
    run(configure)
        
