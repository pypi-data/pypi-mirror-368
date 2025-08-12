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
"""Unit tests for Workflow Module StepAccounting."""

import json
from pathlib import Path
import shutil
import zipfile
import pytest

from DIRAC import S_OK, S_ERROR
from DIRAC.RequestManagementSystem.Client.Request import Request
from LHCbDIRAC.Workflow.Modules.UploadLogFile import UploadLogFile
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
PRODCONF_JSON = "prodConf_example.json"
PRODCONF_PY = "prodConf_example.py"


@pytest.fixture
def uplogfile(mocker):
    """Fixture for UploadLogFile module."""
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator")
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.ModuleBase._resolveInputVariables")

    uplogfile = UploadLogFile()
    mocker.patch.object(uplogfile, "jobReport")
    uplogfile.request = Request()

    yield uplogfile

    Path(PRODCONF_JSON).unlink(missing_ok=True)
    Path(PRODCONF_PY).unlink(missing_ok=True)

    if uplogfile.logdir:
        shutil.rmtree(uplogfile.logdir, ignore_errors=True)

    Path(f"{prod_job_id}.zip").unlink(missing_ok=True)
    shutil.rmtree("unzipped", ignore_errors=True)


# Test Scenarios
def test_uploadLogFile_success(mocker, uplogfile):
    """Test successful execution of UploadLogFile module."""
    logURL = "notImportant"
    mockSEMethod = mocker.patch(
        "DIRAC.Resources.Storage.StorageElement.StorageElementItem._StorageElementItem__executeMethod",
        return_value=S_OK({"Failed": [], "Successful": {logURL: logURL}}),
    )
    mockTransferAndRegister = mocker.patch(
        "DIRAC.DataManagementSystem.Client.FailoverTransfer.FailoverTransfer.transferAndRegisterFile",
        return_value=S_OK(),
    )

    # Create fake prodconf files
    with open(PRODCONF_JSON, "w") as f:
        f.write('{"foo": "bar"}')
    with open(PRODCONF_PY, "w") as f:
        f.write('foo = "bar"')

    # Execute the module
    assert uplogfile.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=uplogfile.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"], "Execution should succeed."

    # Check the log directory
    assert uplogfile.logdir != ""
    logDirectory = Path(uplogfile.logdir)
    assert logDirectory.exists()
    assert logDirectory.is_dir()
    assert logDirectory.joinpath("prodConf_example.json").exists()
    assert logDirectory.joinpath(PRODCONF_JSON).read_text() == '{"foo": "bar"}'
    assert logDirectory.joinpath("prodConf_example.py").exists()
    assert logDirectory.joinpath(PRODCONF_PY).read_text() == 'foo = "bar"'

    for file in logDirectory.iterdir():
        assert file.stat().st_mode & 0o777 == 0o755

    # Check the generated zip file
    zipFile = Path(f"{prod_job_id}.zip")
    assert zipFile.exists()

    zipfile.ZipFile(zipFile, "r").extractall("unzipped")
    unzipped = Path("unzipped").joinpath(prod_job_id)
    assert unzipped.joinpath(PRODCONF_JSON).exists()
    assert unzipped.joinpath(PRODCONF_PY).exists()
    assert unzipped.joinpath(PRODCONF_JSON).read_text() == '{"foo": "bar"}'
    assert unzipped.joinpath(PRODCONF_PY).read_text() == 'foo = "bar"'

    # Make sure that StorageElement was called twice (getURL, putFile)
    assert mockSEMethod.call_count == 2

    # Make sure that the request was not created
    assert mockTransferAndRegister.call_count == 0

    # Make sure the application status was not changed
    assert uplogfile.jobReport.setApplicationStatus.call_count == 0

    # Check the jobReport.setParameter arguments
    assert uplogfile.jobReport.setJobParameter.call_count == 1
    assert uplogfile.jobReport.setJobParameter.call_args_list
    params = uplogfile.jobReport.setJobParameter.call_args_list[0][0]
    assert params[0] == "Log URL"
    assert params[1] == f'<a href="{logURL}">Log file directory</a>'


