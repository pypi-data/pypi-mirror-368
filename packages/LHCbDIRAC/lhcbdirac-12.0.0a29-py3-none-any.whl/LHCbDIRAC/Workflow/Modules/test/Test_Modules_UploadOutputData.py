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
"""Unit tests for Workflow Module UploadOutputData."""
# pylint: disable=protected-access, missing-docstring
import json
from pathlib import Path
import pytest

from DIRAC import S_OK, S_ERROR
from DIRAC.DataManagementSystem.Client.FailoverTransfer import FailoverTransfer
from DIRAC.RequestManagementSystem.Client.File import File
from DIRAC.RequestManagementSystem.Client.Operation import Operation
from DIRAC.RequestManagementSystem.Client.Request import Request
from DIRAC.TransformationSystem.Client.FileReport import FileReport
from DIRAC.WorkloadManagementSystem.Client.JobReport import JobReport
from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

from LHCbDIRAC.Workflow.Modules.test.mock_Commons import (
    prod_id,
    prod_job_id,
    wms_job_id,
    workflowStatus,
    step_id,
    step_number,
    wf_commons,
)

from LHCbDIRAC.Workflow.Modules.UploadOutputData import UploadOutputData


# Helper Functions
SIM_FILE = "00211518_00024457_1.sim"
BK_FILE = "bookkeeping_00211518_00024457_1.xml"
DISABLE_WATCHDOG_FILE = "DISABLE_WATCHDOG_CPU_WALLCLOCK_CHECK"


@pytest.fixture
def upod(mocker):
    """Fixture for UploadOutputData module."""
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator")
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.ModuleBase._resolveInputVariables")
    mocker.patch("LHCbDIRAC.Workflow.Modules.UploadOutputData.getDestinationSEList", return_value=["CERN", "CNAF"])

    # Mock FileCatalog
    mocker.patch("DIRAC.Resources.Catalog.FileCatalog.FileCatalog.__init__", return_value=None)
    mocker.patch("DIRAC.Resources.Catalog.FileCatalog.FileCatalog.__getattr__", return_value=lambda x: S_OK({}))

    if "ProductionOutputData" in wf_commons[0]:
        wf_commons[0].pop("ProductionOutputData")

    upod = UploadOutputData()
    upod.request = Request()
    upod.failoverTransfer = FailoverTransfer(upod.request)
    upod.jobReport = JobReport(wms_job_id)
    upod.bkClient = BookkeepingClient()
    upod.fileReport = FileReport()

    mocker.patch.object(upod.bkClient, "sendXMLBookkeepingReport", return_value=S_OK())
    mocker.patch.object(upod.fileReport, "setFileStatus")
    mocker.patch.object(upod.jobReport, "setJobParameter")

    yield upod

    Path(SIM_FILE).unlink(missing_ok=True)
    Path(BK_FILE).unlink(missing_ok=True)
    Path(DISABLE_WATCHDOG_FILE).unlink(missing_ok=True)


# Test Scenarios
def test_uploadOutputData_success(mocker, upod):
    """Test successful execution of UploadOutputData module.
    * The output should be uploaded and registered in the bookkeeping system.
    * The bookkeeping report should be sent and the job parameter updated.
    """
    mocker.patch.object(
        upod.failoverTransfer, "transferAndRegisterFile", return_value=S_OK({"uploadedSE": "CERN", "lfn": SIM_FILE})
    )
    mocker.patch.object(upod.failoverTransfer, "transferAndRegisterFileFailover")

    wf_commons[0]["outputDataStep"] = "1"
    wf_commons[0]["outputList"] = [
        {"outputDataName": SIM_FILE, "outputDataType": "sim", "outputBKType": "SIM", "stepName": "Gauss_1"}
    ]
    upod.outputSEs = {
        "SIM": "Tier1-Buffer",
    }

    # Create output files
    with open(SIM_FILE, "w") as f:
        f.write("Sim file content")

    with open(BK_FILE, "w") as f:
        f.write("Bookkeeping file content")

    # Execute module
    result = upod.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=upod.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )

    assert result["OK"], "Execution should succeed."
    assert result["Value"] == "Output data uploaded"

    assert upod.fileReport.setFileStatus.call_count == 0
    assert upod.bkClient.sendXMLBookkeepingReport.call_count == 1

    assert upod.failoverTransfer.transferAndRegisterFile.call_count == 1
    assert upod.failoverTransfer.transferAndRegisterFile.call_args[1]["fileName"] == SIM_FILE

    assert upod.failoverTransfer.transferAndRegisterFileFailover.call_count == 0

    assert upod.jobReport.setJobParameter.call_count == 1
    assert upod.jobReport.setJobParameter.call_args[0][0] == "UploadedOutputData"
    assert upod.jobReport.setJobParameter.call_args[0][1] == SIM_FILE

    # Make sure the forward DISET is not generated
    requestDict = json.loads(upod.request.toJSON()["Value"])
    operations = requestDict["Operations"]
    assert len(operations) == 0


