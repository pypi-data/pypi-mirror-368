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
"""Unit tests for Workflow Module UserJobFinalization."""

import json
from pathlib import Path
import pytest

from DIRAC import S_OK, S_ERROR
from DIRAC.DataManagementSystem.Client.FailoverTransfer import FailoverTransfer
from DIRAC.RequestManagementSystem.Client.Request import Request
from DIRAC.WorkloadManagementSystem.Client.JobReport import JobReport
from LHCbDIRAC.Workflow.Modules.UserJobFinalization import UserJobFinalization
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
ROOT_FILE = "LcstDs_2018Down_alltriggerfilter.root"
DISABLE_WATCHDOG_FILE = "DISABLE_WATCHDOG_CPU_WALLCLOCK_CHECK"
REQUEST_JSON = f"{prod_id}_{prod_job_id}_request.json"


@pytest.fixture
def ujf(mocker):
    """Fixture for UserJobFinalization module."""

    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator")
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.ModuleBase._resolveInputVariables")
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.ModuleBase._getCurrentOwner", return_value="user")
    mocker.patch("LHCbDIRAC.Workflow.Modules.UserJobFinalization.getDestinationSEList", return_value=["CERN", "CNAF"])

    ujf = UserJobFinalization()
    ujf.request = Request()
    ujf.failoverTransfer = FailoverTransfer(ujf.request)
    ujf.jobReport = JobReport(wms_job_id)

    if "ReplicateUserOutputData" in wf_commons[0]:
        wf_commons[0].pop("ReplicateUserOutputData")

    mocker.patch.object(ujf.jobReport, "setJobParameter", return_value=S_OK())
    mocker.patch.object(ujf.jobReport, "setApplicationStatus", return_value=S_OK())

    yield ujf

    Path(ROOT_FILE).unlink(missing_ok=True)
    Path(DISABLE_WATCHDOG_FILE).unlink(missing_ok=True)
    Path(REQUEST_JSON).unlink(missing_ok=True)


# Test Scenarios
def test_userJobFinalization_success(mocker, ujf):
    """Test successful execution of UserJobFinalization module:
    1 output file, 2 SEs: the file should be uploaded to the first SE.
    """
    mocker.patch.object(
        ujf.failoverTransfer, "transferAndRegisterFile", return_value=S_OK({"uploadedSE": "CERN", "lfn": ROOT_FILE})
    )
    mocker.patch.object(ujf.failoverTransfer, "transferAndRegisterFileFailover")

    # Set the output data
    wf_commons[0]["UserOutputData"] = ["*.root"]
    with open(ROOT_FILE, "w") as f:
        f.write("Any root content")

    # Execute the module
    result = ujf.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=ujf.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )
    assert result["OK"], "Execution should succeed."
    assert result["Value"] == "Output data uploaded"

    assert ujf.userOutputData == [ROOT_FILE], "Output data should be set."
    # There should be 1 upload, and 0 failover request
    assert ujf.failoverTransfer.transferAndRegisterFile.call_count == 1
    assert ujf.failoverTransfer.transferAndRegisterFileFailover.call_count == 0

    assert ujf.jobReport.setApplicationStatus.call_count == 1
    assert ujf.jobReport.setApplicationStatus.call_args[0][0] == "Job Finished Successfully"

    assert ujf.jobReport.setJobParameter.call_count == 1
    assert ujf.jobReport.setJobParameter.call_args[0][0] == "UploadedOutputData"
    assert ROOT_FILE in ujf.jobReport.setJobParameter.call_args[0][1]

    # Make sure the forward DISET is not generated
    requestDict = json.loads(ujf.request.toJSON()["Value"])
    operations = requestDict["Operations"]
    assert len(operations) == 0

    assert not Path(REQUEST_JSON).exists()


