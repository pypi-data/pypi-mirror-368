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
"""Unit tests for Workflow Module UploadMC."""
# pylint: disable=protected-access, missing-docstring, invalid-name, line-too-long

import json
from pathlib import Path
from textwrap import dedent
import pytest

from DIRAC import S_OK
from LHCbDIRAC.Workflow.Modules.test.mock_Commons import (
    step_commons,
    wf_commons,
    prod_id,
    prod_job_id,
    wms_job_id,
    workflowStatus,
    step_id,
    step_number,
)
from LHCbDIRAC.Workflow.Modules.UploadMC import UploadMC


# Helpers
ERROR_FILE = f"{wms_job_id}_Errors_Gauss.json"
XML_SUMMARY = f"summaryGauss_{prod_id}_{prod_job_id}_1.xml"
GENERATOR_LOG = "GeneratorLog.xml"
PRMON = "prmon_Gauss.json"

GENERATED_GAUSS_SUMMARY = f"summaryGauss_{prod_id}_{prod_job_id}_1.json"
GENERATED_GENERATOR_LOG = f"GeneratorLog_{prod_id}_{prod_job_id}.json"


@pytest.fixture
def mc(mocker):
    """Setup AnalyseXMLSummaryNew module."""
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator")
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.ModuleBase._resolveInputVariables")

    # Setup module
    mc = UploadMC()

    yield mc

    Path(ERROR_FILE).unlink(missing_ok=True)
    Path(XML_SUMMARY).unlink(missing_ok=True)
    Path(GENERATOR_LOG).unlink(missing_ok=True)
    Path(PRMON).unlink(missing_ok=True)

    Path(GENERATED_GAUSS_SUMMARY).unlink(missing_ok=True)
    Path(GENERATED_GENERATOR_LOG).unlink(missing_ok=True)


