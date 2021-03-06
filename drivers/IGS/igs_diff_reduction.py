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
This driver was a request from the B{BASIS} (aka B{BSS}) team and is not
formally documented.
"""

def convert_data_to_d_spacing(data_som):

    data_som1 = common_lib.tof_to_wavelength(data_som, inst_param="total",
                                             units="microsecond")
    
    return common_lib.wavelength_to_d_spacing(data_som1)

def convert_data_to_tof_focused_det(conf, data_som):

    return common_lib.d_spacing_to_tof_focused_det(data_som,
                                                   pixel_id=conf.pixel_id,
                                                   verbose=True)


def convert_data_to_scalar_Q(config, data_som):

    data_som1 = common_lib.tof_to_wavelength(data_som, inst_param="total",
                                             units="microsecond")

    return common_lib.wavelength_to_scalar_Q(data_som1)

    
def run(config):
    import sys

    import DST
    
    if config.data is None:
        raise RuntimeError("Need to pass a data filename to the driver "\
                           +"script.")

    try:
        data_dst = DST.getInstance("application/x-NeXus", config.data)
    except SystemError:
        print "ERROR: Failed to data read file %s" % config.data
        sys.exit(-1)

    so_axis = "time_of_flight"

    if config.Q_bins is not None:
        rmd_written = False
    else:
        rmd_written = True

    if config.verbose:
        print "Reading data file"

    d_som1 = data_dst.getSOM(config.data_paths, so_axis)

    if config.det_geom is not None:
        if config.verbose:
            print "Reading in detector geometry file"
            
        det_geom_dst = DST.getInstance("application/x-NxsGeom",
                                       config.det_geom)
        det_geom_dst.setGeometry(config.data_paths, d_som1)
        det_geom_dst.release_resource()

    if config.d_bins is not None:

        if config.verbose:
            print "Converting TOF to d-spacing"

        d_som2 = convert_data_to_d_spacing(d_som1)

        if config.dump_pxl:
            hlr_utils.write_file(config.data, "text/Spec", d_som2,
                                 output_ext="dsp", verbose=config.verbose,
                                 message="pixel d-spacing information")

        d_som3 = common_lib.rebin_axis_1D(d_som2, config.d_bins)
    
        d_som4 = dr_lib.sum_all_spectra(d_som3)
        
        d_som4[0].id = ("bank3", (0, 0))

        hlr_utils.write_file(config.output_ds, "text/Spec", d_som4,
                             replace_ext=False, verbose=config.verbose,
                             message="combined d-spacing information")

        if config.verbose:
            print "Converting d-spacing to TOF focused detector"

        d_som5 = convert_data_to_tof_focused_det(config, d_som2)

        if config.dump_pxl:
            hlr_utils.write_file(config.data, "text/Spec", d_som5,
                                 output_ext="tfp", verbose=config.verbose,
                                 message="pixel TOF focused information")

        d_som6 = common_lib.rebin_axis_1D(d_som5, config.tof_bins)

        d_som7 = dr_lib.sum_all_spectra(d_som6)

        d_som7[0].id = config.pixel_id

        hlr_utils.write_file(config.output_tof, "text/GSAS", d_som7,
                             replace_ext=False, verbose=config.verbose,
                             message="combined TOF focused information")

        hlr_utils.write_file(config.data, "text/Spec", d_som7,
                             output_ext="toff",
                             verbose=config.verbose,
                             message="combined TOF focused information")

        d_som7.attr_list["config"] = config

        if rmd_written:
            hlr_utils.write_file(config.data, "text/rmd", d_som7,
                                 output_ext="rmd", verbose=config.verbose,
                                 message="metadata")
        
    else:
        pass

    if config.Q_bins is not None:
        if config.verbose:
            print "Converting TOF to Q"

        d_som2 = convert_data_to_scalar_Q(config, d_som1)
    
        if config.dump_pxl:
            hlr_utils.write_file(config.data, "text/Spec", d_som2,
                                 output_ext="qtp", verbose=config.verbose,
                                 message="pixel Q information")
        
        d_som3 = common_lib.rebin_axis_1D(d_som2, config.Q_bins)
    
        d_som4 = dr_lib.sum_all_spectra(d_som3)
        
        d_som4[0].id = ("bank3", (0, 0))

        hlr_utils.write_file(config.output_qt, "text/Spec", d_som4,
                             replace_ext=False, verbose=config.verbose,
                             message="combined Q information")

        hlr_utils.write_file(config.data, "text/rmd", d_som7,
                             output_ext="rmd", verbose=config.verbose,
                             message="metadata")
    else:
        pass

if __name__ == "__main__":
    import os
    
    import common_lib
    import dr_lib
    import hlr_utils

    # set up the options available
    parser = hlr_utils.BasicOptions("usage: %prog [options] <datafile>", None,
                                    None, hlr_utils.program_version())

    parser.add_option("", "--d-bins", dest="d_bins",
                      help="Specify the minimum and maximum d-spacing values"\
                      +" and the d-spacing bin width in Angstroms")
    parser.set_defaults(d_bins="0,6,0.01")
    
    parser.add_option("", "--data-paths", dest="data_paths",
                      help="Specify the comma separated list of detector data"\
                      +" paths and signals. Default is /entry-diff/bank3,1")
    parser.set_defaults(data_paths="/entry-diff/bank3,1")
    
    parser.add_option("", "--dump-pxl", action="store_true", dest="dump_pxl",
                      help="Flag to dump the d-spacing for all pixels")
    parser.set_defaults(dump_pxl=False)

    parser.add_option("", "--mom-trans-bins", dest="Q_bins",
                      help="Specify the minimum and maximum momentum transfer"\
                      +" values and the momentum transfer bin width in"\
                      +" Angstroms^-1")

    parser.add_option("", "--tof-bins", dest="tof_bins",
                      help="Specify the minimum and maximum TOF values"\
                      +" and the TOF bin width in microseconds. Default is 0,"\
                      +"200000,100")
    parser.set_defaults(tof_bins="0,200000,100")

    parser.add_option("", "--pixel-id", dest="pixel_id",
                      help="Specify the pixel ID for time focussing in a "\
                      +"comma-delimited list. Default is bank3,3,63")
    parser.set_defaults(pixel_id="bank3,3,63")

    parser.add_option("", "--det-geom", dest="det_geom",
                      help="Specify the detector geometry file")


    (options, args) = parser.parse_args()
   
    # set up the configuration
    configure = hlr_utils.Configure()
    
    # get the datafile name and check it
    if len(args) == 1:
        configure.data = args[0]
        if not hlr_utils.file_exists(configure.data):
            parser.error("Data file [%s] does not exist" % configure.data)
    else:
        if options.data is not None:
            configure.data = hlr_utils.fix_filename(options.data)
            if not hlr_utils.file_exists(configure.data):
                parser.error("Data file [%s] does not exist" % configure.data)
        else:
            parser.error("Did not specify a datafile")
    # create the output file name if there isn't one supplied
    if options.output:
        configure.output = hlr_utils.fix_filename(options.output)
        print "Using %s as output file" % configure.output
    else:
        configure.output = None
        outfile = os.path.basename(configure.data)
        path = os.path.join(os.getcwd(), outfile)
        if options.d_bins is not None:
            configure.output_ds = hlr_utils.ext_replace(path, "nxs", "ds1")
            print "Using %s as output file" % configure.output_ds
        else:
            configure.output_ds = None

        if options.tof_bins is not None:
            configure.output_tof = hlr_utils.ext_replace(path, "nxs", "gs")
            print "Using %s as output file" % configure.output_tof
        else:
            configure.output_tof = None            
            
        if options.Q_bins is not None:
            configure.output_qt = hlr_utils.ext_replace(path, "nxs", "qt1")
            print "Using %s as output file" % configure.output_qt
        else:
            configure.output_qt = None

    configure.det_geom = hlr_utils.fix_filename(options.det_geom)
    if configure.det_geom is not None:
        if not hlr_utils.file_exists(configure.det_geom):
            parser.error("Detector geometry file [%s] does not exist" \
                         % configure.det_geom)
            
    if options.d_bins is None and options.Q_bins is None:
        parser.error("Must specify at least one type of binning")
    else:
        pass

    # set the verbosity
    configure.verbose = options.verbose

    # set the data paths
    configure.data_paths = hlr_utils.create_data_paths(options.data_paths)

    # set the d bins
    if options.d_bins is not None:
        dfacts = options.d_bins.split(',')
        configure.d_bins = hlr_utils.make_axis(float(dfacts[0]),
                                               float(dfacts[1]),
                                               float(dfacts[2]))
    else:
        configure.d_bins = options.d_bins

    # set the Q bins
    if options.Q_bins is not None:
        qfacts = options.Q_bins.split(',')
        configure.Q_bins = hlr_utils.make_axis(float(qfacts[0]),
                                               float(qfacts[1]),
                                               float(qfacts[2]))
    else:
        configure.Q_bins = options.Q_bins

    # set the tof bins
    if options.tof_bins is not None:
        tfacts = options.tof_bins.split(',')
        configure.tof_bins = hlr_utils.make_axis(float(tfacts[0]),
                                                 float(tfacts[1]),
                                                 float(tfacts[2]))
    else:
        configure.tof_bins = options.tof_bins

    configure.pixel_id = hlr_utils.create_pixel_id(options.pixel_id)

    # set the ability to dump the d-spacing information
    configure.dump_pxl = options.dump_pxl

    run(configure)
