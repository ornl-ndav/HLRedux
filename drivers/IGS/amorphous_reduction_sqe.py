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
This program covers the functionality outlined in B{Section 2.2.1 Powder or
amorphous material reduction} in
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
    import common_lib
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

    # Perform early background subtraction if the hwfix flag is used
    if config.hwfix:
        if not config.mc:
            so_axis = "time_of_flight"
        else:
            so_axis = "Time_of_Flight"
        
        bkg_som0 = dr_lib.add_files(config.back,
                                    Data_Paths=config.data_paths.toPath(),
                                    SO_Axis=so_axis,
                                    Signal_ROI=config.roi_file,
                                    dataset_type="background",
                                    Verbose=config.verbose, Timer=tim)[0]

        bkg_som = dr_lib.fix_bin_contents(bkg_som0)
        del bkg_som0
    else:
        bkg_som = None

    # Perform Steps 1-9 on sample data
    d_som1 = dr_lib.process_igs_data(config.data, config, timer=tim,
                                     inst_geom_dst=inst_geom_dst,
                                     tib_const=config.tib_data_const,
                                     bkg_som=bkg_som)

    # Perform Steps 1-9 on empty can data
    if config.ecan is not None:
        e_som1 = dr_lib.process_igs_data(config.ecan, config, timer=tim,
                                         inst_geom_dst=inst_geom_dst,
                                         dataset_type="empty_can",
                                         tib_const=config.tib_ecan_const,
                                         bkg_som=bkg_som)
    else:
        e_som1 = None

    # Perform Steps 1-9 on normalization data            
    if config.norm is not None:
        n_som1 = dr_lib.process_igs_data(config.norm, config, timer=tim,
                                         inst_geom_dst=inst_geom_dst,
                                         dataset_type="normalization",
                                         tib_const=config.tib_norm_const,
                                         bkg_som=bkg_som)
    else:
        n_som1 = None

    # Perform Steps 1-9 on background data
    if config.back is not None:
        b_som1 = dr_lib.process_igs_data(config.back, config, timer=tim,
                                         inst_geom_dst=inst_geom_dst,
                                         dataset_type="background",
                                         tib_const=config.tib_back_const,
                                         bkg_som=bkg_som)
    else:
        b_som1 = None

    # Perform Step 1-9 on direct scattering background data
    if config.dsback is not None:
        ds_som1 = dr_lib.process_igs_data(config.dsback, config, timer=tim,
                                          inst_geom_dst=inst_geom_dst,
                                          tib_const=config.tib_dsback_const,
                                          dataset_type="dsbackground",
                                          bkg_som=bkg_som)

        # Note: time_zero_slope MUST be a tuple
        if config.time_zero_slope is not None:
            ds_som1.attr_list["Time_zero_slope"] = \
                                      config.time_zero_slope.toValErrTuple()

        # Note: time_zero_offset MUST be a tuple
        if config.time_zero_offset is not None:
            ds_som1.attr_list["Time_zero_offset"] = \
                                      config.time_zero_offset.toValErrTuple()
        
        # Step 10: Linearly interpolate TOF elastic range in direct scattering
        #          background data

        # First convert TOF elastic range to appropriate pixel initial
        # wavelengths
        if config.verbose:
            print "Determining initial wavelength range for elastic line"

        if tim is not None:
            tim.getTime(False)
        
        if config.tof_elastic is None:
            # Units are in microseconds
            tof_elastic_range = (140300, 141300)
        else:
            tof_elastic_range = config.tof_elastic
        
        ctof_elastic_low = dr_lib.convert_single_to_list(\
               "tof_to_initial_wavelength_igs_lin_time_zero",
               (tof_elastic_range[0], 0.0),
               ds_som1)
        
        ctof_elastic_high = dr_lib.convert_single_to_list(\
               "tof_to_initial_wavelength_igs_lin_time_zero",
               (tof_elastic_range[1], 0.0),
               ds_som1)
        
        ctof_elastic_range = [(ctof_elastic_low[i][0], ctof_elastic_high[i][0])
                              for i in xrange(len(ctof_elastic_low))]

        if tim is not None:
            tim.getTime(msg="After calculating initial wavelength range for "\
                        +"elastic line ")

        del ctof_elastic_low, ctof_elastic_high

        if config.split:
            lambda_filter = [(d_som1[i].axis[0].val[0],
                              d_som1[i].axis[0].val[-1])
                             for i in xrange(len(d_som1))]
        else:
            lambda_filter = None

        # Now interpolate spectra between TOF elastic range (converted to
        # initial wavelength)
        if config.verbose:
            print "Linearly interpolating direct scattering spectra"

        if tim is not None:
            tim.getTime(False)
            
        ds_som2 = dr_lib.lin_interpolate_spectra(ds_som1, ctof_elastic_range,
                                                 filter=lambda_filter)

        if tim is not None:
            tim.getTime(msg="After linearly interpolating direct scattering "\
                        +"spectra ")

        if config.dump_dslin:
            ds_som2_1 = dr_lib.sum_all_spectra(ds_som2,\
                                  rebin_axis=config.lambda_bins.toNessiList())

            hlr_utils.write_file(config.output, "text/Spec", ds_som2_1,
                                 output_ext="lin",
                                 data_ext=config.ext_replacement,    
                                 path_replacement=config.path_replacement,
                                 verbose=config.verbose,
                                 message="dsbackground linear interpolation")
            del ds_som2_1
        
        del ds_som1
    else:
        ds_som2 = None

    if inst_geom_dst is not None:
        inst_geom_dst.release_resource()

    # Steps 11-12: Subtract background spectrum from sample spectrum
    if config.dsback is None:
        back_som = b_som1
        bkg_type = "background"
    else:
        back_som = ds_som2
        bkg_type = "dsbackground"
    d_som2 = dr_lib.subtract_bkg_from_data(d_som1, back_som,
                                           verbose=config.verbose,
                                           timer=tim,
                                           dataset1="data",
                                           dataset2=bkg_type,
                                           scale=config.scale_bs)

    if config.dsback is not None:
        del ds_som2 

    # Step 13: Zero region outside TOF elastic for background for empty can
    if config.dsback is None:
        bcs_som = b_som1
        cs_som = e_som1
    else:
        if config.verbose and b_som1 is not None:
            print "Zeroing background spectra"

        if tim is not None and b_som1 is not None:
            tim.getTime(False)
            
        bcs_som = dr_lib.zero_spectra(b_som1, ctof_elastic_range)

        if tim is not None and b_som1 is not None:
            tim.getTime(msg="After zeroing background spectra")


        if config.verbose and e_som1 is not None:
            print "Zeroing empty can spectra"

        if tim is not None and e_som1 is not None:
            tim.getTime(False)
            
        cs_som = dr_lib.zero_spectra(e_som1, ctof_elastic_range)

        if tim is not None and e_som1 is not None:
            tim.getTime(msg="After zeroing empty can spectra")
            
        del ctof_elastic_range

    # Steps 14-15: Subtract background spectrum from empty can spectrum    
    e_som2 = dr_lib.subtract_bkg_from_data(cs_som, bcs_som,
                                           verbose=config.verbose,
                                           timer=tim,
                                           dataset1="empty_can",
                                           dataset2="background",
                                           scale=config.scale_bcs)

    # Steps 16-17: Subtract background spectrum from empty can spectrum for
    #              normalization
    e_som3 = dr_lib.subtract_bkg_from_data(e_som1, b_som1,
                                           verbose=config.verbose,
                                           timer=tim,
                                           dataset1="empty_can",
                                           dataset2="background",
                                           scale=config.scale_bcn)

    # Steps 18-19: Subtract background spectrum from normalization spectrum

    try:
        config.pre_norm
    except AttributeError:
        config.pre_norm = False
    
    if not config.pre_norm:
        n_som2 = dr_lib.subtract_bkg_from_data(n_som1, b_som1,
                                               verbose=config.verbose,
                                               timer=tim,
                                               dataset1="normalization",
                                               dataset2="background",
                                               scale=config.scale_bn)
    else:
        n_som2 = n_som1

    del b_som1, e_som1, bcs_som, cs_som

    # Steps 20-21: Subtract empty can spectrum from sample spectrum    
    d_som3 = dr_lib.subtract_bkg_from_data(d_som2, e_som2,
                                           verbose=config.verbose,
                                           timer=tim,
                                           dataset1="data",
                                           dataset2="empty_can",
                                           scale=config.scale_cs)

    del d_som2, e_som2
    
    # Steps 22-23: Subtract empty can spectrum from normalization spectrum
    if not config.pre_norm:
        n_som3 = dr_lib.subtract_bkg_from_data(n_som2, e_som3,
                                               verbose=config.verbose,
                                               timer=tim,
                                               dataset1="normalization",
                                               dataset2="empty_can",
                                               scale=config.scale_cn)
    else:
        n_som3 = n_som2

    del n_som2, e_som3

    # Step 24-25: Integrate normalization spectra
    if config.verbose and n_som3 is not None and not config.pre_norm:
        print "Integrating normalization spectra"

    if not config.pre_norm:
        norm_int = dr_lib.integrate_spectra(n_som3, start=config.norm_start,
                                            end=config.norm_end, norm=True)
    else:
        norm_int = n_som3

    del n_som3
        
    # Step 26: Normalize data by integrated values
    if config.verbose and norm_int is not None:
        print "Normalizing data by normalization data"

    if norm_int is not None:
        d_som4 = common_lib.div_ncerr(d_som3, norm_int)
    else:
        d_som4 = d_som3

    if norm_int is not None:
        if tim is not None:
            tim.getTime(msg="After normalizing data ")

    del d_som3, norm_int

    # Steps 27 to end: Creating S(Q,E)
    if config.verbose:
        print "Creating 2D spectrum"

    if tim is not None:
        tim.getTime(False)
        
    d_som5 = dr_lib.create_E_vs_Q_igs(d_som4,
                                      config.E_bins.toNessiList(),
                                      config.Q_bins.toNessiList(),
                                      so_id="Full Detector",
                                      y_label="counts",
                                      y_units="counts / (ueV * A^-1)",
                                      x_labels=["Q transfer",
                                                "energy transfer"],
                                      x_units=["1/Angstroms","ueV"],
                                      split=config.split,
                                      configure=config)
    
    if tim is not None:
        tim.getTime(msg="After creation of final spectrum ")

    del d_som4

    # If rescaling factor present, rescale the data
    if config.rescale_final is not None and not config.split:
        d_som6 = common_lib.mult_ncerr(d_som5, (config.rescale_final, 0.0))
    else:
        d_som6 = d_som5

    if not __name__ == "amorphous_reduction_sqe":

        del d_som5

        # Writing 2D DAVE file
        if not config.split:
            hlr_utils.write_file(config.output, "text/Dave2d", d_som6,
                                 verbose=config.verbose,
                                 message="data",
                                 replace_path=False,
                                 replace_ext=False)
        
        d_som6.attr_list["config"] = config

        hlr_utils.write_file(config.output, "text/rmd", d_som6,
                             output_ext="rmd",
                             data_ext=config.ext_replacement,         
                             path_replacement=config.path_replacement,
                             verbose=config.verbose,
                             message="metadata")
    
        if tim is not None:
            tim.setOldTime(old_time)
            tim.getTime(msg="Total Running Time")

    else:
        return d_som6
    
