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
"""Unit tests for LHCbScript."""
import unittest
import copy
import os

from DIRAC import gLogger

from LHCbDIRAC.Workflow.Modules.test.mock_Commons import (
    prod_id,
    prod_job_id,
    wms_job_id,
    workflowStatus,
    stepStatus,
    step_id,
    step_number,
    step_commons,
    wf_commons,
)


class ModulesApplicationsTestCase(unittest.TestCase):
    """Base class for the Modules Applications test cases."""

    def setUp(self):
        gLogger.setLevel("DEBUG")
        self.maxDiff = None

    def tearDown(self):
        for fileProd in [
            "prodConf_someApp_123_00000456_123_00000456_321.py",
            "appLog",
            "gaudi_extra_options.py",
            "applicationError.txt",
            "someApp",
            "applicationLog.txt",
        ]:
            try:
                os.remove(fileProd)
            except OSError:
                continue


#############################################################################
# LHCbScript.py
#############################################################################


class LHCbScriptSuccess(ModulesApplicationsTestCase):
    def test_execute(self):
        from LHCbDIRAC.Workflow.Modules.LHCbScript import LHCbScript

        lhcbScript = LHCbScript()

        lhcbScript.jobType = "Merge"
        lhcbScript.stepInputData = ["foo", "bar"]

        lhcbScript.production_id = prod_id
        lhcbScript.prod_job_id = prod_job_id
        lhcbScript.jobID = wms_job_id
        lhcbScript.workflowStatus = workflowStatus
        lhcbScript.stepStatus = stepStatus
        lhcbScript.workflow_commons = wf_commons
        lhcbScript.step_commons = step_commons[0]
        lhcbScript.step_number = step_number
        lhcbScript.step_id = step_id
        lhcbScript.executable = "ls"
        lhcbScript.applicationLog = "applicationLog.txt"

        # no errors, no input data
        for wf_cs in copy.deepcopy(wf_commons):
            for s_cs in step_commons:
                lhcbScript.workflow_commons = wf_cs
                lhcbScript.step_commons = s_cs
                lhcbScript._setCommand()
                lhcbScript._executeCommand()


class LHCbScriptFailure(ModulesApplicationsTestCase):
    def test_execute(self):
        from LHCbDIRAC.Workflow.Modules.LHCbScript import LHCbScript

        lhcbScript = LHCbScript()

        lhcbScript.jobType = "Merge"
        lhcbScript.stepInputData = ["foo", "bar"]

        lhcbScript.production_id = prod_id
        lhcbScript.prod_job_id = prod_job_id
        lhcbScript.jobID = wms_job_id
        lhcbScript.workflowStatus = workflowStatus
        lhcbScript.stepStatus = stepStatus
        lhcbScript.workflow_commons = wf_commons
        lhcbScript.step_commons = step_commons[0]
        lhcbScript.step_number = step_number
        lhcbScript.step_id = step_id

        # no errors, no input data
        for wf_cs in copy.deepcopy(wf_commons):
            for s_cs in step_commons:
                lhcbScript.workflow_commons = wf_cs
                lhcbScript.step_commons = s_cs
                res = lhcbScript.execute()
                self.assertFalse(res["OK"])


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ModulesApplicationsTestCase)
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(LHCbScriptSuccess))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(LHCbScriptFailure))
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
