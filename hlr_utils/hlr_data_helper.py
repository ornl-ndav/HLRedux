# this should be replaced with an enum
SOM_type="SOM"
SO_type="SO"
num_type="number"

def empty_result(obj1,obj2):
    """
    This function inspects the arguments and returns an appropriate
    return type for an operation using the arguments. The object can
    be filled using result_insert.
    """

    return (None,SOM_type)

def result_insert(result,descr,value):
    """
    This function takes value and puts it into the result in an
    appropriate fasion. The description is used for decision making.
    """
    pass

def get_length(obj1,obj2=None):
    """
    This function returns the length appropriate for itterating
    through the objects.
    """
    return 0

def get_descr(obj1,obj2=None):
    return SOM_type

def get_value(obj,index=0,descr=None):
    """
    This function takes an arbitrary object and returns the value for
    the given index. If the object is not a collection the index is
    ignored.
    """
    return 0

def get_err2(obj,index,descr=None):
    """
    This function takes an arbitrary object and returns the
    uncertainty squared for the given index. If the object is not a
    collection the index is ignored.
    """
    return 0
