#!/usr/bin/env python

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

###############################################################################
#
# Script for installing the HLRedux package modules and scripts
#
# $Id$
#
###############################################################################

from distutils.core import setup
import distutils.sysconfig
import getopt
import os
import sys
from version import version as __version__

# Package name and version information
PACKAGE = "HLRedux"
VERSION = __version__

package_list = ['', 'common_lib', 'dr_lib', 'hlr_utils', 'hlr_test']

instrument_scripts = {
    "ASG" : [
    'memory_test',
    'null_int_test',
    'null_int_test2'
    ],
    "DGS" : [
    ],
    "IGS" : [
    'amorphous_reduction',
    'delta_E0',
    'igs_diff_reduction'
    ],
    "PD" : [
    ],
    "REF" : [
    'get_specular_background',
    'incident_spectrum_ratio',
    'reflect_reduction',
    'specular_area',
    'specular_point'
    ],
    "SAS" : [
    ],
    "SCD" : [
    ]
    }

def pythonVersionCheck():
    # Minimum version of Python
    PYTHON_MAJOR = 2
    PYTHON_MINOR = 2

    if sys.version_info < (PYTHON_MAJOR, PYTHON_MINOR):
        print >> sys.stderr, 'You need at least Python %d.%d for %s %s' \
              % (PYTHON_MAJOR, PYTHON_MINOR, PACKAGE, VERSION)
        sys.exit(-3)


def parseOptions( argv, keywords ):
    """get values for input keywords

    inputs like:
    --keyword=value

    transformed to a dictionary of 
    {keyword: value}

    if nothing is given, value is set to default: True
    """
    res = {}
    for keyword in keywords:
        for i, item in enumerate(argv):
            if item.startswith(keyword):
                value = item[ len(keyword) + 1: ]
                if value == "": value = True
                res[keyword] = value
                del argv[i]
                pass
            continue
        continue
    return res


def parseCommandLine():
    argv = sys.argv

    keywords = ['--inst']
    options = parseOptions(argv, keywords)

    instruments = None
    if options.get('--inst'):
        instruments = options['--inst'].split(',')
    else:
        instruments = ["All"]

    return instruments


def getScripts(instruments):
    scripts = []
    if len(instruments) == 1:
        if instruments[0].lower() == "all":
            for key in instrument_scripts.keys():
                for script in instrument_scripts[key]:
                    scripts.append(os.path.join('drivers', key, script))
        else:
            if instrument_scripts.has_key(instruments[0]):
                for script in instrument_scripts[instruments[0]]:
                    scripts.append(os.path.join('drivers', instruments[0],
                                                script))
            else:
                print "No such instrument", instrument[0]

    else:
        for inst in instruments:
            if instrument_scripts.has_key(inst):
                for script in instrument_scripts[inst]:
                    scripts.append(os.path.join('drivers', inst, script))
            else:
                print "No such instrument", inst

    return scripts


if __name__ == "__main__":
    pythonVersionCheck()
    instruments = parseCommandLine()
    script_list = getScripts(instruments)

    setup(name=PACKAGE,
          version=VERSION,
          extra_path=PACKAGE,
          packages=package_list,
          scripts=script_list)
                        
