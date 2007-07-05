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

class Axis(object):
    """
    This class provides a container for information to create a data axis
    """

    def __init__(self, min, max, delta, units="", title=""):
        """
        Constructor for class

        @param min: The axis minimum value
        @type min: C{float}
        
        @param max: The axis maximum value
        @type max: C{float}
        
        @param delta: The bin width (histogram) or spacing (density) of the
                      axis
        @type delta: C{float}

        @param units: The units associated with the axis values
        @type units: C{string}
        
        @param title: The title associated with the axis
        @type title: C{string}
        """
        self.__min = float(min)
        self.__max = float(max)
        self.__delta = float(delta)
        self.__units = units
        self.__title = title

    def __repr__(self):
        """
        This method returns an instance representation of the C{Axis} object

        @return: The representation of the C{Axis} object
        @rtype: C{string}
        """
        return self.__str__()

    def __str__(self):
        """
        This method returns a string representation of the C{Axis} object

        @return: The representation of the C{Axis} object
        @rtype: C{string}
        """
        return "Min=%f, Max=%f, Delta=%f, Units=%s, Title: %s" % \
               (self.__min, self.__max, self.__delta, str(self.__units),
                self.__title)

    def __eq__(self, other):
        """
        This method checks to see if the incoming C{Axis} object and the
        current one are equal.

        @param other: Object to check for equality
        @type other: C{Axis} 


        @return: I{True} if the C{Axis} objects are equal, I{False} if they
                 are not
        @rtype: C{boolean}
        """
        try:
            if self.__min != other.getMinimum():
                return False

            if self.__max != other.getMaximum():
                return False

            if self.__delta != other.getDelta():
                return False
            
            if self.__units != other.getUnits():
                return False            

        except:
            return True

        return True

    def __neq__(self, other):
        """
        This method checks to see if the incoming C{Axis} object and the
        current one are not equal.

        @param other: Object to check for equality
        @type other: C{Axis} 


        @return: I{True} if the C{Axis} objects are not equal, I{False} if they
                 are
        @rtype: C{boolean}
        """
        return not self.__eq__(other)

    def getDelta():
        """
        This method returns the C{Axis} object's delta parameter

        @return: C{Axis} delta parameter
        @rtype: C{float}
        """
        return self.__delta

    def getMaximum():
        """
        This method returns the C{Axis} object's maximum axis value

        @return: C{Axis} axis maximum parameter
        @rtype: C{float}
        """
        return self.__max

    def getMinimum():
        """
        This method returns the C{Axis} object's minimum axis value

        @return: C{Axis} axis minimum parameter
        @rtype: C{float}
        """
        return self.__min

    def getTitle():
        """
        This method returns the C{Axis} object's axis title

        @return: C{Axis} title
        @rtype: C{string}
        """        
        return self.__title

    def getUnits():
        """
        This method returns the C{Axis} object's units

        @return: C{Axis} units
        @rtype: C{string}
        """        
        return self.__units

    def setDelta(delta):
        """
        This method sets the C{Axis} object's delta parameter

        @param delta: Value of the C{Axis} object's delta parameter
        @type delta: C{float}
        """        
        self.__delta = float(delta)

    def setMaximum(max):
        """
        This method sets the C{Axis} object's maximum axis value

        @param max: Value of the C{Axis} object's max parameter
        @type max: C{float}
        """        
        self.__max = float(max)

    def setMinimum(min):
        """
        This method sets the C{Axis} object's minimum axis value

        @param min: Value of the C{Axis} object's min parameter
        @type min: C{float}
        """        
        self.__min = float(min)

    def setTitle(title):
        """
        This method sets the C{Axis} object's title string

        @param title: The title for the C{Axis} object
        @type title: C{string}
        """
        self.__title = str(title)

    def setUnits(units):
        """
        This method sets the C{Axis} object's units 

        @param units: The units for the C{Axis} object
        @type units: C{string}
        """
        self.__units = units
        
    def toNessiList(self, type="histogram"):
        """
        This method provides a mechanism for the class to generate a
        C{NessiList} axis based on the information contained within the
        C{Axis} object. The type parameter sets additional data depending on
        type. The main types of data are I{histogram} or I{density} (also
        I{coordinate}).

        @param type: The axis data type: I{histogram} or I{density}
        @type type: C{string}
        """
        import math
        import nessi_list
        
        n_bins = int(math.fabs(self.__max - self.__min) / self.__delta)

        axis = nessi_list.NessiList()
        
        for i in xrange(n_bins):
            axis.append(self.__min + i * self.__delta)

        try:
            if(type == "histogram"):
                axis.append(self.__max)
            elif(type == "density" or type == "coordinate"):
                pass
            else:
                raise RuntimeError("Do not understand type: %s" % type)
        except KeyError:
            axis.append(self.__max)

        return axis

    def toXmlConfig(self, doc, node):
        """
        This method an XML document and node and fills the information from the
        C{Axis} object within the incoming node

        @param doc: Instance of an XML document
        @type doc: C{xml.dom.minidom.Document}
        
        @param node: A XML node for storing the C{Axis} object information
        @type node: C{xml.dom.minidom.Node}


        @return: The XML node with the C{Axis} object information
        @rtype: C{xml.dom.minidom.Node}
        """
        import xml.dom.minidom

        min_node = doc.createElement("min")
        min_text = doc.createTextNode(str(self.__min))
        min_node.appendChild(min_text)

        max_node = doc.createElement("max")
        max_text = doc.createTextNode(str(self.__max))
        max_node.appendChild(max_text)

        delta_node = doc.createElement("delta")
        delta_text = doc.createTextNode(str(self.__delta))
        delta_node.appendChild(delta_text)

        units_node = doc.createElement("units")
        units_text = doc.createTextNode(str(self.__units))
        units_node.appendChild(units_text)

        title_node = doc.createElement("title")
        title_text = doc.createTextNode(str(self.__title))
        title_node.appendChild(title_text)        
        
        node.appendChild(min_node)
        node.appendChild(max_node)
        node.appendChild(delta_node)
        node.appendChild(units_node)
        node.appendChild(title_node)        

        return node

