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

def determine_ref_background(obj, no_bkg=False, **kwargs):
    """
    This function takes in a collection of pixels that have been selected as
    the reflectometer background. The pixels are summed into a single spectrum
    and then scaled by the total number of pixels present in the selection.

    @param obj: Object containing reflectometer background information
    @type obj: C{SOM.SOM}
    
    @param no_bkg: (OPTIONAL) Flag which determines if the background will be
                              calculated
    @type no_bkg: C{boolean}
    
    
    @return: A length object containing a summed background spectrum scaled by
             the total number of background pixels
    @rtype: C{SOM.SOM}
    """
    import dr_lib
    import common_lib
    import hlr_utils

    # If user does not desire background subtraction or incoming SOM is None,
    # return None
    if no_bkg or obj is None:
        return None

    # set up for working through data
    o_descr = hlr_utils.get_descr(obj)

    if o_descr != "SOM":
        raise RuntimeError("Must provide a SOM to the function.")
    # Go on
    else:
        pass

    # Combine all background spectra into one
    obj1 = dr_lib.sum_all_spectra(obj)

    # Determine scaling ratio
    ratio = (1.0 / float(len(obj)), 0.0)

    # Scale background spectrum by ratio
    return common_lib.mult_ncerr(obj1, ratio)

if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som()

    print "********** SOM1"
    print "* ", som1

    print "********** determine_ref_background"
    print "* som :", determine_ref_background(som1)
