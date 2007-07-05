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
    
    @keyword Bkg_ROI: This is the name of a file that contains a list of pixel
                      IDs that will be read from the data file and stored as a
                      background C{SOM}
    @type Bkg_ROI: C{string}
    
    @keyword dataset_type: The practical name of the dataset being processed.
                           The default value is I{data}.
    @type dataset_type: C{string}
    
    @keyword Verbose: This is a flag to turn on print statments. The default is
                      I{False}.
    @type Verbose: C{boolean}
    
    @keyword Timer: This is an SNS Timer object used for showing the
                    performance timing in the function.
    @type Timer: C{sns_timing.Timer}


    @return: Signal C{SOM.SOM} and background C{SOM.SOM}
    @rtype: C{tuple}

    
    @raise SystemExit: If any file cannot be read
    """
    import sys

    import common_lib
    import DST

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
        bkg_roi = kwargs["Bkg_ROI"]
    except KeyError:
        bkg_roi = None        

    try:
        dataset_type = kwargs["dataset_type"]
    except KeyError:
        dataset_type = "data"

    try:
        verbose = kwargs["Verbose"]
    except KeyError:
        verbose = False

    try:
        timer = kwargs["Timer"]
    except KeyError:
        timer = None

    counter = 0

    for filename in filelist:
        if verbose:
            print "File:",filename
            
        try:
            data_dst = DST.getInstance("application/x-NeXus", filename) 
        except SystemError:
            print "ERROR: Failed to data read file %s" % filename
            sys.exit(-1)

        if verbose:
            print "Reading data file %d" % counter

        if counter == 0:
            d_som1 = data_dst.getSOM(data_paths, so_axis,
                                     roi_file=signal_roi)
            d_som1.rekeyNxPars(dataset_type)

            if verbose:
                print "# Signal SO:",len(d_som1)
                print "# TOF:",len(d_som1[0])

            if bkg_roi is not None:
                b_som1 = data_dst.getSOM(data_paths, so_axis,
                                         roi_file=bkg_roi)
                b_som1.rekeyNxPars(dataset_type)
                
                if verbose:
                    print "# Background SO:",len(b_som1)

            else:
                b_som1 = None

            if timer is not None:
                timer.getTime(msg="After reading data")

        else:
            d_som_t = data_dst.getSOM(data_paths, so_axis,
                                      roi_file=signal_roi)
            d_som_t.rekeyNxPars(dataset_type)

            if bkg_roi is not None:
                b_som_t = data_dst.getSOM(data_paths, so_axis,
                                          roi_file=bkg_roi)
                b_som_t.rekeyNxPars(dataset_type)
            else:
                b_som_t = None
            if timer is not None:
                timer.getTime(msg="After reading data")

            d_som1 = common_lib.add_ncerr(d_som_t, d_som1, add_nxpars=True)
            if bkg_roi is not None:
                b_som1 = common_lib.add_ncerr(b_som_t, b_som1, add_nxpars=True)

            if timer is not None:
                timer.getTime(msg="After adding spectra")

            del d_som_t
            if bkg_roi is not None:
                del b_som_t

            if timer is not None:
                timer.getTime(msg="After SOM deletion")

        data_dst.release_resource()
        del data_dst
        counter += 1

        if timer is not None:
            timer.getTime(msg="After resource release and DST deletion")

        som_key_parts = [dataset_type, "filename"]
        som_key = "-".join(som_key_parts)

        d_som1.attr_list[som_key] = filelist
        if b_som1 is not None:
            b_som1.attr_list[som_key] = filelist

    return (d_som1, b_som1)

if __name__ == "__main__":

    my_files = []
    my_files.append("/SNS/REF_L/2006_2_4B_SCI/1/1845/NeXus/REF_L_1845.nxs")
    my_files.append("/SNS/REF_L/2006_2_4B_SCI/1/1848/NeXus/REF_L_1848.nxs")

    my_paths = ("/entry/bank1", 1)

    signal_roi_file = "../../hlr_test/files/REF_L_1845_signal_Pid.txt"
    bkg_roi_file = "../../hlr_test/files/REF_L_1845_background_Pid.txt"

    (d_som, b_som) = add_files(my_files, Data_Paths=my_paths,
                               Signal_ROI=signal_roi_file,
                               Bkg_ROI=bkg_roi_file, Verbose=True)

    print "Length Data:", len(d_som)
    if b_som is not None:
        print "Length Background:", len(b_som)
