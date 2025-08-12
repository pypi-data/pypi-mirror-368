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
"""Unit tests for Workflow Module FailoverRequest."""

import json
from pathlib import Path
import pytest

from DIRAC import S_OK, S_ERROR
from DIRAC.RequestManagementSystem.Client.Request import Request
from DIRAC.TransformationSystem.Client.FileReport import FileReport
from DIRAC.WorkloadManagementSystem.Client.JobReport import JobReport

from LHCbDIRAC.Workflow.Modules.FailoverRequest import FailoverRequest
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
REQUEST_JSON = f"{prod_id}_{prod_job_id}_request.json"


@pytest.fixture
def fr(mocker):
    """Fixture for FailoverRequest module."""
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator")
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.ModuleBase._resolveInputVariables")
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.ModuleBase._resolveInputStep")

    fr = FailoverRequest()
    fr.fileReport = FileReport()
    fr.jobReport = JobReport(wms_job_id)
    fr.request = Request()

    yield fr

    Path(REQUEST_JSON).unlink(missing_ok=True)


# Test Scenarios
def test_failoverRequest_success(mocker, fr):
    """Test successful execution of FailoverRequest module."""
    problematicFiles = [
        "/lhcb/data/2010/EW.DST/00008380/0000/00008380_00000287_1.ew.dst",
    ]
    mocker.patch("DIRAC.TransformationSystem.Client.FileReport.FileReport.getFiles", side_effect=[problematicFiles, []])
    mocker.patch("DIRAC.TransformationSystem.Client.FileReport.FileReport.commit", return_value=S_OK("Anything"))
    mocker.patch.object(fr.fileReport, "setFileStatus")
    mocker.patch.object(fr.jobReport, "setApplicationStatus")

    fr.inputDataList = [
        "/lhcb/data/2010/EW.DST/00008380/0000/00008380_00000281_1.ew.dst",
        "/lhcb/data/2011/EW.DST/00008380/0000/00008380_00000281_1.ew.dst",
    ] + problematicFiles

    # Execute the module
    assert fr.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=fr.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"], "Execution should succeed."

    # Check the FileReport calls: the problematic file should not appear
    # The input files should be set to "Processed"
    assert fr.fileReport.setFileStatus.call_count == 2
    args = fr.fileReport.setFileStatus.call_args_list
    assert args[0][0][0] == int(prod_id)
    assert args[0][0][1] == fr.inputDataList[0]
    assert args[0][0][2] == "Processed"

    assert args[1][0][0] == int(prod_id)
    assert args[1][0][1] == fr.inputDataList[1]
    assert args[1][0][2] == "Processed"

    # Make sure the appliction is successfully finished
    assert fr.jobReport.setApplicationStatus.call_count == 1
    assert fr.jobReport.setApplicationStatus.call_args[0][0] == "Job Finished Successfully"

    # Make sure the forward DISET is not generated
    requestDict = json.loads(fr.request.toJSON()["Value"])
    operations = requestDict["Operations"]
    assert len(operations) == 0

    # Make sure the request json does not exists
    assert not Path(REQUEST_JSON).exists()


def test_failoverRequest_commitFailure1(mocker, fr):
    """Test execution of FailoverRequest module when the fileReport.commit() fails:
    In this context, the second call to commit() will work, so the request should not be generated.
    """
    problematicFiles = [
        "/lhcb/data/2010/EW.DST/00008380/0000/00008380_00000287_1.ew.dst",
    ]
    # Both calla to getFiles() will return the problematic files because the commit did not work
    mocker.patch(
        "DIRAC.TransformationSystem.Client.FileReport.FileReport.getFiles",
        side_effect=[problematicFiles, problematicFiles],
    )
    mocker.patch(
        "DIRAC.TransformationSystem.Client.FileReport.FileReport.commit", side_effect=[S_ERROR("Error"), S_OK(None)]
    )
    mocker.patch.object(fr.fileReport, "setFileStatus")
    mocker.patch.object(fr.jobReport, "setApplicationStatus")

    fr.inputDataList = [
        "/lhcb/data/2010/EW.DST/00008380/0000/00008380_00000281_1.ew.dst",
        "/lhcb/data/2011/EW.DST/00008380/0000/00008380_00000281_1.ew.dst",
    ] + problematicFiles

    # Execute the module
    assert fr.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=fr.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"], "Execution should succeed."

    # Check the FileReport calls: the problematic file should not appear
    # The input files should be set to "Processed"
    assert fr.fileReport.setFileStatus.call_count == 2
    args = fr.fileReport.setFileStatus.call_args_list
    assert args[0][0][0] == int(prod_id)
    assert args[0][0][1] == fr.inputDataList[0]
    assert args[0][0][2] == "Processed"

    assert args[1][0][0] == int(prod_id)
    assert args[1][0][1] == fr.inputDataList[1]
    assert args[1][0][2] == "Processed"

    # Make sure the appliction is successfully finished
    assert fr.jobReport.setApplicationStatus.call_count == 1
    assert fr.jobReport.setApplicationStatus.call_args[0][0] == "Job Finished Successfully"

    # Make sure the forward DISET is generated
    requestDict = json.loads(fr.request.toJSON()["Value"])
    operations = requestDict["Operations"]
    assert len(operations) == 0

    # Make sure the request json does not exists
    assert not Path(REQUEST_JSON).exists()