def test_userJobFinalization_successWithReplicate(mocker, ujf):
    """Test successful execution of UserJobFinalization module:
    1 output file, 2 SEs: the file should be uploaded to both SEs because replicate are enabled.
    """
    mocker.patch.object(
        ujf.failoverTransfer, "transferAndRegisterFile", return_value=S_OK({"uploadedSE": "CERN", "lfn": ROOT_FILE})
    )
    mocker.patch.object(ujf.failoverTransfer, "transferAndRegisterFileFailover")

    # Set the output data
    wf_commons[0]["UserOutputData"] = ["*.root"]
    with open(ROOT_FILE, "w") as f:
        f.write("Any root content")

    # Replicate is enabled
    wf_commons[0]["ReplicateUserOutputData"] = True

    # Execute the module
    result = ujf.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=ujf.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )
    assert result["OK"], "Execution should succeed."
    assert result["Value"] == "Output data uploaded"

    assert ujf.userOutputData == [ROOT_FILE], "Output data should be set."
    # There should be 1 upload, and 0 failover request
    assert ujf.failoverTransfer.transferAndRegisterFile.call_count == 1
    assert ujf.failoverTransfer.transferAndRegisterFileFailover.call_count == 0

    assert ujf.jobReport.setApplicationStatus.call_count == 1
    assert ujf.jobReport.setApplicationStatus.call_args[0][0] == "Job Finished Successfully"

    assert ujf.jobReport.setJobParameter.call_count == 1
    assert ujf.jobReport.setJobParameter.call_args[0][0] == "UploadedOutputData"
    assert ROOT_FILE in ujf.jobReport.setJobParameter.call_args[0][1]

    # Make sure the forward DISET is generated and contains the replicate operation from CERN to CNAF
    requestDict = json.loads(ujf.request.toJSON()["Value"])
    operations = requestDict["Operations"]
    assert len(operations) == 1
    assert operations[0]["Type"] == "ReplicateAndRegister"
    assert operations[0]["TargetSE"] == "CNAF"
    assert operations[0]["SourceSE"] == "CERN"
    assert ROOT_FILE in operations[0]["Files"][0]["LFN"]

    assert Path(REQUEST_JSON).exists()


def test_userJobFinalization_failUpload(mocker, ujf):
    """Test successful execution of UserJobFinalization module:
    1 output file, 2 SEs: the upload to the first SE should fail. A 2nd upload should succeed.
    """
    mocker.patch.object(ujf.failoverTransfer, "transferAndRegisterFile", return_value=S_ERROR("Error"))
    mocker.patch.object(ujf.failoverTransfer, "transferAndRegisterFileFailover", return_value=S_OK())

    # Set the output data
    wf_commons[0]["UserOutputData"] = ["*.root"]
    with open(ROOT_FILE, "w") as f:
        f.write("Any root content")

    # Replicate is enabled
    wf_commons[0]["ReplicateUserOutputData"] = True

    # Execute the module
    result = ujf.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=ujf.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )
    assert result["OK"], "Execution should succeed."
    assert result["Value"] == "Output data uploaded"

    assert ujf.userOutputData == [ROOT_FILE], "Output data should be set."
    # There should be 1 failed upload, and therefore 1 failover request
    assert ujf.failoverTransfer.transferAndRegisterFile.call_count == 1
    assert ujf.failoverTransfer.transferAndRegisterFileFailover.call_count == 1

    assert ujf.jobReport.setApplicationStatus.call_count == 1
    assert ujf.jobReport.setApplicationStatus.call_args[0][0] == "Job Finished Successfully"

    assert ujf.jobReport.setJobParameter.call_count == 1
    assert ujf.jobReport.setJobParameter.call_args[0][0] == "UploadedOutputData"
    assert ROOT_FILE in ujf.jobReport.setJobParameter.call_args[0][1]

    # Make sure the forward DISET is not generated
    requestDict = json.loads(ujf.request.toJSON()["Value"])
    operations = requestDict["Operations"]
    assert len(operations) == 1

    assert operations[0]["Type"] == "ReplicateAndRegister"
    assert operations[0]["TargetSE"] in ["CNAF", "CERN"]  # This is random
    assert operations[0]["SourceSE"] in ["CNAF", "CERN"]  # This is random
    assert ROOT_FILE in operations[0]["Files"][0]["LFN"]

    assert Path(REQUEST_JSON).exists()


def test_userJobFinalization_failUpload2(mocker, ujf):
    """Test successful execution of UserJobFinalization module:
    1 output file, 2 SEs: the uploads should all fail. A request should be generated for the failover.
    """
    mocker.patch.object(ujf.failoverTransfer, "transferAndRegisterFile", return_value=S_ERROR("Error"))
    mocker.patch.object(ujf.failoverTransfer, "transferAndRegisterFileFailover", return_value=S_ERROR("Error"))

    # Set the output data
    wf_commons[0]["UserOutputData"] = ["*.root"]
    with open(ROOT_FILE, "w") as f:
        f.write("Any root content")

    # Replicate is enabled
    wf_commons[0]["ReplicateUserOutputData"] = True

    # Execute the module
    result = ujf.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=ujf.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )
    assert not result["OK"], "Execution should succeed."
    assert result["Message"] == "Failed To Upload Output Data"

    assert ujf.userOutputData == [ROOT_FILE], "Output data should be set."
    # There should be 1 failed upload, and therefore 1 failover request
    assert ujf.failoverTransfer.transferAndRegisterFile.call_count == 1
    assert ujf.failoverTransfer.transferAndRegisterFileFailover.call_count == 1

    assert ujf.jobReport.setApplicationStatus.call_count == 0
    assert ujf.jobReport.setJobParameter.call_count == 0

    # Make sure the forward DISET is not generated
    requestDict = json.loads(ujf.request.toJSON()["Value"])
    operations = requestDict["Operations"]
    assert len(operations) == 0

    assert not Path(REQUEST_JSON).exists()


