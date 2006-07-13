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

def filter_pixels(obj, paths, start_ids, end_ids, **kwargs):
    """
    This function filters a set of pixels based on starting and ending IDs
    for each data path.

    Parameters:
    ----------
    -> obj is a SOM that needs to be filtered
    -> paths is a list of tuples containing the NeXus data paths and signals
    -> start_ids is a list of tuples containing the starting ID pairs (i,j)
                 for each data path in paths
    -> end_ids is a list of tuples containing the ending ID pairs (i,j) for
               each data path in paths

    Returns:
    -------
    <- A tuple of containing the SOM with the pixels in the filter range and
       SOM containing the rest of the pixels not filtered

    Exceptions:
    ----------
    <- TypeError is raised if obj is not a SOM
    <- RuntimeError is raised if the number of data paths, starting IDs and
                    ending IDs are not all identical
    """

    # import the helper functions
    import hlr_utils

    # set up for working through data
    (result, res_descr) = hlr_utils.empty_result(obj)
    o_descr = hlr_utils.get_descr(obj)

    if o_descr != "SOM":
        raise TypeError, "Only SOM operations supported"
    else:
        pass

    if len(paths) != len(start_ids) and len(start_ids) != len(end_ids):
        raise RuntimeError, "Data paths, starting ids and ending ids need "\
              +"to have the same length."
    else:
        pass

    result = hlr_utils.copy_som_attr(result, res_descr, obj, o_descr)

    # Next three try/except blocks look for difference between list and tuple
    try:
        paths.reverse()
        paths.reverse()
    except AttributeError:
        temp = paths
        paths = []
        paths.append(temp)

    try:
        start_ids.reverse()
        start_ids.reverse()
    except AttributeError:
        temp = start_ids
        start_ids = []
        start_ids.append(temp)

    try:
        end_ids.reverse()
        end_ids.reverse()
    except AttributeError:
        temp = end_ids
        end_ids = []
        end_ids.append(temp)

    for path, s_id, e_id in map(None, paths, start_ids, end_ids):
        bank = path[0].split('/')[-1]

        for i in range(s_id[0], e_id[0]):
            for j in range(s_id[1], e_id[1]):
                id = (bank, (i, j))

                length = hlr_utils.get_length(obj)

                nabove = length + 1
                nbelow = 0
                index = nbelow - 1
                
                while nabove - nbelow > 1:
                    middle = (nabove + nbelow) / 2

                    if id == obj[middle-1].id:
                        index = middle - 1
                        break

                    if id < obj[middle-1].id:
                        nabove = middle
                    else:
                        nbelow = middle

                if index != -1:
                    so = obj.pop(index)

                    hlr_utils.result_insert(result, res_descr, so, None, "all")

    return (result, obj)
    

if __name__=="__main__":
    import hlr_test
    import SOM

    som1=hlr_test.generate_som("histogram", 1, 5)

    som1[0].id = ("bank1", (0, 0))
    som1[1].id = ("bank1", (1, 0))
    som1[2].id = ("bank1", (2, 0))
    som1[3].id = ("bank1", (3, 0))
    som1[4].id = ("bank1", (4, 0))
    

    print "********** SOM1"
    print "* ", som1[0]
    print "* ", som1[1]
    print "* ", som1[2]
    print "* ", som1[3]
    print "* ", som1[4]
    
    print "********** filter_pixels"
    (in_som, out_som) = filter_pixels(som1, ("/entry/bank1", 1), (1, 0),
                                      (4, 1))
    print "* in som : ", in_som
    print "* out som: ", out_som

