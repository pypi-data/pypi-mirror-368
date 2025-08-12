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
"""Unit tests for Workflow Module RemoveInputData."""

import json
import pytest

from DIRAC import S_OK, S_ERROR
from DIRAC.RequestManagementSystem.Client.Request import Request
from LHCbDIRAC.Workflow.Modules.RemoveInputData import RemoveInputData
from LHCbDIRAC.Workflow.Modules.test.mock_Commons import (
    prod_id,
    prod_job_id,
    wms_job_id,
    workflowStatus,
    step_id,
    step_number,
    wf_commons,
)


# Helper Functions
@pytest.fixture
def rid(mocker):
    """Fixture for StepAccounting module."""
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator")
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.ModuleBase._resolveInputVariables")

    rid = RemoveInputData()
    rid.request = Request()

    yield rid


# Test Scenarios
def test_removeInputData_success(mocker, rid):
    """Test successful execution of RemoveInputData module."""
    rid.inputDataList = [
        "/lhcb/data/2010/EW.DST/00008380/0000/00008380_00000287_1.ew.dst",
        "/lhcb/data/2010/EW.DST/00008380/0000/00008380_00000281_1.ew.dst",
        "/lhcb/data/2011/EW.DST/00008380/0000/00008380_00000281_1.ew.dst",
    ]
    successful = dict.fromkeys((lfn for lfn in rid.inputDataList), True)

    mocker.patch(
        "DIRAC.DataManagementSystem.Client.DataManager.DataManager.removeFile",
        return_value=S_OK({"Successful": successful, "Failed": {}}),
    )

    assert rid.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=rid.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"], "Execution should succeed."

    rid.dataManager.removeFile.assert_called_once()
    args, _ = rid.dataManager.removeFile.call_args
    assert args[0] == rid.inputDataList

    assert rid.request.isEmpty()


def test_removeInputData_failedRemoval(mocker, rid):
    """Test RemoveInputData when the removal of input data fails."""
    successInputDataList = [
        "/lhcb/data/2010/EW.DST/00008380/0000/00008380_00000287_1.ew.dst",
        "/lhcb/data/2010/EW.DST/00008380/0000/00008380_00000281_1.ew.dst",
        "/lhcb/data/2011/EW.DST/00008380/0000/00008380_00000281_1.ew.dst",
    ]
    failedInputDataList = [
        "/lhcb/data/2011/EW.DST/00008380/0000/00008380_00000285_1.ew.dst",
        "/lhcb/data/2011/EW.DST/00008380/0000/00008380_00000286_1.ew.dst",
    ]
    rid.inputDataList = successInputDataList + failedInputDataList
    successful = dict.fromkeys((lfn for lfn in successInputDataList), True)
    failed = dict.fromkeys((lfn for lfn in failedInputDataList), "Failed to remove file")

    mocker.patch(
        "DIRAC.DataManagementSystem.Client.DataManager.DataManager.removeFile",
        return_value=S_OK({"Successful": successful, "Failed": failed}),
    )

    assert rid.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=rid.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"], "Execution should succeed."

    rid.dataManager.removeFile.assert_called_once()
    args, _ = rid.dataManager.removeFile.call_args
    assert args[0] == rid.inputDataList

    assert not rid.request.isEmpty()

    requestDict = json.loads(rid.request.toJSON()["Value"])
    operations = requestDict["Operations"]
    for operation in operations:
        assert operation["Type"] == "RemoveFile"
        assert len(operation["Files"]) == 1
        assert operation["Files"][0]["LFN"] in failedInputDataList


def test_removeInputData_errorRemoval(mocker, rid):
    """Test Test RemoveInputData when the removal of input data returns an error."""
    rid.inputDataList = [
        "/lhcb/data/2010/EW.DST/00008380/0000/00008380_00000287_1.ew.dst",
        "/lhcb/data/2010/EW.DST/00008380/0000/00008380_00000281_1.ew.dst",
        "/lhcb/data/2011/EW.DST/00008380/0000/00008380_00000281_1.ew.dst",
    ]

    mocker.patch("DIRAC.DataManagementSystem.Client.DataManager.DataManager.removeFile", return_value=S_ERROR("Error"))
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.ModuleBase.setApplicationStatus")

    assert rid.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=rid.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"], "Execution should succeed."

    rid.dataManager.removeFile.assert_called_once()
    args, _ = rid.dataManager.removeFile.call_args
    assert args[0] == rid.inputDataList

    assert not rid.request.isEmpty()

    requestDict = json.loads(rid.request.toJSON()["Value"])
    operations = requestDict["Operations"]
    for operation in operations:
        assert operation["Type"] == "RemoveFile"
        assert len(operation["Files"]) == 1
        assert operation["Files"][0]["LFN"] in rid.inputDataList


def test_removeInputData_previousError_fail(mocker, rid):
    """Test RemoveInputData with an intentional failure from a previous step."""
    mocker.patch("DIRAC.DataManagementSystem.Client.DataManager.DataManager.removeFile")
    assert rid.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=rid.step_commons,
        step_number=step_number,
        step_id=step_id,
        # Intentional error
        stepStatus=S_ERROR(),
    )["OK"]

    rid.dataManager.removeFile.assert_not_called()
    assert rid.request.isEmpty()
