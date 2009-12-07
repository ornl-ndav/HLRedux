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

class NxPath(object):
    """
    This class creates U{NeXus<www.nexusformat.org>} path,signal groups from an
    incoming comma-separated string. The string needs to have an even number of
    entries. The string should have the following form:
    I{/entry/bank1,1/entry/bank2,1}. The string can also be just a listing of
    numeric bank numbers: I{1-4,7-10}. One can also add alternate path
    destinations for the numeric specification. A colon is used as the
    delimiter I{:} to designate that what follows is the path. The path is
    given as a comma delimited list with the final part being the string that
    the numeric entries will be appended to: I{1:entry,monitor}.
    """

    def __init__(self, infostr):
        """
        Constructor for class

        @param infostr: Comma-separated values for I{NeXus} paths and signals.
        @type infostr: C{string}
        """
        if infostr is None:
            self.__length = 0
            self.__data_paths = None
            return

        self.__data_paths = []
        
        if infostr[0].isdigit():
            if ":" in infostr:
                (bankstr, paths) = infostr.split(':')
                paths = paths.split(',')
            else:
                paths = None
                bankstr = infostr
            
            import sns_inst_util
            banks = sns_inst_util.generateList([bankstr])
            for bank in banks:
                if paths is None:
                    self.__data_paths.append(("/entry/bank"+str(bank), 1))
                else:
                    self.__data_paths.append(("/"+"/".join(paths)+str(bank),
                                              1))

            # Count of entry + signal
            self.__length = len(banks) * 2
            
            # If only one entry, make this a tuple for sure
            if self.__length == 2:
                self.__data_paths = (self.__data_paths[0])
        else:
            mylist = infostr.split(',')
            self.__length = len(mylist)

            if self.__length == 2:
                use_extend = True
            else:
                use_extend = False
            
            for i in range(0, len(mylist), 2):
                if use_extend:
                    self.__data_paths.extend((mylist[i], int(mylist[i + 1])))
                else:
                    self.__data_paths.append((mylist[i], int(mylist[i + 1])))

    def __repr__(self):
        """
        This method returns an instance representation of the C{NxPath} object

        @return: The object representation of the C{NxPath} information
        @rtype: C{string}
        """
        return self.__str__()

    def __str__(self):
        """
        This method returns a string representation of the C{NxPath} object

        @return: The string representation of the C{NxPath} information
        @rtype: C{string}
        """
        return str(self.toPath())

    def toPath(self):
        """
        This method returns a tuple or list of tuples of NeXus path, signal
        pairs

        @return: Objects like C{('/entry/bank1', 1)} or C{[('/entry/bank1', 1),
                 ('/entry/bank2', 1)]}
        @rtype: C{tuple} or C{list} of C{tuple}s         
        """
        if self.__length == 2:
            return tuple(self.__data_paths)
        else:
            return self.__data_paths

    def toXmlConfig(self, doc, node):
        """
        This method an XML document and node and fills the information from the
        C{NxPath} object within the incoming node

        @param doc: An instance of an XML document
        @type doc: C{xml.dom.minidom.Document}
        
        @param node: A XML node for storing the C{NxPath} object information
        @type node: C{xml.dom.minidom.Node}


        @return: The XML node with the C{NxPath} object information
        @rtype: C{xml.dom.minidom.Node}
        """
        if self.__data_paths is None:
            return None
        else:
            import xml.dom.minidom

            tnode = doc.createTextNode(str(self.toPath()))
            node.appendChild(tnode)

            return node

def NxPathFromXmlConfig(node):
    """
    Alternative constructor for C{NxPath} object

    @param node: A node from an XML that contains the information for
                 generating a C{NxPath} object
    @type node: C{xml.dom.minidom.Node}


    @return: Object based on the XML node information
    @rtype: C{hlr_utils.NxPath}
    """
    node_val = str(node.childNodes[0].nodeValue).split(',')
    fix_val = []
    for val in node_val:
        fix_val.append(str(val.lstrip('([ \'"').rstrip(')] \'')))

    return NxPath(",".join(fix_val))

if __name__ == "__main__":
    import hlr_utils
    
    str1 = "/entry/bank1,1"
    str2 = "/entry/bank1,1,/entry/bank2,1"

    path1 = NxPath(str1)
    path2 = NxPath(str2)

    import xml.dom.ext
    import xml.dom.minidom

    doc = xml.dom.minidom.Document()
    mainnode = doc.createElement("test")
    doc.appendChild(mainnode)
    node1 = doc.createElement("test_path1")
    mainnode.appendChild(node1)
    anode1 = path1.toXmlConfig(doc, node1)
    node2 = doc.createElement("test_path2")
    mainnode.appendChild(node2)
    anode2 = path2.toXmlConfig(doc, node2)    

    xml.dom.ext.PrettyPrint(doc, open("test.xml", "w"))

    rdoc = xml.dom.minidom.parse("test.xml")
    tnode1 = rdoc.getElementsByTagName("test_path1")[0]
    path3 = hlr_utils.NxPathFromXmlConfig(tnode1)

    tnode2 = rdoc.getElementsByTagName("test_path2")[0]
    path4 = hlr_utils.NxPathFromXmlConfig(tnode2)    

    print "******************************"
    print "* path1:", path1
    print "* path2:", path2.toPath()
    print "* path3:", path3.toPath()
    print "* path4:", path4