def test_failoverRequest_commitFailure2(mocker, fr):
    """Test execution of FailoverRequest module when the fileReport.commit() fails:
    In this context, the second call to commit() will fail, so the request should be generated.
    """
    problematicFiles = [
        "/lhcb/data/2010/EW.DST/00008380/0000/00008380_00000287_1.ew.dst",
    ]
    # Both calla to getFiles() will return the problematic files because the commit did not work
    mocker.patch(
        "DIRAC.TransformationSystem.Client.FileReport.FileReport.getFiles",
        side_effect=[problematicFiles, problematicFiles],
    )
    mocker.patch(
        "DIRAC.TransformationSystem.Client.FileReport.FileReport.commit",
        side_effect=[S_ERROR("Error"), S_ERROR("Error")],
    )
    mocker.patch.object(fr.fileReport, "setFileStatus")
    mocker.patch.object(fr.jobReport, "setApplicationStatus")

    fr.inputDataList = [
        "/lhcb/data/2010/EW.DST/00008380/0000/00008380_00000281_1.ew.dst",
        "/lhcb/data/2011/EW.DST/00008380/0000/00008380_00000281_1.ew.dst",
    ] + problematicFiles

    # Execute the module
    assert fr.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=fr.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"], "Execution should succeed."

    # Check the FileReport calls: the problematic file should not appear
    # The input files should be set to "Processed"
    assert fr.fileReport.setFileStatus.call_count == 2
    args = fr.fileReport.setFileStatus.call_args_list
    assert args[0][0][0] == int(prod_id)
    assert args[0][0][1] == fr.inputDataList[0]
    assert args[0][0][2] == "Processed"

    assert args[1][0][0] == int(prod_id)
    assert args[1][0][1] == fr.inputDataList[1]
    assert args[1][0][2] == "Processed"

    # Make sure the appliction is successfully finished
    assert fr.jobReport.setApplicationStatus.call_count == 1
    assert fr.jobReport.setApplicationStatus.call_args[0][0] == "Job Finished Successfully"

    # Make sure the forward DISET is generated
    requestDict = json.loads(fr.request.toJSON()["Value"])
    operations = requestDict["Operations"]

    assert len(operations) == 1
    assert operations[0]["Type"] == "SetFileStatus"

    # Make sure the request json does not exists
    assert Path(REQUEST_JSON).exists()


def test_failoverRequest_previousError_fail(mocker, fr):
    """Test FailoverRequest with an intentional failure."""
    problematicFiles = [
        "/lhcb/data/2010/EW.DST/00008380/0000/00008380_00000287_1.ew.dst",
    ]
    mocker.patch("DIRAC.TransformationSystem.Client.FileReport.FileReport.getFiles", side_effect=[problematicFiles, []])
    mocker.patch("DIRAC.TransformationSystem.Client.FileReport.FileReport.commit", return_value=S_OK("Anything"))
    mocker.patch.object(fr.fileReport, "setFileStatus")
    mocker.patch.object(fr.jobReport, "setApplicationStatus")

    fr.inputDataList = [
        "/lhcb/data/2010/EW.DST/00008380/0000/00008380_00000281_1.ew.dst",
        "/lhcb/data/2011/EW.DST/00008380/0000/00008380_00000281_1.ew.dst",
    ] + problematicFiles

    # Execute the module
    assert fr.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=fr.step_commons,
        step_number=step_number,
        step_id=step_id,
        # Intentional error
        stepStatus=S_ERROR(),
    )["OK"], "Execution should succeed."

    # Check the FileReport calls: the problematic file should not appear
    # The input files should be set to "Unused"
    assert fr.fileReport.setFileStatus.call_count == 2
    args = fr.fileReport.setFileStatus.call_args_list
    assert args[0][0][0] == int(prod_id)
    assert args[0][0][1] == fr.inputDataList[0]
    assert args[0][0][2] == "Unused"

    assert args[1][0][0] == int(prod_id)
    assert args[1][0][1] == fr.inputDataList[1]
    assert args[1][0][2] == "Unused"

    # Make sure the appliction is not reported as a success
    assert fr.jobReport.setApplicationStatus.call_count == 0

    # Make sure the forward DISET is not generated
    requestDict = json.loads(fr.request.toJSON()["Value"])
    operations = requestDict["Operations"]
    assert len(operations) == 0

    # Make sure the request json does not exists
    assert not Path(REQUEST_JSON).exists()
