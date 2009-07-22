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

def add_files(filelist, **kwargs):
    """
    This function takes a list of U{NeXus<www.nexusformat.org>} files and
    various keyword arguments and returns a data C{SOM} and a background C{SOM}
    (if requested) that is the sum of all the data from the specified files.
    B{It is assumed that the files contain similar data as only crude
    cross-checks will be made. You have been warned.}

    @param filelist: A list containing the names of the files to sum
    @type filelist: C{list}
    
    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword SO_Axis: This is the name of the main axis to read from the NeXus
                      file
    @type SO_Axis: C{string}
    
    @keyword Data_Paths: This contains the data paths and signals for the
                         requested detector banks
    @type Data_Paths: C{tuple} of C{tuple}s
    
    @keyword Signal_ROI: This is the name of a file that contains a list of
                         pixel IDs that will be read from the data file and
                         stored as a signal C{SOM}
    @type Signal_ROI: C{string}

    @keyword Signal_MASK: This is the name of a file that contains a list of
                         pixel IDs that will be read from the data file and
                         stored as a signal C{SOM}
    @type Signal_MASK: C{string}    
    
    @keyword dataset_type: The practical name of the dataset being processed.
                           The default value is I{data}.
    @type dataset_type: C{string}

    @keyword dst_type: The type of C{DST} to be created during file read-in.
                       The default value is I{application/x-NeXus}.
    @type dst_type: C{string}
    
    @keyword Verbose: This is a flag to turn on print statments. The default is
                      I{False}.
    @type Verbose: C{boolean}
    
    @keyword Timer: This is an SNS Timer object used for showing the
                    performance timing in the function.
    @type Timer: C{sns_timing.Timer}


    @return: Signal C{SOM.SOM} and background C{SOM.SOM}
    @rtype: C{tuple}

    
    @raise SystemExit: If any file cannot be read
    @raise RuntimeError: If both a ROI and MASK file are specified
    """
    import sys

    import common_lib
    import DST
    import hlr_utils
    
    # Parse keywords
    try:
        so_axis = kwargs["SO_Axis"]
    except KeyError:
        so_axis = "time_of_flight"
    
    try:
        data_paths = kwargs["Data_Paths"]
    except KeyError:
        data_paths = None

    try:
        signal_roi = kwargs["Signal_ROI"]
    except KeyError:
        signal_roi = None 

    try:
        signal_mask = kwargs["Signal_MASK"]
    except KeyError:
        signal_mask = None         

    try:
        dataset_type = kwargs["dataset_type"]
    except KeyError:
        dataset_type = "data"

    try:
        dst_type = kwargs["dst_type"]
    except KeyError:
        try:
            dst_type = hlr_utils.file_peeker(filelist[0])
        except RuntimeError:
            # Assume it is a NeXus file, since it is not a DR produced file
            dst_type = "application/x-NeXus"

    try:
        verbose = kwargs["Verbose"]
    except KeyError:
        verbose = False

    try:
        timer = kwargs["Timer"]
    except KeyError:
        timer = None

    if signal_roi is not None and signal_mask is not None:
        raise RuntimeError("Cannot specify both ROI and MASK file! Please "\
                           +"choose!")

    counter = 0

    for filename in filelist:
        if verbose:
            print "File:", filename
            
        try:
            if dst_type == "application/x-NeXus":
                data_dst = DST.getInstance(dst_type, filename)
            else:
                resource = open(filename, "r")
                data_dst = DST.getInstance(dst_type, resource) 
        except SystemError:
            print "ERROR: Failed to data read file %s" % filename
            sys.exit(-1)

        if verbose:
            print "Reading data file %d" % counter

        if counter == 0:
            if dst_type == "application/x-NeXus":
                d_som1 = data_dst.getSOM(data_paths, so_axis,
                                         roi_file=signal_roi,
                                         mask_file=signal_mask)
                d_som1.rekeyNxPars(dataset_type)
            else:
                if dst_type != "text/Dave2d":
                    d_som1 = data_dst.getSOM(data_paths, roi_file=signal_roi,
                                             mask_file=signal_mask)
                else:
                    d_som1 = data_dst.getSOM(data_paths)

            if verbose:
                print "# Signal SO:", len(d_som1)
                try:
                    dsize = len(d_som1[0])
                except IndexError:
                    # All data has been filtered
                    print "Information is unavailable since no data "\
                          +"present. Exiting."
                    sys.exit(0)

                if dst_type == "application/x-NeXus":
                    print "# TOF:", dsize
                    print "# TOF Axis:", len(d_som1[0].axis[0].val)
                elif dst_type != "text/num-info":
                    print "# Data Size:", dsize
                    print "# X-Axis:", len(d_som1[0].axis[0].val)
                    try:
                        axis_len = len(d_som1[0].axis[1].val)
                        print "# Y-Axis:", axis_len
                    except IndexError:
                        pass

            if timer is not None:
                timer.getTime(msg="After reading data")

        else:
            if dst_type == "application/x-NeXus":
                d_som_t = data_dst.getSOM(data_paths, so_axis,
                                          roi_file=signal_roi,
                                          mask_file=signal_mask)
                d_som_t.rekeyNxPars(dataset_type)
                add_nxpars_sig = True
            else:
                if dst_type != "text/Dave2d":
                    d_som_t = data_dst.getSOM(data_paths, roi_file=signal_roi,
                                              mask_file=signal_mask)
                else:
                    d_som_t = data_dst.getSOM(data_paths)
                add_nxpars_sig = False
                
            if timer is not None:
                timer.getTime(msg="After reading data")

            d_som1 = common_lib.add_ncerr(d_som_t, d_som1,
                                          add_nxpars=add_nxpars_sig)

            if timer is not None:
                timer.getTime(msg="After adding spectra")

            del d_som_t

            if timer is not None:
                timer.getTime(msg="After SOM deletion")

        data_dst.release_resource()
        del data_dst
        counter += 1

        if timer is not None:
            timer.getTime(msg="After resource release and DST deletion")

        if dst_type == "application/x-NeXus":
            som_key_parts = [dataset_type, "filename"]
            som_key = "-".join(som_key_parts)

            d_som1.attr_list[som_key] = filelist
        else:
            # Previously written files already have this structure imposed
            pass

    return d_som1

if __name__ == "__main__":

    my_files = []
    my_files.append("/SNS/REF_L/2006_2_4B_SCI/1/1845/NeXus/REF_L_1845.nxs")
    my_files.append("/SNS/REF_L/2006_2_4B_SCI/1/1848/NeXus/REF_L_1848.nxs")

    my_paths = ("/entry/bank1", 1)

    signal_roi_file = "../hlr_test/files/REF_L_1845_signal_Pid.txt"

    d_som = add_files(my_files, Data_Paths=my_paths,
                      Signal_ROI=signal_roi_file,
                      Verbose=True)

    print "Length Data:", len(d_som)