def test_uploadLogFile_noOutputFile(mocker, uplogfile):
    """Test execution of UploadLogFile module when there is no output files:

    __populateLogDirectory should return an error, because there is no "successful" files in logDirectory.
    """
    mockSEMethod = mocker.patch(
        "DIRAC.Resources.Storage.StorageElement.StorageElementItem._StorageElementItem__executeMethod",
        return_value=S_OK({"Failed": [], "Successful": {"notImportant": "notImportant"}}),
    )
    mockTransferAndRegister = mocker.patch(
        "DIRAC.DataManagementSystem.Client.FailoverTransfer.FailoverTransfer.transferAndRegisterFile",
        return_value=S_OK(),
    )

    # Execute the module
    assert uplogfile.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=uplogfile.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"], "Execution should succeed."

    # Check the log directory
    assert uplogfile.logdir != ""
    logDirectory = Path(uplogfile.logdir)
    assert logDirectory.exists()
    assert logDirectory.is_dir()
    # Make sur logDirectory is an empty directory
    assert not list(logDirectory.iterdir())

    # Check the generated zip file
    zipFile = Path(f"{prod_job_id}.zip")
    assert not zipFile.exists()

    # Make sure that StorageElement was called twice (getURL, putFile)
    assert mockSEMethod.call_count == 0

    # Make sure that the request was not created
    assert mockTransferAndRegister.call_count == 0

    # Make sure the application status was changed
    assert uplogfile.jobReport.setApplicationStatus.call_count == 1
    assert uplogfile.jobReport.setJobParameter.call_count == 0


def test_uploadLogFile_zipException(mocker, uplogfile):
    """Test execution of UploadLogFile module when an exception is raised when zipping files:"""
    mocker.patch("LHCbDIRAC.Workflow.Modules.UploadLogFile.zipFiles", side_effect=OSError)
    mockSEMethod = mocker.patch(
        "DIRAC.Resources.Storage.StorageElement.StorageElementItem._StorageElementItem__executeMethod",
        return_value=S_OK({"Failed": [], "Successful": {"notImportant": "notImportant"}}),
    )
    mockTransferAndRegister = mocker.patch(
        "DIRAC.DataManagementSystem.Client.FailoverTransfer.FailoverTransfer.transferAndRegisterFile",
        return_value=S_OK(),
    )

    # Create fake prodconf files
    with open(PRODCONF_JSON, "w") as f:
        f.write('{"foo": "bar"}')
    with open(PRODCONF_PY, "w") as f:
        f.write('foo = "bar"')

    # Execute the module
    assert uplogfile.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=uplogfile.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"], "Execution should succeed."

    # Check the log directory
    assert uplogfile.logdir != ""
    logDirectory = Path(uplogfile.logdir)
    assert logDirectory.exists()
    assert logDirectory.is_dir()
    assert logDirectory.joinpath("prodConf_example.json").exists()
    assert logDirectory.joinpath(PRODCONF_JSON).read_text() == '{"foo": "bar"}'
    assert logDirectory.joinpath("prodConf_example.py").exists()
    assert logDirectory.joinpath(PRODCONF_PY).read_text() == 'foo = "bar"'

    for file in logDirectory.iterdir():
        assert file.stat().st_mode & 0o777 == 0o755

    # Check the generated zip file
    zipFile = Path(f"{prod_job_id}.zip")
    assert not zipFile.exists()

    # Make sure that StorageElement was called twice (getURL, putFile)
    assert mockSEMethod.call_count == 0

    # Make sure that the request was not created
    assert mockTransferAndRegister.call_count == 0

    # Make sure the application status was changed
    assert uplogfile.jobReport.setApplicationStatus.call_count == 1


