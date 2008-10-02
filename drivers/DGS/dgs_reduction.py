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
This program covers the functionality outlined in B{Section 2.1.1 General
sample reduction} in
U{http://neutrons.ornl.gov/asg/projects/SCL/reqspec/DR_Lib_RS.doc}
"""
def run(config, tim=None):
    """
    This method is where the data reduction process gets done.

    @param config: Object containing the data reduction configuration
                   information.
    @type config: L{hlr_utils.Configure}

    @param tim: (OPTIONAL) Object that will allow the method to perform
                           timing evaluations.
    @type tim: C{sns_time.DiffTime}
    """
    import dr_lib
    import DST
    
    if tim is not None:
        tim.getTime(False)
        old_time = tim.getOldTime()

    if config.data is None:
        raise RuntimeError("Need to pass a data filename to the driver "\
                           +"script.")

    # Read in geometry if one is provided
    if config.inst_geom is not None:
        if config.verbose:
            print "Reading in instrument geometry file"
            
        inst_geom_dst = DST.getInstance("application/x-NxsGeom",
                                        config.inst_geom)
    else:
        inst_geom_dst = None

    config.so_axis = "time_of_flight"

    # Step 0: Read in dark current data

    # Step 1: Integrate dark current spectra

    # Step 2: Scale integrated spectra by dark current acquisition time

    # Perform Steps 3-6 on black can data

    # Perform Steps 3-6 on empty can data    

    # Perform Steps 3-6 on normalization data

    # Perform Steps 3-6 on sample data
    d_som1 = dr_lib.calibrate_dgs_data(config.data, config,
                                       inst_geom_dst=inst_geom_dst,
                                       timer=tim)

    # Perform Steps 7-16 on sample data
    d_som2 = dr_lib.process_dgs_data(d_som1, config, timer=tim)

    del d_som1
    
    # Perform Steps 7-16 on normalization data

    # Step 17: Integrate normalization spectra

    # Step 18: Normalize sample data by integrated values

    # Step 19: Calculate the initial energy
    if conf.initial_energy is not None:
        d_som2.attr_list["Initial_Energy"] = conf.initial_energy

    # Steps 20-21: Calculate the energy transfer
    d_som3 = dr_lib.energy_transfer(d_som2, "DGS", "Initial_Energy")

    del d_som2
    
    if tim is not None:
        tim.setOldTime(old_time)
        tim.getTime(msg="Total Running Time")

if __name__ == "__main__":
    import hlr_utils

    # Make description for driver
    description = []
    description.append("This driver runs the data reduction for the Direct")
    description.append("Geometry Spectrometer class of instruments.")
    
    # Set up the options available
    parser = hlr_utils.DgsOptions("usage: %prog [options] <datafile>", None,
                                  None, hlr_utils.program_version(), 'error',
                                  " ".join(description))

    # Set defaults for options
    parser.set_defaults(usmon_path="/entry/monitor1,1")
    parser.set_defaults(dsmon_path="/entry/monitor2,1")

    # Add dgs_reduction specific options
    parser.add_option("", "--timing", action="store_true", dest="timing",
                      help="Flag to turn on timing of code")
    parser.set_defaults(timing=False)

    (options, args) = parser.parse_args()

    # Set up the configuration
    configure = hlr_utils.Configure()

    # Call the configuration setter for DgsOptions
    hlr_utils.DgsConfiguration(parser, configure, options, args)

    # Set timer object if timing option is used
    if options.timing:
        import sns_timing
        timer = sns_timing.DiffTime()
    else:
        timer = None
    
    # Run the program
    run(configure, timer)
