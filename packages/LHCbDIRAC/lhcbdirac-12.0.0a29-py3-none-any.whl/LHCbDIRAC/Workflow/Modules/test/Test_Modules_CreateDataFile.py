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
"""Test for CreateDataFile module."""
from pathlib import Path
from textwrap import dedent
import pytest
from LHCbDIRAC.Workflow.Modules.CreateDataFile import CreateDataFile
from DIRAC import S_OK, S_ERROR
from LHCbDIRAC.Workflow.Modules.test.mock_Commons import (
    prod_id,
    prod_job_id,
    wms_job_id,
    workflowStatus,
    step_id,
    step_number,
    wf_commons,
)


@pytest.fixture
def cdf(mocker):
    """Fixture for creating an instance of CreateDataFile module."""
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator")
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.ModuleBase._resolveInputVariables")
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.ModuleBase._resolveInputStep")

    cdf = CreateDataFile()

    yield cdf

    Path(cdf.gangaFileName).unlink(missing_ok=True)


def test_createDataFile_success(cdf):
    """Test CreateDataFile module successfully creates a data file."""
    cdf.inputDataList = [
        "/lhcb/MC/Dev/XDIGI/00211521/0000/00211521_00000489_1.dst",
        "/lhcb/MC/Dev/XDIGI/00211521/0000/00211521_00000489_2.dst",
    ]

    assert cdf.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=cdf.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"], "Execution should succeed."

    assert Path(cdf.gangaFileName).exists(), "Ganga data file should exist."
    with open(cdf.gangaFileName) as f:
        content = f.read()

    expectedContent = dedent(
        """from Gaudi.Configuration import * \nfrom GaudiConf import IOHelper
IOHelper().inputFiles([
'LFN:/lhcb/MC/Dev/XDIGI/00211521/0000/00211521_00000489_1.dst',
'LFN:/lhcb/MC/Dev/XDIGI/00211521/0000/00211521_00000489_2.dst',
], clear=True)

FileCatalog().Catalogs += [ 'xmlcatalog_file:pool_xml_catalog.xml' ]
"""
    )

    assert expectedContent in content


def test_createDataFile_existingData(cdf):
    """Test CreateDataFile module successfully creates a data file."""
    # data.py already exists
    with open(cdf.gangaFileName, "w") as f:
        f.write("Some existing content.")

    cdf.inputDataList = [
        "/lhcb/MC/Dev/XDIGI/00211521/0000/00211521_00000489_1.dst",
        "/lhcb/MC/Dev/XDIGI/00211521/0000/00211521_00000489_2.dst",
    ]

    assert cdf.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=cdf.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"], "Execution should succeed."

    assert Path(cdf.gangaFileName).exists(), "Ganga data file should be created."
    with open(cdf.gangaFileName) as f:
        content = f.read()

    expectedContent = dedent(
        """from Gaudi.Configuration import * \nfrom GaudiConf import IOHelper
IOHelper().inputFiles([
'LFN:/lhcb/MC/Dev/XDIGI/00211521/0000/00211521_00000489_1.dst',
'LFN:/lhcb/MC/Dev/XDIGI/00211521/0000/00211521_00000489_2.dst',
], clear=True)

FileCatalog().Catalogs += [ 'xmlcatalog_file:pool_xml_catalog.xml' ]
"""
    )

    assert expectedContent in content, "Ganga data file should contain the expected content."


def test_createDataFile_noInputData(cdf):
    """Test CreateDataFile when there is no input data: it should exit without data.py."""
    # No input data
    cdf.inputDataList = []

    assert cdf.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=cdf.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"], "Execution should succeed."

    assert not Path(cdf.gangaFileName).exists(), "Ganga data file should not be created."


def test_createDataFile_previousError(cdf):
    """Test CreateDataFile module when there is a previous error: it should not create data.py."""
    cdf.inputDataList = [
        "/lhcb/MC/Dev/XDIGI/00211521/0000/00211521_00000489_1.dst",
        "/lhcb/MC/Dev/XDIGI/00211521/0000/00211521_00000489_2.dst",
    ]

    assert cdf.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=cdf.step_commons,
        step_number=step_number,
        step_id=step_id,
        # Intentionally setting stepStatus to S_ERROR
        stepStatus=S_ERROR(),
    )["OK"], "Execution should succeed."

    assert not Path(cdf.gangaFileName).exists(), "Ganga data file should not be created."
