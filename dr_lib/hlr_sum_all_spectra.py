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

def sum_all_spectra(obj):
    """
    This function takes all the SOs in a SOM and sums them together using the
    summing by weights concept. All of the SOs are assumed to have the same
    axis scale.
    
    Parameters:
    ----------
    -> obj is a SOM in which all of the SOs are to be summed together

    Returns:
    -------
    <- A SOM containing a single spectrum

    Exceptions:
    ----------
    <- TypeError is raised if anything other than a SOM is given 
    """

    # import the helper functions
    import hlr_utils

    (o_descr,d_descr)=hlr_utils.get_descr(obj)

    if o_descr != "SOM":
        raise TypeError, "Function argument must be a SOM"

    (result,res_descr)=hlr_utils.empty_result(obj)

    result=hlr_utils.copy_som_attr(result,res_descr,obj,o_descr)

    # iterate through the values
    import common_lib

    so_id_list = []

    for i in range(hlr_utils.get_length(obj)):
        if i == 0:
            val1 = hlr_utils.get_value(obj,i,o_descr,"all")
            val2 = hlr_utils.get_value(obj,i+1,o_descr,"all")
            value = common_lib.sumw_ncerr(val1, val2)
            so_id_list.append(val1.id)
            so_id_list.append(val2.id)
        elif i == 1:
            pass
        else:
            val = hlr_utils.get_value(obj,i,o_descr,"all")
            value = common_lib.sumw_ncerr(val, value)
            so_id_list.append(val.id)


    hlr_utils.result_insert(result,res_descr,value,None,"all")
    result.attr_list["Summed IDs"] = so_id_list
    result[0].id = 0
            
    return result

if __name__=="__main__":
    import hlr_test
    import SOM
    
    som1=SOM.SOM()
    so1=hlr_test.generate_so("histogram",0,5,1,1)
    so1.id=1
    som1.append(so1)
    so2=hlr_test.generate_so("histogram",0,5,1,3)
    so2.id=2
    som1.append(so2)
    so3=hlr_test.generate_so("histogram",0,5,1,2)
    so3.id=3
    som1.append(so3)

    print "********** SOM1"
    print "* ",som1[0]
    print "* ",som1[1]
    print "* ",som1[2]

    print "********** sum_all_spectra"
    print "* som:",sum_all_spectra(som1)

