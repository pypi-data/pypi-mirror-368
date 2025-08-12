###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""Dummy module to be removed as soon
as all the Transformations with it in the workflow XML are gone
"""
import os

from DIRAC import gLogger
from DIRAC.Core.Utilities.ReturnValues import S_OK

from LHCbDIRAC.Workflow.Modules.ModuleBase import ModuleBase


class ErrorLogging(ModuleBase):
    def __init__(self):
        """c'tor."""

        self.log = gLogger.getSubLogger("ErrorLogging")
        super().__init__(self.log)

    def execute(self, *args, **kwargs):
        self.log.info(f"===== Executing fake ErrorLogging module ===== ")
        return S_OK()
