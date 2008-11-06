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

class Configure:
    """
    This class provides a store location for various pieces of information
    gathered during or necessary for the data reduction process. It can be
    used later to provide metadata files, but that is handled in a separate
    mechanism.
    """
    def __init__(self):

        self.verbose = False
        self.data = None
        self.output = None

    def __repr__(self):
        """
        This method returns an instance representation of the C{Configure}
        object

        @return: The representation of the C{Configure} object
        @rtype: C{string}
        """
        return str(self.__dict__)

    def __str__(self):
        """
        This method returns a string representation of the C{Configure} object

        @return: The representation of the C{Configure} object
        @rtype: C{string}
        """
        import os
        output = ""
        for key, value in self.__dict__.items():
            output += str(key) + ": " + str(value) + os.linesep
        return output

def ConfigFromXml(doc, configure):
    """
    This method takes a configuration file XML document and a
    L{hlr_utils.Configure} object and sets the information from the document
    into the object.

    @param doc: A XML Document that is read from a reduction metadata file
    @type doc: C{xml.dom.minidom.Document}

    @param configure: A configuration object
    @type configure: L{hlr_utils.Configure}


    @return: The configuration object with the information added
    @rtype: L{hlr_utils.Configure}
    """
    import hlr_utils
    
    for node in doc.childNodes:
        for cnode in node.childNodes:
            try:
                attr = cnode.getAttribute("type")
                
                setter = None
                
                if attr == "bool":
                    value = str(cnode.childNodes[0].nodeValue)
                    if value == "False":
                        setter = False
                    elif value == "True":
                        setter = True

                elif attr == "int":
                    setter = int(cnode.childNodes[0].nodeValue)
                
                elif attr == "float":
                    setter = float(cnode.childNodes[0].nodeValue)

                elif attr == "str":
                    setter = str(cnode.childNodes[0].nodeValue)

                elif attr == "unicode":
                    setter = unicode(cnode.childNodes[0].nodeValue)

                elif attr == "list":
                    nval = str(cnode.childNodes[0].nodeValue).strip('[]')
                    sval = nval.split(',')
                    setter = []
                    for val in sval:
                        setter.append(val.strip(' \''))

                elif attr == "tuple":
                    nval = str(cnode.childNodes[0].nodeValue).strip('()')
                    sval = nval.split(',')
                    setter = []
                    for val in sval:
                        try:
                            setter.append(int(val))
                        except ValueError:
                            setter.append(float(val))
                            
                    setter = tuple(setter)
                    
                elif attr == "hlr_utils.hlr_axis_object.Axis":
                    setter = hlr_utils.AxisFromXmlConfig(cnode)

                elif attr == "hlr_utils.hlr_drparameter.DrParameter":
                    setter = hlr_utils.DrParameterFromXmlConfig(cnode)
                    
                elif attr == "hlr_utils.hlr_nxpath.NxPath":
                    setter = hlr_utils.NxPathFromXmlConfig(cnode)

                configure.__dict__[str(cnode.localName)] = setter
                
            except AttributeError:
                continue

    return configure