def test_uploadOutputData_failedBKRegistration(mocker, upod):
    """Test execution of UploadOutputData module when the BK registation fails.
    * The output should be uploaded but not registered in the bookkeeping system now.
    """
    mocker.patch.object(
        upod.failoverTransfer, "transferAndRegisterFile", return_value=S_OK({"uploadedSE": "CERN", "lfn": SIM_FILE})
    )
    mocker.patch.object(upod.failoverTransfer, "transferAndRegisterFileFailover")
    # BK registration failure
    mocker.patch(
        "DIRAC.Resources.Catalog.FileCatalog.FileCatalog.__getattr__",
        return_value=lambda x: S_OK(
            {
                "Failed": {
                    f"/lhcb/{wf_commons[0]['configName']}/{wf_commons[0]['configVersion']}/"
                    f"SIM/00000{prod_id}/0000/{SIM_FILE}": "error"
                }
            }
        ),
    )

    wf_commons[0]["outputDataStep"] = "1"
    wf_commons[0]["outputList"] = [
        {"outputDataName": SIM_FILE, "outputDataType": "sim", "outputBKType": "SIM", "stepName": "Gauss_1"}
    ]
    upod.outputSEs = {
        "SIM": "Tier1-Buffer",
    }

    # Create output files
    with open(SIM_FILE, "w") as f:
        f.write("Sim file content")

    with open(BK_FILE, "w") as f:
        f.write("Bookkeeping file content")

    # Execute module
    result = upod.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=upod.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )

    assert result["OK"], "Execution should succeed."
    assert result["Value"] == "Output data uploaded"

    assert upod.fileReport.setFileStatus.call_count == 0
    assert upod.bkClient.sendXMLBookkeepingReport.call_count == 1

    assert upod.failoverTransfer.transferAndRegisterFile.call_count == 1
    assert upod.failoverTransfer.transferAndRegisterFile.call_args[1]["fileName"] == SIM_FILE

    assert upod.failoverTransfer.transferAndRegisterFileFailover.call_count == 0

    assert upod.jobReport.setJobParameter.call_count == 1
    assert upod.jobReport.setJobParameter.call_args[0][0] == "UploadedOutputData"
    assert upod.jobReport.setJobParameter.call_args[0][1] == SIM_FILE

    # Make sure the request is generated
    requestDict = json.loads(upod.request.toJSON()["Value"])
    operations = requestDict["Operations"]
    assert len(operations) == 1

    assert operations[0]["Type"] == "RegisterFile"
    assert operations[0]["Catalog"] == "BookkeepingDB"
    assert SIM_FILE in operations[0]["Files"][0]["LFN"]