def test_uploadLogFile_zipError(mocker, uplogfile):
    """Test execution of UploadLogFile module when an error is occurring when zipping files:"""
    mocker.patch("LHCbDIRAC.Workflow.Modules.UploadLogFile.zipFiles", return_value=S_ERROR("Error"))
    mockSEMethod = mocker.patch(
        "DIRAC.Resources.Storage.StorageElement.StorageElementItem._StorageElementItem__executeMethod",
        return_value=S_OK({"Failed": [], "Successful": {"notImportant": "notImportant"}}),
    )
    mockTransferAndRegister = mocker.patch(
        "DIRAC.DataManagementSystem.Client.FailoverTransfer.FailoverTransfer.transferAndRegisterFile",
        return_value=S_OK(),
    )

    # Create fake prodconf files
    with open(PRODCONF_JSON, "w") as f:
        f.write('{"foo": "bar"}')
    with open(PRODCONF_PY, "w") as f:
        f.write('foo = "bar"')

    # Execute the module
    assert uplogfile.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=uplogfile.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"], "Execution should succeed."

    # Check the log directory
    assert uplogfile.logdir != ""
    logDirectory = Path(uplogfile.logdir)
    assert logDirectory.exists()
    assert logDirectory.is_dir()
    assert logDirectory.joinpath("prodConf_example.json").exists()
    assert logDirectory.joinpath(PRODCONF_JSON).read_text() == '{"foo": "bar"}'
    assert logDirectory.joinpath("prodConf_example.py").exists()
    assert logDirectory.joinpath(PRODCONF_PY).read_text() == 'foo = "bar"'

    for file in logDirectory.iterdir():
        assert file.stat().st_mode & 0o777 == 0o755

    # Check the generated zip file
    zipFile = Path(f"{prod_job_id}.zip")
    assert not zipFile.exists()

    # Make sure that StorageElement was called twice (getURL, putFile)
    assert mockSEMethod.call_count == 0

    # Make sure that the request was not created
    assert mockTransferAndRegister.call_count == 0

    # Make sure the application status was changed
    assert uplogfile.jobReport.setApplicationStatus.call_count == 1


def test_uploadLogFile_SEError(mocker, uplogfile):
    """Test execution of UploadLogFile module when an error is occurring when calling StorageElement"""
    mocker.patch("LHCbDIRAC.Workflow.Modules.UploadLogFile.getDestinationSEList", return_value=["SE1", "SE2"])
    mockSEMethod = mocker.patch(
        "DIRAC.Resources.Storage.StorageElement.StorageElementItem._StorageElementItem__executeMethod",
        return_value=S_ERROR("Error"),
    )
    mockTransferAndRegister = mocker.patch(
        "DIRAC.DataManagementSystem.Client.FailoverTransfer.FailoverTransfer.transferAndRegisterFile",
        return_value=S_OK({"uploadedSE": "SE1"}),
    )

    # Create fake prodconf files
    with open(PRODCONF_JSON, "w") as f:
        f.write('{"foo": "bar"}')
    with open(PRODCONF_PY, "w") as f:
        f.write('foo = "bar"')

    # Execute the module
    assert uplogfile.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=uplogfile.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"], "Execution should succeed."

    # Check the log directory
    assert uplogfile.logdir != ""
    logDirectory = Path(uplogfile.logdir)
    assert logDirectory.exists()
    assert logDirectory.is_dir()
    assert logDirectory.joinpath("prodConf_example.json").exists()
    assert logDirectory.joinpath(PRODCONF_JSON).read_text() == '{"foo": "bar"}'
    assert logDirectory.joinpath("prodConf_example.py").exists()
    assert logDirectory.joinpath(PRODCONF_PY).read_text() == 'foo = "bar"'

    for file in logDirectory.iterdir():
        assert file.stat().st_mode & 0o777 == 0o755

    # Check the generated zip file
    zipFile = Path(f"{prod_job_id}.zip")
    assert zipFile.exists()

    zipfile.ZipFile(zipFile, "r").extractall("unzipped")
    unzipped = Path("unzipped").joinpath(prod_job_id)
    assert unzipped.joinpath(PRODCONF_JSON).exists()
    assert unzipped.joinpath(PRODCONF_PY).exists()
    assert unzipped.joinpath(PRODCONF_JSON).read_text() == '{"foo": "bar"}'
    assert unzipped.joinpath(PRODCONF_PY).read_text() == 'foo = "bar"'

    # Make sure that StorageElement was called twice (getURL, putFile)
    assert mockSEMethod.call_count == 2

    # Make sure that the request was created
    assert mockTransferAndRegister.call_count == 1

    requestDict = json.loads(uplogfile.request.toJSON()["Value"])
    operations = requestDict["Operations"]

    assert len(operations) == 2
    assert operations[0]["Type"] == "LogUpload"
    assert len(operations[0]["Files"]) == 1
    assert operations[0]["Files"][0]["LFN"] == uplogfile.logLFNPath

    assert operations[1]["Type"] == "RemoveFile"
    assert len(operations[1]["Files"]) == 1
    assert operations[1]["Files"][0]["LFN"] == uplogfile.logLFNPath

    # Make sure the application status was not changed
    assert uplogfile.jobReport.setApplicationStatus.call_count == 0


