import axis_manip
import SOM.so
import SOM.som

def copy_attr(source,destination):
    for key in source.attr_list.keys():
        destination.attr_list[key]=source.attr_list[key]

def tof_to_initial_wavelength_igs(left,right):
    TITLE=SOM.som.SOM.TITLE
    X_UNITS=SOM.som.SOM.X_UNITS
    Y_UNITS=SOM.som.SOM.Y_UNITS

    pass