def test_uploadOutputData_postponeBKRegistration(mocker, upod):
    """Test execution of UploadOutputData module when there is already a RegisterFile operation on the output.
    * The output should be uploaded but not registered in the bookkeeping system now.
    """
    mocker.patch.object(
        upod.failoverTransfer, "transferAndRegisterFile", return_value=S_OK({"uploadedSE": "CERN", "lfn": SIM_FILE})
    )
    mocker.patch.object(upod.failoverTransfer, "transferAndRegisterFileFailover")

    wf_commons[0]["outputDataStep"] = "1"
    wf_commons[0]["outputList"] = [
        {"outputDataName": SIM_FILE, "outputDataType": "sim", "outputBKType": "SIM", "stepName": "Gauss_1"}
    ]
    upod.outputSEs = {
        "SIM": "Tier1-Buffer",
    }

    # Create output files
    with open(SIM_FILE, "w") as f:
        f.write("Sim file content")

    with open(BK_FILE, "w") as f:
        f.write("Bookkeeping file content")

    # Mock a previous failover request: the BK registration should be postponed and added to the request
    file1 = File()
    file1.LFN = (
        f"/lhcb/{wf_commons[0]['configName']}/{wf_commons[0]['configVersion']}/SIM/00000{prod_id}/0000/{SIM_FILE}"
    )

    o1 = Operation()
    o1.Type = "RegisterFile"
    o1.addFile(file1)

    upod.request.addOperation(o1)

    # Execute module
    result = upod.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=upod.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )

    assert result["OK"], "Execution should succeed."
    assert result["Value"] == "Output data uploaded"

    assert upod.fileReport.setFileStatus.call_count == 0
    assert upod.bkClient.sendXMLBookkeepingReport.call_count == 1

    assert upod.failoverTransfer.transferAndRegisterFile.call_count == 1
    assert upod.failoverTransfer.transferAndRegisterFile.call_args[1]["fileName"] == SIM_FILE

    assert upod.failoverTransfer.transferAndRegisterFileFailover.call_count == 0

    assert upod.jobReport.setJobParameter.call_count == 1
    assert upod.jobReport.setJobParameter.call_args[0][0] == "UploadedOutputData"
    assert upod.jobReport.setJobParameter.call_args[0][1] == SIM_FILE

    # Make sure the request is generated
    requestDict = json.loads(upod.request.toJSON()["Value"])
    operations = requestDict["Operations"]
    assert len(operations) == 2

    assert operations[0]["Type"] == "RegisterFile"
    assert operations[0]["Catalog"] is None
    assert SIM_FILE in operations[0]["Files"][0]["LFN"]

    assert operations[1]["Type"] == "RegisterFile"
    assert operations[1]["Catalog"] == "BookkeepingDB"
    assert SIM_FILE in operations[1]["Files"][0]["LFN"]


def test_uploadOutputData_errorBKRegistration(mocker, upod):
    """Test execution of UploadOutputData module when an error occurs during the BK registation.
    * The output should be uploaded but not registered in the bookkeeping system at all.
    """
    mocker.patch.object(
        upod.failoverTransfer, "transferAndRegisterFile", return_value=S_OK({"uploadedSE": "CERN", "lfn": SIM_FILE})
    )
    mocker.patch.object(upod.failoverTransfer, "transferAndRegisterFileFailover")
    # BK registration failure
    mocker.patch(
        "DIRAC.Resources.Catalog.FileCatalog.FileCatalog.__getattr__",
        return_value=lambda x: S_ERROR("Error registering file"),
    )

    wf_commons[0]["outputDataStep"] = "1"
    wf_commons[0]["outputList"] = [
        {"outputDataName": SIM_FILE, "outputDataType": "sim", "outputBKType": "SIM", "stepName": "Gauss_1"}
    ]
    upod.outputSEs = {
        "SIM": "Tier1-Buffer",
    }

    # Create output files
    with open(SIM_FILE, "w") as f:
        f.write("Sim file content")

    with open(BK_FILE, "w") as f:
        f.write("Bookkeeping file content")

    # Execute module
    result = upod.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=upod.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )

    assert not result["OK"], "Execution should not succeed."
    assert result["Message"] == "Could Not Perform BK Registration"

    assert upod.fileReport.setFileStatus.call_count == 0
    assert upod.bkClient.sendXMLBookkeepingReport.call_count == 1

    assert upod.failoverTransfer.transferAndRegisterFile.call_count == 1
    assert upod.failoverTransfer.transferAndRegisterFile.call_args[1]["fileName"] == SIM_FILE

    assert upod.failoverTransfer.transferAndRegisterFileFailover.call_count == 0

    assert upod.jobReport.setJobParameter.call_count == 1
    assert upod.jobReport.setJobParameter.call_args[0][0] == "UploadedOutputData"
    assert upod.jobReport.setJobParameter.call_args[0][1] == SIM_FILE

    # Make sure the request is generated
    requestDict = json.loads(upod.request.toJSON()["Value"])
    operations = requestDict["Operations"]
    assert len(operations) == 0


