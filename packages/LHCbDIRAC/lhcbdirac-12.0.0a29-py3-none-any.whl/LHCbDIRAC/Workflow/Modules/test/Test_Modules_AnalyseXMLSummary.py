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
""" Analyse XMLSummary test module."""
# pylint: disable=protected-access, missing-docstring, invalid-name, line-too-long
import pytest
from pathlib import Path
from textwrap import dedent

from DIRAC import S_OK, S_ERROR
from DIRAC.TransformationSystem.Client.FileReport import FileReport
from LHCbDIRAC.Core.Utilities.XMLSummaries import XMLSummary

# mocks
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
from DIRAC.DataManagementSystem.Client.test.mock_DM import dm_mock
from LHCbDIRAC.BookkeepingSystem.Client.test.mock_BookkeepingClient import bkc_mock
from LHCbDIRAC.Workflow.Modules.AnalyseXMLSummary import AnalyseXMLSummary


# Helper functions
XML_SUMMARY_FILE = "XMLSummary.xml"


def prepare_XMLSummary_file(xml_summary, content):
    with open(xml_summary, "w") as f:
        f.write(content)
    return XMLSummary(xml_summary)


@pytest.fixture
def axlf(mocker):
    """Fixture for AnalyseXMLSummary module."""
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator")
    mocker.patch("LHCbDIRAC.Workflow.Modules.AnalyseXMLSummary.AnalyseXMLSummary._resolveInputVariables")
    mocker.patch("LHCbDIRAC.Workflow.Modules.AnalyseXMLSummary.NotificationClient.sendMail", return_value=S_OK())

    axlf = AnalyseXMLSummary(bkClient=bkc_mock, dm=dm_mock)
    mocker.patch.object(axlf, "jobReport", autospec=True)
    axlf.jobReport.setApplicationStatus.return_value = S_OK()
    axlf.fileReport = FileReport()
    axlf.XMLSummary = XML_SUMMARY_FILE

    yield axlf

    # Teardown
    Path(XML_SUMMARY_FILE).unlink()


# Test scenarios
def test_analyseXMLSummary_basic_success(axlf):
    """Test basic success scenario."""
    xml_content = dedent(
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
                        status="full">200</file>
                </input>
                <output>
                        <file GUID="229BBEF1-66E9-E011-BBD0-003048F35252" name="PFN:00012478_00000532_2.xdigi"
                        status="full">200</file>
                </output>
        </summary>
        """
    )
    axlf.XMLSummary_o = prepare_XMLSummary_file(axlf.XMLSummary, xml_content)

    assert axlf.XMLSummary_o.success == "True"
    assert axlf.XMLSummary_o.step == "finalize"
    assert axlf.XMLSummary_o._outputsOK()
    assert not axlf.XMLSummary_o.inputFileStats["mult"]
    assert not axlf.XMLSummary_o.inputFileStats["other"]
    assert axlf.execute(
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
    axlf.jobReport.setApplicationStatus.assert_called_once()
    axlf.nc.sendMail.assert_not_called()
    assert axlf.fileReport.statusDict == {}


def test_analyseXMLSummary_previousError_success(axlf):
    """Test success scenario with previous error: stepStatus = S_ERROR()."""
    xml_content = dedent(
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
                        status="full">200</file>
                </input>
                <output>
                        <file GUID="229BBEF1-66E9-E011-BBD0-003048F35252" name="PFN:00012478_00000532_2.xdigi"
                        status="full">200</file>
                </output>
        </summary>
        """
    )
    axlf.XMLSummary_o = prepare_XMLSummary_file(axlf.XMLSummary, xml_content)

    assert axlf.XMLSummary_o.success == "True"
    assert axlf.XMLSummary_o.step == "finalize"
    assert axlf.XMLSummary_o._outputsOK()
    assert not axlf.XMLSummary_o.inputFileStats["mult"]
    assert not axlf.XMLSummary_o.inputFileStats["other"]
    assert axlf.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=step_commons[0],
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_ERROR(),
    )["OK"]
    axlf.jobReport.setApplicationStatus.assert_not_called()
    axlf.nc.sendMail.assert_not_called()
    assert axlf.fileReport.statusDict == {}


