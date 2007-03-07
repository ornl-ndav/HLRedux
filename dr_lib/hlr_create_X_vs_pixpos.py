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

import hlr_utils
import SOM

def create_X_vs_pixpos(som, *args, **kwargs):
    """
    This function takes a SOM of single spectrum with any given axes
    (wavelength, energy etc.) and rebins those axes to the given axis and
    converts the spectra into a single I(X, pixel) spectrum.

    Parameters:
    ----------
    -> som is the input SOM with arbitrary (but same) axis SOs
    -> *args is a mandatory list of axes for rebinning.  There is a particular
       order to them. They should be present in the following order:
       Without errors
       1. Axis
       With errors
       1. Axis
       2. Axis error^2
       
    -> **kwargs is a dictionary of optional keywords that pass information to
       the function. Here are the currently accepted keywords:
       - withXVar=<string>. The string will either be True or False. If the
                  keyword is not present, the default value will be False
       - data_type=<string> The string can be either histogram, density or
                   coordinate. If the keyword is not present, the default
                   value will be histogram
       - so_id=<identifier> The identifier represents a number, string, tuple
               or other object that describes the resulting SO
       - y_label=<string> This is a string that sets the y axis label
       - y_units=<string> This is a string that sets the y axis units
       - x_labels=<list of strings> This is a list of strings that sets the
                  individual x axes labels
       - x_units=<list of string> This is a list of strings that sets the
                 individual x axes units
       - rebin=<boolean> Flag for turning rebin on or off. Default is True

    Returns:
    -------
    <- A SOM with a single 2D SO with the given axis and global pixel position

    Exceptions:
    ----------
    <- RuntimeError is raised if the parameter given to the keyword argument
       withXVar is not True or False
    <- RuntimeError is raised if the parameter given to the keyword argument
       data_type is not histogram or density or coordinate
    <- RuntimeError is raised is the number of given arguments (x-axes) is not
       either 2 (no errors) or 4 (with errors)
    """

    import common_lib
    import nessi_list

    # Setup some variables 
    dim = 2
    N_y = []
    N_tot = 1
    N_args = len(args)

    # Check withXVar keyword argument and also check number of given args.
    # Set xvar to the appropriate value
    try:
        value = kwargs["withXVar"]
        if value.lower() == "true":
            if N_args != 2:
                raise RuntimeError("Since you have requested x errors, 2 x "\
                                   +"axes must be provided.")
            else:
                xvar = True
                Q_pos = 2
        elif value.lower() == "false":
            if N_args != 2:
                raise RuntimeError("Since you did not requested x errors, 2 "\
                                   +"x axes must be provided.")
            else:
                xvar = False
        else:
            raise RuntimeError("Do not understand given parameter %s" % \
                               value)
    except KeyError:
        if N_args != 1:
            raise RuntimeError("Since you did not requested x errors, 1 "\
                               +"x axes must be provided.")
        else:
            xvar = False

    # Check dataType keyword argument. An offset will be set to 1 for the
    # histogram type and 0 for either density or coordinate
    try:
        data_type = kwargs["data_type"]
        if data_type.lower() == "histogram":
            offset = 1
        elif data_type.lower() == "density" or \
                 data_type.lower() == "coordinate":
            offset = 0
        else:
            raise RuntimeError("Do not understand data type given: %s" % \
                               data_type)
    # Default is offset for histogram
    except KeyError:
        offset = 1

    so_dim = SOM.SO(dim)

    arb_axis = 1
    pixel_axis = 0

    # Set the x-axis arguments from the *args list into the new SO
    if not xvar:
        so_dim.axis[arb_axis].val = args[0]
    else:
        so_dim.axis[arb_axis].val = args[0]
        so_dim.axis[arb_axis].var = args[1]

    # Set individual value axis sizes (not x-axis size)
    N_y.append(len(args[0]) - offset)

    # Calculate total 2D array size
    N_som = len(som)
    N_tot = N_som * N_y[-1]

    # Make second axis on total number of pixels
    so_dim.axis[pixel_axis].val = hlr_utils.make_axis(0, N_som, 1)
    if xvar:
        so_dim.axis[pixel_axis].var = nessi_list.NessiList(N_som+1)

    # Create y and var_y lists from total 2D size
    so_dim.y = nessi_list.NessiList(N_tot)
    so_dim.var_y = nessi_list.NessiList(N_tot)

    # Check for rebinning
    try:
        rebin = kwargs["rebin"]
    except KeyError:
        rebin = True

    # Rebin data to X axis
    if rebin:
        som_1 = common_lib.rebin_axis_1D(som, args[0])
    else:
        som_1 = som

    del som

    import array_manip
    
    for i in xrange(hlr_utils.get_length(som_1)):

        val = hlr_utils.get_value(som_1, i, "SOM", "y")
        err2 = hlr_utils.get_err2(som_1, i, "SOM", "y")

        start = i * N_y[0]

        (so_dim.y, so_dim.var_y) = array_manip.add_ncerr(so_dim.y,
                                                         so_dim.var_y,
                                                         val,
                                                         err2,
                                                         a_start=start)

        
    # Check for so_id keyword argument
    if kwargs.has_key("so_id"):
        so_dim.id = kwargs["so_id"]
    else:
        so_dim.id = 0

    comb_som = SOM.SOM()
    comb_som.copyAttributes(som_1)

    del som_1

    # Check for y_label keyword argument
    if kwargs.has_key("y_label"):
        comb_som.setYLabel(kwargs["y_label"])
    else:
        comb_som.setYLabel("Counts")

    # Check for y_units keyword argument
    if kwargs.has_key("y_units"):
        comb_som.setYUnits(kwargs["y_units"])
    else:
        comb_som.setYUnits("Counts / Arb")

    # Check for x_labels keyword argument
    if kwargs.has_key("x_label"):
        comb_som.setAllAxisLabels(["Pixel Number", kwargs["x_label"]])
    else:
        comb_som.setAllAxisLabels(["Pixel Number", "Arbitrary"])

    # Check for x_units keyword argument
    if kwargs.has_key("x_units"):
        comb_som.setAllAxisUnits(["Pixel#", kwargs["x_units"]])
    else:
        comb_som.setAllAxisUnits(["Pixel#", "Arb"])

    comb_som.append(so_dim)

    del so_dim

    return comb_som


if __name__ == "__main__":
    import hlr_test

    som1 = hlr_test.generate_som("histogram", 1, 3)
    som1.attr_list.instrument = SOM.ASG_Instrument()

    x_axis_err = hlr_utils.make_axis(0, 1, 0.25)

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]
    print "* ", som1[2]

    print "********** create_X_vs_pixpos"
    print " som :", create_X_vs_pixpos(som1, som1[0].axis[0].val, x_axis_err,
                                       withXVar="True")