def test_uploadOutputData_failUpload1(mocker, upod):
    """Test execution of UploadOutputData module when there is a 1st failure to upload outputs.
    * The output should be uploaded correctly with the second method.
    """
    mocker.patch.object(upod.failoverTransfer, "transferAndRegisterFile", return_value=S_ERROR("Error uploading file"))
    mocker.patch.object(upod.failoverTransfer, "transferAndRegisterFileFailover", return_value=S_OK())

    wf_commons[0]["outputDataStep"] = "1"
    wf_commons[0]["outputList"] = [
        {"outputDataName": SIM_FILE, "outputDataType": "sim", "outputBKType": "SIM", "stepName": "Gauss_1"}
    ]
    upod.outputSEs = {
        "SIM": "Tier1-Buffer",
    }

    # Create output files
    with open(SIM_FILE, "w") as f:
        f.write("Sim file content")

    with open(BK_FILE, "w") as f:
        f.write("Bookkeeping file content")

    # Execute module
    result = upod.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=upod.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )

    assert result["OK"], "Execution should succeed."
    assert result["Value"] == "Output data uploaded"

    assert upod.fileReport.setFileStatus.call_count == 0
    assert upod.bkClient.sendXMLBookkeepingReport.call_count == 1

    assert upod.failoverTransfer.transferAndRegisterFile.call_count == 1
    assert upod.failoverTransfer.transferAndRegisterFile.call_args[1]["fileName"] == SIM_FILE

    assert upod.failoverTransfer.transferAndRegisterFileFailover.call_count == 1
    assert upod.failoverTransfer.transferAndRegisterFileFailover.call_args[1]["fileName"] == SIM_FILE

    assert upod.jobReport.setJobParameter.call_count == 1
    assert upod.jobReport.setJobParameter.call_args[0][0] == "UploadedOutputData"
    assert upod.jobReport.setJobParameter.call_args[0][1] == SIM_FILE

    # Make sure the request is not generated
    requestDict = json.loads(upod.request.toJSON()["Value"])
    operations = requestDict["Operations"]
    assert len(operations) == 0


def test_uploadOutputData_failUpload2(mocker, upod):
    """Test execution of UploadOutputData module when there is a 2 failures to upload outputs.
    * A request should be generated to upload outputs later.
    """
    mocker.patch.object(upod.failoverTransfer, "transferAndRegisterFile", return_value=S_ERROR("Error uploading file"))
    mocker.patch.object(
        upod.failoverTransfer, "transferAndRegisterFileFailover", return_value=S_ERROR("Error uploading file")
    )

    wf_commons[0]["outputDataStep"] = "1"
    wf_commons[0]["outputList"] = [
        {"outputDataName": SIM_FILE, "outputDataType": "sim", "outputBKType": "SIM", "stepName": "Gauss_1"}
    ]
    upod.outputSEs = {
        "SIM": "Tier1-Buffer",
    }

    # Create output files
    with open(SIM_FILE, "w") as f:
        f.write("Sim file content")

    with open(BK_FILE, "w") as f:
        f.write("Bookkeeping file content")

    # Mock a previous failover request:
    # Add the end of the execution, o1 should be removed
    file1 = File()
    file1.LFN = (
        f"/lhcb/{wf_commons[0]['configName']}/{wf_commons[0]['configVersion']}/SIM/00000{prod_id}/0000/{SIM_FILE}"
    )
    file2 = File()
    file2.LFN = "/another/file.txt"

    o1 = Operation()
    o1.Type = "RegisterFile"
    o1.addFile(file1)
    o2 = Operation()
    o2.Type = "RegisterFile"
    o2.addFile(file2)

    upod.request.addOperation(o1)
    upod.request.addOperation(o2)

    # Execute module
    result = upod.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=upod.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )

    assert not result["OK"], "Execution should not succeed."
    assert result["Message"] == "Failed to upload output data"

    assert upod.fileReport.setFileStatus.call_count == 0
    assert upod.bkClient.sendXMLBookkeepingReport.call_count == 1

    assert upod.failoverTransfer.transferAndRegisterFile.call_count == 1
    assert upod.failoverTransfer.transferAndRegisterFile.call_args[1]["fileName"] == SIM_FILE

    assert upod.failoverTransfer.transferAndRegisterFileFailover.call_count == 1
    assert upod.failoverTransfer.transferAndRegisterFileFailover.call_args[1]["fileName"] == SIM_FILE

    assert upod.jobReport.setJobParameter.call_count == 0

    # Make sure the request is generated
    requestDict = json.loads(upod.request.toJSON()["Value"])
    operations = requestDict["Operations"]
    assert len(operations) == 2

    assert operations[0]["Type"] == "RegisterFile"
    assert operations[0]["TargetSE"] is None
    assert operations[0]["SourceSE"] is None
    assert SIM_FILE not in operations[0]["Files"][0]["LFN"]

    assert operations[1]["Type"] == "RemoveFile"
    assert operations[1]["TargetSE"] is None
    assert operations[1]["SourceSE"] is None
    assert SIM_FILE in operations[1]["Files"][0]["LFN"]