def AxisFromString(infostr):
    """
    Alternative constructor for C{Axis} object

    @param infostr: A comma delimited list containing the following pieces of
                    information: axis minimum, axis maximum, axis bin width,
                    axis units and axis title. The mimimum string must conatin
                    the first three pieces of information (min, max, width). If
                    units and title are supplied, it must be in the order l
                    isted above.
    @type infostr: C{string}
    

    @return: A new object based on the information within the C{string}
    @rtype: C{hlr_utils.Axis} 
    """
    # Kickout None if infostr is None
    if infostr is None:
        return None
    
    values = infostr.split(',')
    lenval = len(values)

    if lenval < 3 or lenval > 5:
        raise RuntimeError("Axis object requires at least three pieces of "\
                           +"information and a max of five pieces. See class "\
                           +"documentation for details")
    try:
        return Axis(values[0], values[1], values[2], values[3],
                              values[4])
    except IndexError:
        try:
            return Axis(values[0], values[1], values[2], values[3])
        except IndexError:
            return Axis(values[0], values[1], values[2])

def AxisFromXmlConfig(node):
    """
    Alternative constructor for C{Axis} object

    @param node: XML node that contains the information for generating a
                 C{Axis} object
    @type node: C{xml.dom.minidom.Node}


    @return: A new object based on the XML node information
    @rtype: C{hlr_utils.Axis} 
    """
    import os

    amin = float(node.getElementsByTagName("min")[0].childNodes[0].nodeValue)
    amax = float(node.getElementsByTagName("max")[0].childNodes[0].nodeValue)

    delta_node = node.getElementsByTagName("delta")[0]
    delta = float(delta_node.childNodes[0].nodeValue)    

    unit_node = node.getElementsByTagName("units")[0]
    units = unit_node.childNodes[0].nodeValue.strip(os.linesep).strip(' ')

    title_node = node.getElementsByTagName("title")[0]
    title = title_node.childNodes[0].nodeValue.strip(os.linesep).strip(' ')
    
    return Axis(amin, amax, delta, units, title) 

if __name__ == "__main__":
    import hlr_utils
    
    axis1 = Axis(0, 10, 1, "arb", "A Test Axis")
    axis2 = hlr_utils.AxisFromString("4,50,0.1")

    import xml.dom.ext
    import xml.dom.minidom

    doc = xml.dom.minidom.Document()
    mainnode = doc.createElement("test_axis")
    doc.appendChild(mainnode)
    anode = axis2.toXmlConfig(doc, mainnode)

    xml.dom.ext.PrettyPrint(doc, open("test.xml", "w"))

    rdoc = xml.dom.minidom.parse("test.xml")
    tnode = rdoc.getElementsByTagName("test_axis")[0]
    axis3 = hlr_utils.AxisFromXmlConfig(tnode)

    print "****************************"
    print "* Axis1: ", axis1
    print "* Axis2: ", axis2
    print "* Axis2 (NL):", axis2.toNessiList()
    print "* Axis3: ", axis3
    