# Tests
def test_MCUpload_success(mocker, mc):
    """Test MCUpload success."""
    mocker.patch("LHCbDIRAC.ProductionManagementSystem.Client.MCStatsClient.MCStatsClient.set", return_value=S_OK())
    mocker.patch("DIRAC.ConfigurationSystem.Client.Helpers.Operations.Operations.getValue", return_value=True)
    mcStatsClientSet = mocker.patch("LHCbDIRAC.ProductionManagementSystem.Client.MCStatsClient.MCStatsClient.set")

    # Create error file
    with open(ERROR_FILE, "w") as f:
        json.dump({"1": "error1", "2": "error2", "3": "error3"}, f)

    # Create XML summary
    summaryContent = dedent(
        """<?xml version="1.0" encoding="UTF-8"?>
        <summary version="1.0" xsi:noNamespaceSchemaLocation="$XMLSUMMARYBASEROOT/xml/XMLSummary.xsd"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <success>True</success>
                <step>finalize</step>
                <usage>
                        <stat unit="KB" useOf="MemoryMaximum">866104.0</stat>
                </usage>
                <input>
                        <file GUID="CCE96707-4BE9-E011-81CD-003048F35252" name="LFN:00012478_00000532_1.sim"
                        status="fail">200</file>
                        <file GUID="CCE96709-5BE9-E012-41BD-004048E36253" name="LFN:00012478_00000533_1.sim"
                        status="fail">200</file>
                </input>
                <output>
                        <file GUID="229BBEF1-66E9-E011-BBD0-003048F35252" name="PFN:00012478_00000532_2.xdigi"
                        status="full">200</file>
                </output>
                <counters>
                    <counter name="MCVeloHitPacker/# PackedData">281148</counter>
                    <counter name="MCPuVetoHitPacker/# PackedData">13019</counter>
                    <counter name="MCTTHitPacker/# PackedData">100850</counter>
                </counters>
        </summary>
        """
    )
    with open(XML_SUMMARY, "w") as f:
        f.write(summaryContent)

    # Create GeneratorLog
    generatorLogContent = dedent(
        """<?xml version="1.0"?>
        <generatorCounters>
        <version>1.1</version>
        <eventType>31111201</eventType>
        <counter name = "all events (including empty events)">
            <value> 17699 </value>
        </counter>
        <counter name = "generated events">
            <value> 17692 </value>
        </counter>
        <efficiency name = "generator level cut">
            <after> 39 </after>
            <before> 134 </before>
            <value> 0.29104 </value>
            <error> 0.039241 </error>
        </efficiency>
        <fraction name = "signal tau- in sample">
            <number> 41 </number>
            <value> 0.53247 </value>
            <error> 0.05686 </error>
        </fraction>
        <eventType>30000000</eventType>
        <method>GenerationNext.MinimumBias</method>
        <generator>Pythia8</generator>
        <method>GenerationPrev.MinimumBias</method>
        <generator>Pythia8</generator>
        <crosssection id = "101">
            <description> "non-diffractive" </description>
            <generated> 342 </generated>
            <value> 56.872 </value>
        </crosssection>
        </generatorCounters>
       """
    )

    with open(GENERATOR_LOG, "w") as f:
        f.write(generatorLogContent)

    # Create prmon file
    prmonContent = {}
    with open(PRMON, "w") as f:
        json.dump(prmonContent, f)

    # Call the execute method
    assert mc.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=step_commons[0],
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"]

    # Make sure the MCStatsClient is called as expected
    assert mcStatsClientSet.call_count == 4

    # Check the content of the generated gauss summary
    generatedSummaryGauss = Path(GENERATED_GAUSS_SUMMARY)
    assert generatedSummaryGauss.exists()
    with open(generatedSummaryGauss) as f:
        generatedSummaryGaussContent = json.load(f)

    expectedGeneratedSummaryGauss = {
        "Counters": {
            "MCVeloHitPacker": {"PackedData": 281148},
            "MCPuVetoHitPacker": {"PackedData": 13019},
            "MCTTHitPacker": {"PackedData": 100850},
            "ID": {"JobID": wms_job_id, "ProductionID": prod_id, "prod_job_id": prod_job_id},
        },
    }
    assert generatedSummaryGaussContent == expectedGeneratedSummaryGauss

    # Check the content of the generated generator log
    generatedGeneratorLog = Path(GENERATED_GENERATOR_LOG)
    assert generatedGeneratorLog.exists()
    with open(generatedGeneratorLog) as f:
        generatedGeneratorLogContent = json.load(f)

    expectedGeneratedGeneratorLog = {
        "generatorCounters": {
            "counter": {"all events (including empty events)": 17699, "generated events": 17692},
            "efficiency": {"generator level cut": {"after": 39, "before": 134, "error": 0.039241, "value": 0.29104}},
            "fraction": {"signal tau- in sample": {"number": 41, "error": 0.05686, "value": 0.53247}},
            "crossSection": {"non-diffractive": {"ID": 101, "generated": 342, "value": 56.872}},
            "method": {"GenerationNext.MinimumBias": "Pythia8", "GenerationPrev.MinimumBias": "Pythia8"},
            "ID": {"JobID": 12345, "ProductionID": "123", "prod_job_id": "00000456"},
        }
    }
    assert generatedGeneratorLogContent == expectedGeneratedGeneratorLog


def test_MCUpload_missingFiles(mocker, mc):
    """Test MCUpload success when there are missing files: it should upload the existing files."""
    mocker.patch("LHCbDIRAC.ProductionManagementSystem.Client.MCStatsClient.MCStatsClient.set", return_value=S_OK())
    mocker.patch("DIRAC.ConfigurationSystem.Client.Helpers.Operations.Operations.getValue", return_value=True)
    mcStatsClientSet = mocker.patch("LHCbDIRAC.ProductionManagementSystem.Client.MCStatsClient.MCStatsClient.set")

    # Create error file
    with open(ERROR_FILE, "w") as f:
        json.dump({"1": "error1", "2": "error2", "3": "error3"}, f)

    # Create prmon file
    prmonContent = {}
    with open(PRMON, "w") as f:
        json.dump(prmonContent, f)

    # Call the execute method
    assert mc.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=step_commons[0],
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"]

    assert mcStatsClientSet.call_count == 2
    assert not Path(GENERATED_GAUSS_SUMMARY).exists()
    assert not Path(GENERATED_GENERATOR_LOG).exists()


