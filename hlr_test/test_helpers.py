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

def generate_so(type,start,stop=0,dim=1,extra=0):
    """
    This function generates a SO for testing purposes. The SO can be either
    a histogram or density.

    Parameters:
    ----------
    -> type is defined as histogram or density
    -> start is the starting value for number generation
    -> stop (OPTIONAL) is the stopping value for number generation
    -> dim (OPTIONAL) allows for making SOs multi-dimensional

    Returns:
    -------
    <- A SO
    """
    
    if stop<start:
        stop=start
        start=0
        
    so=SOM.SO(dim)
    if start==stop:
        return so

    if type.lower() == "histogram":
        num = stop-start+1
    else:
        num = stop-start

    for i in range(dim):
        so.axis[i].val.extend(range(num))
        size = len(so.axis[i].val)

        if i == 0:
            so.y.extend(range(start+extra,stop+extra))
            so.var_y.extend(range(start+extra,stop+extra))
        else:
            for j in range(size - 2):
                so.y.extend(range(start+extra,stop+extra))
                so.var_y.extend(range(start+extra,stop+extra))

    return so


def generate_som(type="histogram",dim=1,number=2):
    """
    This function generates a SOM for testing purposes.

    Parameters:
    ----------
    -> type is defined as histogram or density

    Returns:
    -------
    <- A SOM
    """

    som = SOM.SOM()
    count=0
    for i in range(number):
        so=generate_so(type,count,count+5,dim)
        so.id=i+1
        som.append(so)
        count+=5

    return som
