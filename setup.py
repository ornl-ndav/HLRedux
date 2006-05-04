#!/usr/bin/env python
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

# Package name and version information
PACKAGE = "HLRedux"
VERSION = "1.0.0iqc1"

package_list = ['', 'common_lib', 'dr_lib', 'hlr_utils', 'hlr_test']

instrument_scripts = {
    "ASG" : [
    'null_int_test',
    'null_int_test2'
    ],
    "DGS" : [
    ],
    "IGS" : [
    'amorphous_reduction',
    'delta_E0'
    ],
    "PD" : [
    ],
    "REF" : [
    'get_specular_background',
    'incident_spectrum_ratio',
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
                        
