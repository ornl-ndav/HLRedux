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

def generate_so(data_type, start, stop=0, dim=1, extra=0):
    """
    This function generates a C{SO} for testing purposes. The C{SO} can be
    either histogram or density data.

    @param data_type: is defined as histogram or density
    @type data_type: C{string}
    @param start: is the starting value for number generation
    @type start: C{int}
    @param stop: (OPTIONAL) is the stopping value for number generation
    @type stop: C{int}
    @param dim: (OPTIONAL) allows for making C{SO}s multi-dimensional
    @type dim: C{int}
    @param extra: (OPTIONAL) is an offset added to the B{start} and B{stop}
    values
    @type extra: C{int}              
    
    @return: A C{SO} filled with default information
    @rtype: C{SOM.SO}
    """
    
    if stop < start:
        stop = start
        start = 0
        
    so = SOM.SO(dim, construct=True)
    if start == stop:
        return so

    if data_type.lower() == "histogram":
        num = stop - start + 1
    else:
        num = stop - start

    for i in range(dim):
        so.axis[i].val.extend(range(num))
        size = len(so.axis[i].val)

        if i == 0:
            so.y.extend(range(start + extra, stop + extra))
            so.var_y.extend(range(start + extra, stop + extra))
        else:
            counter = 0
            while counter < (size - 2):
                so.y.extend(range(start + extra, stop + extra))
                so.var_y.extend(range(start + extra, stop + extra))
                counter += 1

    return so


def generate_som(data_type="histogram", dim=1, number=2):
    """
    This function generates a C{SOM} for testing purposes.

    @param data_type: (OPTIONAL) is defined as histogram or density
    @type data_type: C{string}
    @param dim: (OPTIONAL) is the dimensionality of the individual C{SO}s
    @type dim: C{int}
    @param number: (OPTIONAL) is the number of C{SO}s generated
    @type number: C{int}

    @return: A C{SOM} containing the requested information
    @rtype: C{SOM.SOM}
    """

    som = SOM.SOM()
    som.setDataSetType(data_type)
    count = 0
    for i in range(number):
        so = generate_so(data_type, count, count + 5, dim)
        so.id = i + 1
        som.append(so)
        count += 5

    return som
