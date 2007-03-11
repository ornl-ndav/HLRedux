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

def determine_time_indep_bkg(obj, tof_vals, **kwargs):
    """
    This functions calculates the average counts at four given TOF channels
    for determining the time-independent background. The incoming object must
    be a SOM or a SO.

    Parameters:
    ----------
    -> obj is a SOM used for determining the time-independent background
    -> tof_vals is the four TOF channels from which the average counts will
       be determined

    Returns:
    -------
    <- A list of tuples containing the time-independent background and the
       associated error 
    """

    # import the helper functions
    import hlr_utils

    o_descr = hlr_utils.get_descr(obj)

    if o_descr != "SOM" or o_descr != "SO":
        raise TypeError("Incoming object must be a SOM or a SO")
    # Have a SOM or SO
    else:
        pass
    
    # set up for working through data
    # This time highest object in the hierarchy is NOT what we need
    result = []
    if(hlr_utils.get_length(obj) > 1):
        res_descr = "list"
    else:
        res_descr = "number"
    


if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som()

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]

    print "********** determine_time_indep_bkg"
    print "* ", determine_time_indep_bkg(som1)
    
