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

def param_array(som, param):
    """
    This function takes a parameter and interrogates the object for that
    information.

    @param som: The object containing the requested information.
    @type som: C{SOM.SOM}

    @param param: The name of the parameter to seek.
    @type param: C{string}


    @return: An array of the parameters from the incoming object.
    @rtype: C{list}
    """
    len_som = hlr_utils.get_length(som)
    plist = []
    inst = som.attr_list.instrument

    for i in xrange(len_som):
        plist.append(hlr_utils.get_parameter(param, som[i], inst)[0])

    return plist
        
def negparam_array(som, param):
    """
    This function takes a parameter and interrogates the object for that
    information and flips its sign.

    @param som: The object containing the requested information.
    @type som: C{SOM.SOM}

    @param param: The name of the parameter to seek.
    @type param: C{string}


    @return: An array of the negated values from parameters from the incoming
             object.
    @rtype: C{list}
    """
    len_som = hlr_utils.get_length(som)
    plist = hlr_utils.param_array(som, param)

    for i in xrange(len_som):
        plist[i] *= -1.0

    return plist
    
def __trig_param_array(som, param, trig_func):
    """
    This private function applies a trigonometric function to a given
    parameter obtained from the supplied object.

    @param som: The object containing the requested information.
    @type som: C{SOM.SOM}

    @param param: The name of the parameter to seek.
    @type param: C{string}

    @param trig_func: The name of the trigonometric function to apply.
    @type trig_func: C{string}
    

    @return: An array of trigonometry applied values from parameters from the
             incoming object.
    @rtype: C{list}   
    """
    import math
    len_som = hlr_utils.get_length(som)
    plist = []
    inst = som.attr_list.instrument

    tfunc = math.__getattribute__(trig_func)

    for i in xrange(len_som):
        plist.append(tfunc(hlr_utils.get_parameter(param, som[i], inst)[0]))

    return plist