def test_uploadOutputData_BKReportError(mocker, upod):
    """Test execution of UploadOutputData module when the BK report cannot be sent.
    * The output should be uploaded and registered in the bookkeeping system.
    * The bookkeeping report should be added to a failover request.
    """
    mocker.patch.object(
        upod.failoverTransfer, "transferAndRegisterFile", return_value=S_OK({"uploadedSE": "CERN", "lfn": SIM_FILE})
    )
    mocker.patch.object(upod.failoverTransfer, "transferAndRegisterFileFailover")

    wf_commons[0]["outputDataStep"] = "1"
    wf_commons[0]["outputList"] = [
        {"outputDataName": SIM_FILE, "outputDataType": "sim", "outputBKType": "SIM", "stepName": "Gauss_1"}
    ]
    upod.outputSEs = {
        "SIM": "Tier1-Buffer",
    }

    # Create output files
    with open(SIM_FILE, "w") as f:
        f.write("Sim file content")

    with open(BK_FILE, "w") as f:
        f.write("Bookkeeping file content")

    # Mock the sendXMLBookkeepingReport method
    mocker.patch.object(
        upod.bkClient,
        "sendXMLBookkeepingReport",
        return_value={"OK": False, "rpcStub": "Error", "Message": "Error sending BK report"},
    )

    # Execute module
    result = upod.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=upod.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )

    assert result["OK"], "Execution should succeed."
    assert result["Value"] == "Output data uploaded"

    assert upod.fileReport.setFileStatus.call_count == 0
    assert upod.bkClient.sendXMLBookkeepingReport.call_count == 1

    assert upod.failoverTransfer.transferAndRegisterFile.call_count == 1
    assert upod.failoverTransfer.transferAndRegisterFile.call_args[1]["fileName"] == SIM_FILE

    assert upod.failoverTransfer.transferAndRegisterFileFailover.call_count == 0

    assert upod.jobReport.setJobParameter.call_count == 1
    assert upod.jobReport.setJobParameter.call_args[0][0] == "UploadedOutputData"
    assert upod.jobReport.setJobParameter.call_args[0][1] == SIM_FILE

    # Make sure the request is not generated
    requestDict = json.loads(upod.request.toJSON()["Value"])
    operations = requestDict["Operations"]
    assert len(operations) == 1

    assert operations[0]["Type"] == "ForwardDISET"