def test_userJobFinalization_noOutput(mocker, ujf):
    """Test UserJobFinalization with no output data."""
    mocker.patch.object(
        ujf.failoverTransfer, "transferAndRegisterFile", return_value=S_OK({"uploadedSE": "CERN", "lfn": ROOT_FILE})
    )
    mocker.patch.object(ujf.failoverTransfer, "transferAndRegisterFileFailover")

    # Empty output data
    wf_commons[0]["UserOutputData"] = []

    # Execute the module
    result = ujf.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=ujf.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )

    assert result["OK"], "Execution should succeed."
    assert result["Value"] == "No output data to upload"

    assert ujf.userOutputData == [], "Output data should be set."
    assert ujf.failoverTransfer.transferAndRegisterFile.call_count == 0
    assert ujf.failoverTransfer.transferAndRegisterFileFailover.call_count == 0

    assert ujf.jobReport.setApplicationStatus.call_count == 0
    assert ujf.jobReport.setJobParameter.call_count == 0

    assert not Path(REQUEST_JSON).exists()


def test_userJobFinalization_outputNotFound(mocker, ujf):
    """Test UserJobFinalization with output data not found."""
    mocker.patch.object(
        ujf.failoverTransfer, "transferAndRegisterFile", return_value=S_OK({"uploadedSE": "CERN", "lfn": ROOT_FILE})
    )
    mocker.patch.object(ujf.failoverTransfer, "transferAndRegisterFileFailover")

    # Set the output data: there is no such file
    wf_commons[0]["UserOutputData"] = ["*.root"]

    # Execute the module
    result = ujf.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=ujf.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )
    assert result["OK"], "Execution should succeed."

    assert ujf.userOutputData == [], "Output data should not be set."
    # There should be 0 upload, and 0 failover request
    assert ujf.failoverTransfer.transferAndRegisterFile.call_count == 0
    assert ujf.failoverTransfer.transferAndRegisterFileFailover.call_count == 0

    assert ujf.jobReport.setApplicationStatus.call_count == 1
    assert ujf.jobReport.setApplicationStatus.call_args[0][0] == "No Output Data Files To Upload"

    assert ujf.jobReport.setJobParameter.call_count == 0

    # Make sure the forward DISET is generated and contains the replicate operation from CERN to CNAF
    requestDict = json.loads(ujf.request.toJSON()["Value"])
    operations = requestDict["Operations"]
    assert len(operations) == 0

    assert not Path(REQUEST_JSON).exists()


def test_userJobFinalization_previousError_fail(mocker, ujf):
    """Test UserJobFinalization with an intentional failure."""
    mocker.patch.object(
        ujf.failoverTransfer, "transferAndRegisterFile", return_value=S_OK({"uploadedSE": "CERN", "lfn": ROOT_FILE})
    )
    mocker.patch.object(ujf.failoverTransfer, "transferAndRegisterFileFailover")

    result = ujf.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=ujf.step_commons,
        step_number=step_number,
        step_id=step_id,
        # Intentional error
        stepStatus=S_ERROR(),
    )

    assert result["OK"], "Execution should succeed."

    assert ujf.userOutputData == [], "Output data should not be set."
    # There should be 0 upload, and 0 failover request
    assert ujf.failoverTransfer.transferAndRegisterFile.call_count == 0
    assert ujf.failoverTransfer.transferAndRegisterFileFailover.call_count == 0

    assert ujf.jobReport.setApplicationStatus.call_count == 0
    assert ujf.jobReport.setJobParameter.call_count == 0

    # Make sure the forward DISET is generated and contains the replicate operation from CERN to CNAF
    requestDict = json.loads(ujf.request.toJSON()["Value"])
    operations = requestDict["Operations"]
    assert len(operations) == 0

    assert not Path(REQUEST_JSON).exists()
