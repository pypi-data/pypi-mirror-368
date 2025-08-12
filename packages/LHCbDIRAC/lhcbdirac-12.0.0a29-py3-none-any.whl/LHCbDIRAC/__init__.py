###############################################################################
# (c) Copyright 2025 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import os

from importlib.metadata import version as get_version, PackageNotFoundError

rootPath = os.path.dirname(os.path.realpath(__path__[0]))

try:
    __version__ = get_version(__name__)
    version = __version__
except PackageNotFoundError:
    version = "Unknown"


def extension_metadata():
    return {
        "primary_extension": True,
        "priority": 100,
        "setups": {
            "Production": "dips://lhcb-conf-dirac.cern.ch:9135/Configuration/Server",
            "Certification": "https://lhcb-cert-conf-dirac.cern.ch:9135/Configuration/Server",
        },
        "default_setup": "Production",
    }