if __name__ == "__main__":
    import hlr_utils

    # Make description for driver
    result = []
    result.append("This driver runs the data reduction for the inelastic")
    result.append("banks for the BSS instrument. The standard output is a")
    result.append("*.txt file (DAVE Grouped ASCII) for S(Q,E). Other")
    result.append("intermediate files can be produced by using the ")
    result.append("appropriate dump-X flag described in this help. The file")
    result.append("extensions are described in the option documentation.")
 
    # Set up the options available
    parser = hlr_utils.AmrOptions("usage: %prog [options] <datafile>", None,
                                  hlr_utils.program_version(), 'error',
                                  " ".join(result))

    # Set defaults for imported options
    parser.set_defaults(inst="BSS")
    parser.set_defaults(data_paths="/entry/bank1,1,/entry/bank2,1")
    parser.set_defaults(mon_path="/entry/monitor,1")
    parser.set_defaults(norm_start="6.24")
    parser.set_defaults(norm_end="6.30")
    
    # Add amorphous_reduction specific options
    parser.add_option("", "--timing", action="store_true", dest="timing",
                      help="Flag to turn on timing of code")
    parser.set_defaults(timing=False)
    
    (options, args) = parser.parse_args()

    # Set up the configuration
    configure = hlr_utils.Configure()

    # Call the configuration setter for AmrOptions
    hlr_utils.AmrConfiguration(parser, configure, options, args)

    # Set timer object if timing option is used
    if options.timing:
        import sns_timing
        timer = sns_timing.DiffTime()
    else:
        timer = None
    
    # Run the program
    run(configure, timer)