def test_analyseXMLSummary_badInput_success(axlf):
    """Test success scenario with part and fail input not part of the input data list."""
    xml_content = dedent(
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
                        status="part">200</file>
                        <file GUID="CCE96809-4FC6-F623-61F5-003048F35253" name="LFN:00012478_00000533_1.sim"
                        status="fail">200</file>
                </input>
                <output>
                        <file GUID="229BBEF1-66E9-E011-BBD0-003048F35252" name="PFN:00012478_00000532_2.xdigi"
                        status="full">200</file>
                </output>
        </summary>
        """
    )
    axlf.XMLSummary_o = prepare_XMLSummary_file(axlf.XMLSummary, xml_content)

    assert axlf.XMLSummary_o.success == "True"
    assert axlf.XMLSummary_o.step == "finalize"
    assert axlf.XMLSummary_o._outputsOK()
    assert not axlf.XMLSummary_o.inputFileStats["mult"]
    assert not axlf.XMLSummary_o.inputFileStats["other"]
    assert axlf.execute(
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
    axlf.jobReport.setApplicationStatus.assert_called_once()
    axlf.nc.sendMail.assert_not_called()
    assert axlf.fileReport.statusDict == {}


def test_analyseXMLSummary_partInput_success(axlf):
    """Test success scenario with part input part of the input data list."""
    # Input is 'part' and is part of the input data list but the number of events is not -1
    axlf.inputDataList = ["00012478_00000532_1.sim"]
    axlf.numberOfEvents = 1

    xml_content = dedent(
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
                        status="part">200</file>
                </input>
                <output>
                        <file GUID="229BBEF1-66E9-E011-BBD0-003048F35252" name="PFN:00012478_00000532_2.xdigi"
                        status="full">200</file>
                </output>
        </summary>
        """
    )
    axlf.XMLSummary_o = prepare_XMLSummary_file(axlf.XMLSummary, xml_content)

    assert axlf.XMLSummary_o.success == "True"
    assert axlf.XMLSummary_o.step == "finalize"
    assert axlf.XMLSummary_o._outputsOK()
    assert not axlf.XMLSummary_o.inputFileStats["mult"]
    assert not axlf.XMLSummary_o.inputFileStats["other"]
    assert axlf.execute(
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
    axlf.jobReport.setApplicationStatus.assert_called_once()
    axlf.nc.sendMail.assert_not_called()
    assert axlf.fileReport.statusDict == {}


def test_analyseXMLSummary_notSuccess_fail(axlf):
    """Test failure scenario with success=False."""
    xml_content = dedent(
        """<?xml version="1.0" encoding="UTF-8"?>
        <summary version="1.0" xsi:noNamespaceSchemaLocation="$XMLSUMMARYBASEROOT/xml/XMLSummary.xsd"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <success>False</success>
                <step>finalize</step>
                <usage>
                        <stat unit="KB" useOf="MemoryMaximum">866104.0</stat>
                </usage>
                <input>
                        <file GUID="CCE96707-4BE9-E011-81CD-003048F35252" name="LFN:00012478_00000532_1.sim"
                        status="part">200</file>
                </input>
                <output>
                        <file GUID="229BBEF1-66E9-E011-BBD0-003048F35252" name="PFN:00012478_00000532_2.xdigi"
                        status="full">200</file>
                </output>
        </summary>
        """
    )
    axlf.XMLSummary_o = prepare_XMLSummary_file(axlf.XMLSummary, xml_content)

    assert axlf.XMLSummary_o.success == "False"
    assert axlf.XMLSummary_o.step == "finalize"
    assert axlf.XMLSummary_o._outputsOK()
    assert not axlf.XMLSummary_o.inputFileStats["mult"]
    assert not axlf.XMLSummary_o.inputFileStats["other"]
    assert not axlf.execute(
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
    axlf.jobReport.setApplicationStatus.assert_called_once()
    axlf.nc.sendMail.assert_called_once()
    assert axlf.fileReport.statusDict == {}


def test_analyseXMLSummary_badStep_fail(axlf):
    """Test failure scenario with step != finalize."""
    xml_content = dedent(
        """<?xml version="1.0" encoding="UTF-8"?>
        <summary version="1.0" xsi:noNamespaceSchemaLocation="$XMLSUMMARYBASEROOT/xml/XMLSummary.xsd"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                <success>True</success>
                <step>execute</step>
                <usage>
                        <stat unit="KB" useOf="MemoryMaximum">866104.0</stat>
                </usage>
                <input>
                        <file GUID="CCE96707-4BE9-E011-81CD-003048F35252" name="LFN:00012478_00000532_1.sim"
                        status="part">200</file>
                </input>
                <output>
                        <file GUID="229BBEF1-66E9-E011-BBD0-003048F35252" name="PFN:00012478_00000532_2.xdigi"
                        status="full">200</file>
                </output>
        </summary>
        """
    )
    axlf.XMLSummary_o = prepare_XMLSummary_file(axlf.XMLSummary, xml_content)

    assert axlf.XMLSummary_o.success == "True"
    assert axlf.XMLSummary_o.step == "execute"
    assert axlf.XMLSummary_o._outputsOK()
    assert not axlf.XMLSummary_o.inputFileStats["mult"]
    assert not axlf.XMLSummary_o.inputFileStats["other"]
    assert not axlf.execute(
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
    axlf.jobReport.setApplicationStatus.assert_called_once()
    axlf.nc.sendMail.assert_called_once()
    assert axlf.fileReport.statusDict == {}


def test_analyseXMLSummary_badOutput_fail(axlf):
    """Test failure scenario with output status != full."""
    xml_content = dedent(
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
                        status="part">200</file>
                </input>
                <output>
                        <file GUID="229BBEF1-66E9-E011-BBD0-003048F35252" name="PFN:00012478_00000532_2.xdigi"
                        status="fail">200</file>
                </output>
        </summary>
        """
    )
    axlf.XMLSummary_o = prepare_XMLSummary_file(axlf.XMLSummary, xml_content)

    assert axlf.XMLSummary_o.success == "True"
    assert axlf.XMLSummary_o.step == "finalize"
    assert not axlf.XMLSummary_o._outputsOK()
    assert not axlf.XMLSummary_o.inputFileStats["mult"]
    assert not axlf.XMLSummary_o.inputFileStats["other"]
    assert not axlf.execute(
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
    axlf.jobReport.setApplicationStatus.assert_called_once()
    axlf.nc.sendMail.assert_called_once()
    assert axlf.fileReport.statusDict == {}


def test_analyseXMLSummary_badInput_fail(axlf):
    """Test failure scenario with input status = mult."""
    xml_content = dedent(
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
                        status="mult">200</file>
                </input>
                <output>
                        <file GUID="229BBEF1-66E9-E011-BBD0-003048F35252" name="PFN:00012478_00000532_2.xdigi"
                        status="full">200</file>
                </output>
        </summary>
        """
    )
    axlf.XMLSummary_o = prepare_XMLSummary_file(axlf.XMLSummary, xml_content)

    assert axlf.XMLSummary_o.success == "True"
    assert axlf.XMLSummary_o.step == "finalize"
    assert axlf.XMLSummary_o._outputsOK()
    assert axlf.XMLSummary_o.inputFileStats["mult"]
    assert not axlf.XMLSummary_o.inputFileStats["other"]
    assert not axlf.execute(
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
    axlf.jobReport.setApplicationStatus.assert_called_once()
    axlf.nc.sendMail.assert_called_once()
    assert axlf.fileReport.statusDict == {}


def test_analyseXMLSummary_badInput2_fail(axlf):
    """Test failure scenario with an unknown input status (weoweo)."""
    xml_content = dedent(
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
                        status="weoweo">200</file>
                </input>
                <output>
                        <file GUID="229BBEF1-66E9-E011-BBD0-003048F35252" name="PFN:00012478_00000532_2.xdigi"
                        status="full">200</file>
                </output>
        </summary>
        """
    )
    axlf.XMLSummary_o = prepare_XMLSummary_file(axlf.XMLSummary, xml_content)

    assert axlf.XMLSummary_o.success == "True"
    assert axlf.XMLSummary_o.step == "finalize"
    assert axlf.XMLSummary_o._outputsOK()
    assert not axlf.XMLSummary_o.inputFileStats["mult"]
    assert axlf.XMLSummary_o.inputFileStats["other"]
    assert not axlf.execute(
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
    axlf.jobReport.setApplicationStatus.assert_called_once()
    axlf.nc.sendMail.assert_called_once()
    assert axlf.fileReport.statusDict == {}


def test_analyseXMLSummary_badInput3_fail(axlf):
    """Test failure scenario with input status = fail."""
    axlf.inputDataList = ["00012478_00000532_1.sim"]

    xml_content = dedent(
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
    axlf.XMLSummary_o = prepare_XMLSummary_file(axlf.XMLSummary, xml_content)

    assert axlf.XMLSummary_o.success == "True"
    assert axlf.XMLSummary_o.step == "finalize"
    assert axlf.XMLSummary_o._outputsOK()
    assert not axlf.XMLSummary_o.inputFileStats["mult"]
    assert not axlf.XMLSummary_o.inputFileStats["other"]
    assert not axlf.execute(
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
    axlf.jobReport.setApplicationStatus.assert_called_once()
    axlf.nc.sendMail.assert_called_once()
    assert axlf.fileReport.statusDict == {"00012478_00000532_1.sim": "Problematic"}


def test_analyseXMLSummary_badInput4_fail(axlf):
    """Test failure scenario with input status = part."""
    # Input is 'part' and is part of the input data list but the number of events is -1 (by default)
    axlf.inputDataList = ["00012478_00000532_1.sim"]

    xml_content = dedent(
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
                        status="part">200</file>
                        <file GUID="CCE96709-5BE9-E012-41BD-004048E36253" name="LFN:00012478_00000533_1.sim"
                        status="part">200</file>
                </input>
                <output>
                        <file GUID="229BBEF1-66E9-E011-BBD0-003048F35252" name="PFN:00012478_00000532_2.xdigi"
                        status="full">200</file>
                </output>
        </summary>
        """
    )
    axlf.XMLSummary_o = prepare_XMLSummary_file(axlf.XMLSummary, xml_content)

    assert axlf.XMLSummary_o.success == "True"
    assert axlf.XMLSummary_o.step == "finalize"
    assert axlf.XMLSummary_o._outputsOK()
    assert not axlf.XMLSummary_o.inputFileStats["mult"]
    assert not axlf.XMLSummary_o.inputFileStats["other"]
    assert not axlf.execute(
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
    axlf.jobReport.setApplicationStatus.assert_called_once()
    axlf.nc.sendMail.assert_called_once()
    assert axlf.fileReport.statusDict == {"00012478_00000532_1.sim": "Problematic"}
