#!/usr/bin/env python
###############################################################################
# (c) Copyright 2024 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""
Make Chris sad...
"""
from DIRAC.Core.Base.Script import Script


@Script()
def main():
    print("Please don't do this, Chris will be sad...")


if __name__ == "__main__":
    main()
