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

import SOM

class DrParameter(SOM.NxParameter):
    """
    This class handles configuration parameters that require a value, an
    error and sometimes units. 
    """

    def __init__(self, value, error=None, units=None, **kwargs):
        """
        The class constructor

        @param value: The parameter value
        @type value: C{float}
        
        @param error: The parameter error. Note this can be error^2
        @type error: C{float}
        
        @param units: The parameter units
        @type units: C{string}
        
        @param kwargs: A list of keyword arguments that the function accepts:
        
        @keyword is_square: Flag that tells the object if the provided error is
                            the error squared (error^2). The default behavior
                            is I{True}.
        @type is_square: C{boolean}
        """
        self.__nxpar = SOM.NxParameter(float(value), units)
        self.__error = float(error)
        try:
            self.__is_square = kwargs["is_square"]
        except KeyError:
            self.__is_square = True
            
    def __repr__(self):
        """
        This method returns the object representation of the C{DrParameter}.

        @return: The object representation of the C{DrParameter} information
        @rtype: C{string}
        """
        return self.__str__()

    def __str__(self):
        """
        This method returns the string representation of the C{DrParameter}
        information. The error printed is whatever the stored value is
        reguardless whether or not the stored error is squared.

        @return: The string representation of the C{DrPrameter} information
        @rtype: C{string}
        """
        if self.__error is None:
            if self.__nxpar.getUnits() is None:
                return str((self.__nxpar.getValue(), 0.0))
            else:
                return str((self.__nxpar.getValue(), 0.0,
                            str(self.__nxpar.getUnits())))
        else:
            if self.__nxpar.getUnits() is None:
                return str((self.__nxpar.getValue(), self.__error))
            else:
                return str((self.__nxpar.getValue(), self.__error,
                            str(self.__nxpar.getUnits())))

    def getError(self, errsqr=False):
        """
        This method obtains the error of the C{DrParameter}.

        @param errsqr: Flag for returning the square of the error
        @type errsqr: C{boolean}

        
        @return: The associated C{DrParameter} error
        @rtype: C{float}
        """
        if not errsqr or self.__is_square:
            return self.__error
        else:
            return self._error * self.__error

    def getUnits(self):
        """
        This method obtains the units of the C{DrParameter}.

        @return: The associated C{DrParameter} units
        @rtype: C{string}
        """        
        return self.__nxpar.getUnits()

    def getValue(self):
        """
        This method obtains the value of the C{DrParameter}.

        @return: The associated C{DrParameter} value
        @rtype: C{float}
        """
        return self.__nxpar.getValue()

    def isSqrError(self):
        """
        This method returns the current state of the stored error.

        @return: The sqaured state of the associated C{DrParameter} error
        @rtype: C{float}
        """
        return self.__is_square

    def toFullTuple(self, errsqr=False):
        """
        This method returns a tuple containing all information C{(value, error,
        units)} from the C{DrParameter}.

        @param errsqr: Flag for returning the square of the error
        @type errsqr: C{boolean}


        @return: Object of the form C{(value, error, units)} or
                 C{(value, error^2, units)}
        @rtype: C{tuple}
        """
        if not errsqr or self.__is_square:
            return (self.__nxpar.getValue(), self.__error,
                    self.__nxpar.getUnits())
        else:
            return (self.__nxpar.getValue(), self.__error * self.__error,
                    self.__nxpar.getUnits())
        
    def toValErrTuple(self, errsqr=False):
        """
        This method returns a tuple containing some of the C{DrParameter}
        information C{(value, error)}.

        @param errsqr: Flag for returning the square of the error
        @type errsqr: C{boolean}


        @return: Object of the form C{(value, error)} or C{(value, error^2)}
        @rtype: C{tuple}
        """
        if errsqr or not self.__is_square:
            return (self.__nxpar.getValue(), self.__error * self.__error)
        else:
            return (self.__nxpar.getValue(), self.__error)

    def toXmlConfig(self, doc, node):
        """
        This method an XML document and node and fills the information from the
        C{DrParameter} object within the incoming node. 

        @param doc: An instance of an XML document
        @type doc: C{xml.dom.minidom.Document}
        
        @param node: A XML node for storing the C{DrParameter} object
        information
        @type node: C{xml.dom.minidom.Node}


        @return: The XML node with the C{DrParameter} object information
        @rtype: C{xml.dom.minidom.Node}
        """
        import math
        import xml.dom.minidom
        
        value_node = doc.createElement("value")
        value_text = doc.createTextNode(str(self.__nxpar.getValue()))
        value_node.appendChild(value_text)

        error_node = doc.createElement("error")
        error_node.setAttribute("is_square", str(self.__is_square))
        error_text = doc.createTextNode(str(self.__error))
        error_node.appendChild(error_text)

        units_node = doc.createElement("units")
        units_text = doc.createTextNode(str(self.__nxpar.getUnits()))
        units_node.appendChild(units_text)
        
        node.appendChild(value_node)
        node.appendChild(error_node)
        node.appendChild(units_node)

        return node
    
