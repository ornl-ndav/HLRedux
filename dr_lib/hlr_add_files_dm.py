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

def add_files_dm(filelist, **kwargs):
    """
    This function takes a list of U{NeXus<www.nexusformat.org>} files and
    various keyword arguments and returns a data C{SOM} and a monitor C{SOM}
    that is the sum of all the data from the specified files. B{It is assumed
    that the files contain similar data as only crude cross-checks will be
    made. You have been warned.}

    @param filelist: A list containing the names of the files to sum
    @type filelist: C{list}
    
    @param kwargs: A list of keyword arguments that the function accepts:
    
    @keyword SO_Axis: This is the name of the main axis to read from the NeXus
                      file
    @type SO_Axis: C{string}
    
    @keyword Data_Paths: This contains the data paths and signals for the
                         requested detector banks
    @type Data_Paths: C{tuple} of C{tuple}s

    @keyword Mon_Paths: This contains the data paths and signals for the
                        requested monitor banks
    @type Mon_Paths: C{tuple} of C{tuple}s    
    
    @keyword Signal_ROI: This is the name of a file that contains a list of
                         pixel IDs that will be read from the data file and
                         stored as a signal C{SOM}
    @type Signal_ROI: C{string}
    
    @keyword dataset_type: The practical name of the dataset being processed.
                           The default value is I{data}.
    @type dataset_type: C{string}

    @keyword Verbose: This is a flag to turn on print statments. The default is
                      I{False}.
    @type Verbose: C{boolean}
    
    @keyword Timer: This is an SNS Timer object used for showing the
                    performance timing in the function.
    @type Timer: C{sns_timing.Timer}


    @return: Signal C{SOM.SOM} and monitor C{SOM.SOM}
    @rtype: C{tuple}

    
    @raise SystemExit: If any file cannot be read
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
        mon_paths = kwargs["Mon_Paths"]
    except KeyError:
        mon_paths = None        

    try:
        signal_roi = kwargs["Signal_ROI"]
    except KeyError:
        signal_roi = None 

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

    dst_type == "application/x-NeXus"
    counter = 0

    for filename in filelist:
        if verbose:
            print "File:", filename
            
        try:
            data_dst = DST.getInstance(dst_type, filename)
        except SystemError:
            print "ERROR: Failed to data read file %s" % filename
            sys.exit(-1)

        if verbose:
            print "Reading data file %d" % counter

        if counter == 0:
            d_som1 = data_dst.getSOM(data_paths, so_axis, roi_file=signal_roi)
            d_som1.rekeyNxPars(dataset_type)

            if verbose:
                print "# Signal SO:", len(d_som1)
                print "# TOF:", len(d_som1[0])
                print "# TOF Axis:", len(d_som1[0].axis[0].val)

            if timer is not None:
                timer.getTime(msg="After reading data")

        if verbose:
            print "Reading monitor %d" % counter

        if counter == 0:
            m_som1 = data_dst.getSOM(mon_paths, so_axis)
            m_som1.rekeyNxPars(dataset_type)

            if verbose and m_som1 is not None:
                print "# Monitor SO:", len(m_som1)
                print "# TOF:", len(m_som1[0])
                print "# TOF Axis:", len(m_som1[0].axis[0].val)

            if timer is not None:
                timer.getTime(msg="After reading monitor data")

        else:
            d_som_t = data_dst.getSOM(data_paths, so_axis, roi_file=signal_roi)
            d_som_t.rekeyNxPars(dataset_type)
            
            if timer is not None:
                timer.getTime(msg="After reading data")

            m_som_t = data_dst.getSOM(mon_paths, so_axis)
            m_som_t.rekeyNxPars(dataset_type)
            
            if timer is not None:
                timer.getTime(msg="After reading monitor data")

            d_som1 = common_lib.add_ncerr(d_som_t, d_som1, add_nxpars=True)

            if timer is not None:
                timer.getTime(msg="After adding data spectra")

            del d_som_t

            if timer is not None:
                timer.getTime(msg="After data SOM deletion")
                
            m_som1 = common_lib.add_ncerr(m_som_t, m_som1, add_nxpars=True)

            if timer is not None:
                timer.getTime(msg="After adding monitor spectra")

            del m_som_t            

            if timer is not None:
                timer.getTime(msg="After monitor SOM deletion")
                
        data_dst.release_resource()
        del data_dst
        counter += 1

        if timer is not None:
            timer.getTime(msg="After resource release and DST deletion")

        som_key_parts = [dataset_type, "filename"]
        som_key = "-".join(som_key_parts)
        
        d_som1.attr_list[som_key] = filelist
        if m_som1 is not None:
            m_som1.attr_list[som_key] = filelist

    return (d_som1, m_som1)
    