def test_uploadLogFile_transferError(mocker, uplogfile):
    """Test execution of UploadLogFile module when an error is occurring when calling StorageElement and FailoverTransfer"""
    mocker.patch("LHCbDIRAC.Workflow.Modules.UploadLogFile.getDestinationSEList", return_value=["SE1", "SE2"])
    mockSEMethod = mocker.patch(
        "DIRAC.Resources.Storage.StorageElement.StorageElementItem._StorageElementItem__executeMethod",
        return_value=S_ERROR("Error"),
    )
    mockTransferAndRegister = mocker.patch(
        "DIRAC.DataManagementSystem.Client.FailoverTransfer.FailoverTransfer.transferAndRegisterFile",
        return_value=S_ERROR("Error"),
    )

    # Create fake prodconf files
    with open(PRODCONF_JSON, "w") as f:
        f.write('{"foo": "bar"}')
    with open(PRODCONF_PY, "w") as f:
        f.write('foo = "bar"')

    # Execute the module
    assert uplogfile.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=uplogfile.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"], "Execution should succeed."

    # Check the log directory
    assert uplogfile.logdir != ""
    logDirectory = Path(uplogfile.logdir)
    assert logDirectory.exists()
    assert logDirectory.is_dir()
    assert logDirectory.joinpath("prodConf_example.json").exists()
    assert logDirectory.joinpath(PRODCONF_JSON).read_text() == '{"foo": "bar"}'
    assert logDirectory.joinpath("prodConf_example.py").exists()
    assert logDirectory.joinpath(PRODCONF_PY).read_text() == 'foo = "bar"'

    for file in logDirectory.iterdir():
        assert file.stat().st_mode & 0o777 == 0o755

    # Check the generated zip file
    zipFile = Path(f"{prod_job_id}.zip")
    assert zipFile.exists()

    zipfile.ZipFile(zipFile, "r").extractall("unzipped")
    unzipped = Path("unzipped").joinpath(prod_job_id)
    assert unzipped.joinpath(PRODCONF_JSON).exists()
    assert unzipped.joinpath(PRODCONF_PY).exists()
    assert unzipped.joinpath(PRODCONF_JSON).read_text() == '{"foo": "bar"}'
    assert unzipped.joinpath(PRODCONF_PY).read_text() == 'foo = "bar"'

    # Make sure that StorageElement was called twice (getURL, putFile)
    assert mockSEMethod.call_count == 2

    # Make sure that the request was not created
    assert mockTransferAndRegister.call_count == 1

    requestDict = json.loads(uplogfile.request.toJSON()["Value"])
    operations = requestDict["Operations"]

    assert len(operations) == 0

    # Make sure the application status was changed
    assert uplogfile.jobReport.setApplicationStatus.call_count == 1