def test_uploadOutputData_withDescendents(mocker, upod):
    """Test execution of UploadOutputData module when there is already file descendants.
    It means that the input data has already been processed.
    * The output should not be uploaded and registered in the bookkeeping system.
    * The bookkeeping report should not be sent.
    """
    mocker.patch.object(
        upod.failoverTransfer, "transferAndRegisterFile", return_value=S_OK({"uploadedSE": "CERN", "lfn": SIM_FILE})
    )
    mocker.patch.object(upod.failoverTransfer, "transferAndRegisterFileFailover")
    # Mock the getFileDescendants method
    mocker.patch(
        "LHCbDIRAC.Workflow.Modules.UploadOutputData.getFileDescendents", return_value=S_OK(["/path/to/other/file.txt"])
    )

    wf_commons[0]["outputDataStep"] = "1"
    wf_commons[0]["outputList"] = [
        {"outputDataName": SIM_FILE, "outputDataType": "sim", "outputBKType": "SIM", "stepName": "Gauss_1"}
    ]
    upod.outputSEs = {
        "SIM": "Tier1-Buffer",
    }

    # Mock input files
    upod.inputDataList = ["AnyInputFile1"]

    # Create output files
    with open(SIM_FILE, "w") as f:
        f.write("Sim file content")

    with open(BK_FILE, "w") as f:
        f.write("Bookkeeping file content")

    # Execute module
    result = upod.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=upod.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )

    assert not result["OK"], "Execution should not succeed."
    assert result["Message"] == "Input Data Already Processed"

    assert upod.fileReport.setFileStatus.call_count == 1
    assert upod.fileReport.setFileStatus.call_args[0][0] == int(prod_id)
    assert upod.bkClient.sendXMLBookkeepingReport.call_count == 0

    assert upod.failoverTransfer.transferAndRegisterFile.call_count == 0
    assert upod.failoverTransfer.transferAndRegisterFileFailover.call_count == 0

    assert upod.jobReport.setJobParameter.call_count == 0

    # Make sure the request is not generated
    requestDict = json.loads(upod.request.toJSON()["Value"])
    operations = requestDict["Operations"]
    assert len(operations) == 0


def test_uploadOutputData_noOutput(mocker, upod):
    """Test UploadOutputData with no output data."""
    mocker.patch.object(
        upod.failoverTransfer, "transferAndRegisterFile", return_value=S_OK({"uploadedSE": "CERN", "lfn": SIM_FILE})
    )
    mocker.patch.object(upod.failoverTransfer, "transferAndRegisterFileFailover")

    wf_commons[0]["outputDataStep"] = "1"
    wf_commons[0]["outputList"] = [
        {"outputDataName": SIM_FILE, "outputDataType": "sim", "outputBKType": "SIM", "stepName": "Gauss_1"}
    ]
    upod.outputSEs = {
        "SIM": "Tier1-Buffer",
    }

    # Execute module
    result = upod.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=upod.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )

    assert not result["OK"], "Execution should not succeed."
    assert result["Message"] == "Output data not found"

    assert upod.fileReport.setFileStatus.call_count == 0
    assert upod.bkClient.sendXMLBookkeepingReport.call_count == 0

    assert upod.failoverTransfer.transferAndRegisterFile.call_count == 0
    assert upod.failoverTransfer.transferAndRegisterFileFailover.call_count == 0

    assert upod.jobReport.setJobParameter.call_count == 0

    # Make sure the request is not generated
    requestDict = json.loads(upod.request.toJSON()["Value"])
    operations = requestDict["Operations"]
    assert len(operations) == 0


def test_uploadOutputData_previousError_fail(mocker, upod):
    """Test UploadOutputData with an intentional failure."""
    mocker.patch.object(upod.failoverTransfer, "transferAndRegisterFile")
    mocker.patch.object(upod.failoverTransfer, "transferAndRegisterFileFailover")
    result = upod.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=upod.step_commons,
        step_number=step_number,
        step_id=step_id,
        # Intentional error
        stepStatus=S_ERROR(),
    )

    assert result["OK"], "Execution should succeed."
    assert result["Value"] == "Failures detected in previous steps: no output data upload attempted"

    assert upod.fileReport.setFileStatus.call_count == 0
    assert upod.bkClient.sendXMLBookkeepingReport.call_count == 0

    assert upod.failoverTransfer.transferAndRegisterFile.call_count == 0
    assert upod.failoverTransfer.transferAndRegisterFileFailover.call_count == 0

    assert upod.jobReport.setJobParameter.call_count == 0

    # Make sure the request is not generated
    requestDict = json.loads(upod.request.toJSON()["Value"])
    operations = requestDict["Operations"]
    assert len(operations) == 0
