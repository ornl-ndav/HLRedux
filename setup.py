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
from distutils.cmd import Command
import distutils.sysconfig
import getopt
import os
import sys
from HLR_version import version as __version__

# Package name and version information
PACKAGE = "HLRedux"
VERSION = __version__

package_list = ['', 'common_lib', 'dr_lib', 'drivers', 'drivers.GEN',
                'drivers.IGS', 'drivers.REF', 'hlr_utils', 'hlr_test']

instrument_scripts = {
    "ASG" : [
    'memory_test',
    'multi_read',
    'multi_read_run',
    'null_int_test',
    'null_int_test2'
    ],
    "DGS" : [
    ],
    "GEN" : [
    'mask_generator',
    'tof_slicer'
    ],
    "IGS" : [
    'amorphous_reduction',
    'amorphous_reduction_sqe',
    'bss_tof_spect_gen',
    'bss_tof_sum_gen',
    'calc_norm_eff',
    'find_tib',
    'igs_diff_reduction'
    ],
    "PD" : [
    ],
    "REF" : [
    'reflect_reduction'
    ],
    "SAS" : [
    ],
    "SCD" : [
    ]
    }

class build_doc(Command):
    """
    This class is responsible for creating the API documentation via the
    epydoc system.
    """
    description = "Build the API documentation"
    user_options = []
    
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            epydoc_conf = os.path.join('doc', 'config.epy')
            
            from epydoc import cli
            old_argv = sys.argv[1:]

            sys.argv[1:] = [
                "--config=%s" % epydoc_conf,
                "--verbose"
                ]
            cli.cli()

            sys.argv[1:] = old_argv

        except ImportError:
            print "Epydoc is needed to create API documentation. Skipping.."

def pythonVersionCheck():
    # Minimum version of Python
    PYTHON_MAJOR = 2
    PYTHON_MINOR = 2

    if sys.version_info < (PYTHON_MAJOR, PYTHON_MINOR):
        print >> sys.stderr, 'You need at least Python %d.%d for %s %s' \
              % (PYTHON_MAJOR, PYTHON_MINOR, PACKAGE, VERSION)
        sys.exit(-3)


def parseOptions(argv, keywords):
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
        try:
            index = instruments.index("All")
            instruments = ["All"]
        except ValueError:
            try:
                index = instruments.index("GEN")
            except ValueError:
                instruments.append("GEN")
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
          scripts=script_list,
          cmdclass = {'build_doc': build_doc})
                        