def test_MCUpload_disabledUpload(mocker, mc):
    """Test MCUpload success when uploads are disabled: it should not upload the files."""
    mocker.patch("LHCbDIRAC.ProductionManagementSystem.Client.MCStatsClient.MCStatsClient.set", return_value=S_OK())
    mcStatsClientSet = mocker.patch("LHCbDIRAC.ProductionManagementSystem.Client.MCStatsClient.MCStatsClient.set")
    # opsGetValue is mocked to return False: the upload is disabled
    mocker.patch("DIRAC.ConfigurationSystem.Client.Helpers.Operations.Operations.getValue", return_value=False)

    # Create error file
    with open(ERROR_FILE, "w") as f:
        json.dump({"1": "error1", "2": "error2", "3": "error3"}, f)

    # Create prmon file
    prmonContent = {}
    with open(PRMON, "w") as f:
        json.dump(prmonContent, f)

    # Call the execute method
    assert mc.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=step_commons[0],
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"]

    assert not mcStatsClientSet.called
    assert not Path(GENERATED_GAUSS_SUMMARY).exists()
    assert not Path(GENERATED_GENERATOR_LOG).exists()


def test_MCUpload_malformedXMLSummary(mocker, mc):
    """Test MCUpload when there is a malformed input: it should upload the other files even if there is an issue."""
    mocker.patch("LHCbDIRAC.ProductionManagementSystem.Client.MCStatsClient.MCStatsClient.set", return_value=S_OK())
    mcStatsClientSet = mocker.patch("LHCbDIRAC.ProductionManagementSystem.Client.MCStatsClient.MCStatsClient.set")
    mocker.patch("DIRAC.ConfigurationSystem.Client.Helpers.Operations.Operations.getValue", return_value=True)

    # Create error file
    with open(ERROR_FILE, "w") as f:
        json.dump({"1": "error1", "2": "error2", "3": "error3"}, f)

    # Create a malformed XML summary: there is no counter
    summaryContent = dedent(
        """<?xml version="1.0" encoding="UTF-8"?>
        <summary version="1.0" xsi:noNamespaceSchemaLocation="$XMLSUMMARYBASEROOT/xml/XMLSummary.xsd"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <success>True</success>
                <step>finalize</step>
                <usage>
                        <stat unit="KB" useOf="MemoryMaximum">866104.0</stat>
                </usage>
                <input>
                        <file GUID="CCE96707-4BE9-E011-81CD-003048F35252" name="LFN:00012478_00000532_1.sim"
                        status="fail">200</file>
                        <file GUID="CCE96709-5BE9-E012-41BD-004048E36253" name="LFN:00012478_00000533_1.sim"
                        status="fail">200</file>
                </input>
                <output>
                        <file GUID="229BBEF1-66E9-E011-BBD0-003048F35252" name="PFN:00012478_00000532_2.xdigi"
                        status="full">200</file>
                </output>
        </summary>
        """
    )
    with open(XML_SUMMARY, "w") as f:
        f.write(summaryContent)

    # Create prmon file
    prmonContent = {}
    with open(PRMON, "w") as f:
        json.dump(prmonContent, f)

    # Call the execute method
    assert mc.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=step_commons[0],
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"]

    # Make sure the MCStatsClient is called 2 times and not 3
    assert mcStatsClientSet.call_count == 2
    assert not Path(GENERATED_GAUSS_SUMMARY).exists()
    assert not Path(GENERATED_GENERATOR_LOG).exists()


def test_MCUpload_noInputData(mocker, mc):
    """Test MCUpload success when there is no relevant input data."""
    mocker.patch("LHCbDIRAC.ProductionManagementSystem.Client.MCStatsClient.MCStatsClient.set", return_value=S_OK())
    mocker.patch("DIRAC.ConfigurationSystem.Client.Helpers.Operations.Operations.getValue", return_value=True)
    mcStatsClientSet = mocker.patch("LHCbDIRAC.ProductionManagementSystem.Client.MCStatsClient.MCStatsClient.set")

    assert mc.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=step_commons[0],
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"]

    assert not mcStatsClientSet.called
    assert not Path(GENERATED_GAUSS_SUMMARY).exists()
    assert not Path(GENERATED_GENERATOR_LOG).exists()
