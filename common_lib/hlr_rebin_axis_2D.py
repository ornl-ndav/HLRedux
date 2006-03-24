import axis_manip
import SOM.so
import SOM.som

def copy_attr(source,destination):
    """
    This function copies the attributes from the source SOM to the destination
    SOM.

    Parameters:
    ----------
    -> source is the SOM from which to copy the attributes
    -> destination is the SOM that receives the copied attributes
    """

    for key in source.attr_list.keys():
        destination.attr_list[key]=source.attr_list[key]

def rebin_axis_2D(obj,axis1,axis2):
    """
    This function rebins two primary axes for a SOM or a SO based on the
    given NessiList axis1 and axis2.

    Parameters:
    ----------
    -> obj is the SOM or SO to be rebinned
    -> axis1 is a NessiList containing the 1st axis to rebin the SOM or SO to
    -> axis2 is a NessiList containing the 2nd axis to rebin the SOM or SO to

    Returns:
    -------
    <- A SOM or SO that has been rebinned according to the provided axis

    Exceptions:
    ----------
    <- TypeError is raised if the rebinning axis given is not a NessiList
    <- TypeError is raised if object being rebinned is not a SOM or a SO
    """
    
    TITLE=SOM.som.SOM.TITLE

    pass