def DrParameterFromString(infostr, errsqr=False):
    """
    Alternative constructor for C{DrParameter}

    @param infostr: Information of the following forms. The error may be
                    presented as error^2.
                        - \"value,error,units=unitname\"
                        - \"value,error\"
                        - \"value,units=unitname\"
    @type infostr: C{string}
    
    @param errsqr: Flag which tells if the incoming error is squared (error^2)
                   or not (error)
    @type errsqr: C{boolean}

    
    @return: Object containing the requested information
    @rtype: C{hlr_utils.DrParameter}
    """
    # Kickout None if infostr is None
    if infostr is None:
        return None
    
    values = infostr.split(',')
    lenval = len(values)

    if lenval < 2 or lenval > 3:
        raise RuntimeError("DrParameter object requires at least two pieces "\
                           +"of information and a max of three pieces. See "\
                           +"class documentation for details")


    if not values[-1].find("units"):
        units = values[-1].split('=')[-1]
        try:
            error = float(values[1])
        except ValueError:
            error = 0.0
    else:
        error = values[1]
        units = None

    return DrParameter(values[0], error, units, is_square=errsqr)

def DrParameterFromXmlConfig(node, sqrerr=False):
    """
    Alternative constructor for C{DrParameter} object

    @param node: A node from an XML that contains the information for
    generating a C{DrParameter} object
    @type node: C{xml.dom.minidom.Node}
    
    @param sqrerr: Flag which allows one to square the incoming error
    @type sqrerr: C{boolean}


    @return: Object based on the XML node information
    @rtype: C{hlr_utils.DrParameter}
    """
    import os
    
    value_node = node.getElementsByTagName("value")[0]
    value = float(value_node.childNodes[0].nodeValue)    

    error_node = node.getElementsByTagName("error")[0]

    error_attr = error_node.attributes.getNamedItem("is_square").nodeValue
    if error_attr == "False":
        error_square = False
    elif error_attr == "True":
        error_square = True
        
    error = float(error_node.childNodes[0].nodeValue)

    if sqrerr and not error_square:
        error *= error
        error_square = True
    
    unit_node = node.getElementsByTagName("units")[0]
    units = unit_node.childNodes[0].nodeValue.strip(os.linesep).strip(' ')

    return DrParameter(value, error, units, is_square=error_square)

if __name__ == "__main__":
    import hlr_utils

    par1 = DrParameter(10.0, 1.4, "microseconds")
    par2 = hlr_utils.DrParameterFromString("-3.4,0.42,units=meV")

    import xml.dom.ext
    import xml.dom.minidom

    doc = xml.dom.minidom.Document()
    mainnode = doc.createElement("test_par")
    doc.appendChild(mainnode)
    anode = par2.toXmlConfig(doc, mainnode)

    xml.dom.ext.PrettyPrint(doc, open("test.xml", "w"))

    rdoc = xml.dom.minidom.parse("test.xml")
    tnode = rdoc.getElementsByTagName("test_par")[0]
    par3 = hlr_utils.DrParameterFromXmlConfig(tnode)

    print "****************************************"
    print "* par1: ", par1
    print "* par1 (T): ", par1.toFullTuple()    
    print "* par2: ", par2
    print "* par3: ", par3
