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
"""Unit tests for Workflow Module FileUsage."""

import pytest

from DIRAC import S_OK, S_ERROR
from DIRAC.RequestManagementSystem.Client.Request import Request
from LHCbDIRAC.Workflow.Modules.FileUsage import FileUsage
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
def fileusage(mocker):
    """Fixture for FileUsage module."""
    mocker.patch(
        "LHCbDIRAC.DataManagementSystem.Client.DataUsageClient.DataUsageClient.sendDataUsageReport", return_value=S_OK()
    )
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator")
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.ModuleBase._resolveInputVariables")

    fileusage = FileUsage()
    fileusage.request = Request()

    yield fileusage


# Test Scenarios
def test_fileUsage_success(mocker, fileusage):
    """Test successful execution of FileUsage module."""
    mocker.patch("DIRAC.gConfig.getValue", return_value="SiteA")

    fileusage.inputDataList = [
        "/lhcb/data/2010/EW.DST/00008380/0000/00008380_00000287_1.ew.dst",
        # No directory specified: should be ignored
        "00008380_00000285_1.ew.dst",
        "/lhcb/data/2010/EW.DST/00008380/0000/00008380_00000281_1.ew.dst",
        "/lhcb/data/2011/EW.DST/00008380/0000/00008380_00000281_1.ew.dst",
    ]

    assert fileusage.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=fileusage.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"], "Execution should succeed."

    fileusage.dataUsageClient.sendDataUsageReport.assert_called_once()
    args, _ = fileusage.dataUsageClient.sendDataUsageReport.call_args
    assert args[0] == "SiteA"
    assert args[1] == {
        "/lhcb/data/2010/EW.DST/00008380/0000/": 2,
        "/lhcb/data/2011/EW.DST/00008380/0000/": 1,
    }
    assert fileusage.request.isEmpty()


def test_fileUsage_noSiteName(fileusage):
    """Test successful execution of FileUsage module: there is no site specified in the configuration."""
    fileusage.inputDataList = [
        "/lhcb/data/2010/EW.DST/00008380/0000/00008380_00000287_1.ew.dst",
        # No directory specified: should be ignored
        "00008380_00000285_1.ew.dst",
        "/lhcb/data/2010/EW.DST/00008380/0000/00008380_00000281_1.ew.dst",
    ]

    assert fileusage.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=fileusage.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"], "Execution should succeed."

    # Get parameters passed to sendDataUsageReport
    fileusage.dataUsageClient.sendDataUsageReport.assert_called_once()
    args, _ = fileusage.dataUsageClient.sendDataUsageReport.call_args
    assert args[0] == "UNKNOWN"  # Site name should be "UNKNOWN" because it is not specified in the cfg.
    assert args[1] == {"/lhcb/data/2010/EW.DST/00008380/0000/": 2}
    assert fileusage.request.isEmpty()


def test_fileUsage_failedReport(mocker, fileusage):
    """Test successful execution of FileUsage module:
    the dataUsageReport cannot be sent, a failover request should be generated."""
    mocker.patch("DIRAC.gConfig.getValue", return_value="SiteA")
    mocker.patch(
        "LHCbDIRAC.DataManagementSystem.Client.DataUsageClient.DataUsageClient.sendDataUsageReport",
        return_value={"OK": False, "rpcStub": "123"},
    )

    fileusage.inputDataList = [
        "/lhcb/data/2010/EW.DST/00008380/0000/00008380_00000287_1.ew.dst",
        # No directory specified: should be ignored
        "00008380_00000285_1.ew.dst",
        "/lhcb/data/2010/EW.DST/00008380/0000/00008380_00000281_1.ew.dst",
    ]

    assert fileusage.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=fileusage.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"], "Execution should succeed."

    # Get parameters passed to sendDataUsageReport
    fileusage.dataUsageClient.sendDataUsageReport.assert_called_once()
    args, _ = fileusage.dataUsageClient.sendDataUsageReport.call_args
    assert args[0] == "SiteA"
    assert args[1] == {"/lhcb/data/2010/EW.DST/00008380/0000/": 2}

    assert not fileusage.request.isEmpty()


def test_fileUsage_noInput(fileusage):
    """Test successful execution of FileUsage when no input data is passed."""
    # No input data
    fileusage.inputDataList = []

    assert fileusage.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=fileusage.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"], "Execution should succeed."

    fileusage.dataUsageClient.sendDataUsageReport.assert_not_called()
    assert fileusage.request.isEmpty()


def test_fileUsage_previousError_fail(fileusage):
    """Test FileUsage with an intentional failure."""
    assert fileusage.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=fileusage.step_commons,
        step_number=step_number,
        step_id=step_id,
        # Intentional error
        stepStatus=S_ERROR(),
    )["OK"]

    fileusage.dataUsageClient.sendDataUsageReport.assert_not_called()
    assert fileusage.request.isEmpty()
