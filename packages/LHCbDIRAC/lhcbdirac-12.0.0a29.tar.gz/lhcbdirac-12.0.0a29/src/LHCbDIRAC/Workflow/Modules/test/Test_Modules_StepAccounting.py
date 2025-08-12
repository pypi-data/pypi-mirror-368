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

from textwrap import dedent
import pytest
from pathlib import Path

from DIRAC import S_OK, S_ERROR
from LHCbDIRAC.Core.Utilities.XMLSummaries import XMLSummary
from LHCbDIRAC.Workflow.Modules.StepAccounting import StepAccounting
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
XML_SUMMARY_FILE = "XMLSummary.xml"


def prepare_XMLSummary_file(xml_summary, content):
    with open(xml_summary, "w") as f:
        f.write(content)
    return XMLSummary(xml_summary)


@pytest.fixture
def accounting(mocker):
    """Fixture for StepAccounting module."""
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator")
    mocker.patch("LHCbDIRAC.Workflow.Modules.StepAccounting.StepAccounting._resolveInputVariables")

    step_acc = StepAccounting()
    step_acc.jobID = wms_job_id
    mocker.patch.object(step_acc, "dsc", autospec=True)

    yield step_acc

    Path(XML_SUMMARY_FILE).unlink(missing_ok=True)


# Test Scenarios
def test_accounting_success(accounting):
    """Test successful execution of StepAccounting module."""
    # Mock the StepAccounting module
    accounting.step_commons = {
        "applicationName": "Gauss",
    }
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
    accounting.step_commons["XMLSummary_o"] = prepare_XMLSummary_file(XML_SUMMARY_FILE, xml_content)

    accounting.BKstepID = "12345"
    accounting.stepProcPass = "Sim09m"
    accounting.eventType = "23103003"
    accounting.stepStat = "Done"

    assert accounting.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=accounting.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"], "Execution should succeed."

    # Make sure the dsc was called
    accounting.dsc.addRegister.assert_called_once()


def test_accounting_noApplicationName_success(accounting):
    """Test StepAccounting when there is no application name in step commons."""
    # Mock the StepAccounting module
    accounting.step_commons = {}

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
    accounting.step_commons["XMLSummary_o"] = prepare_XMLSummary_file(XML_SUMMARY_FILE, xml_content)

    assert accounting.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=accounting.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"]

    assert not accounting.dsc.addRegister.called, "No accounting data should be added."


def test_accounting_incompleteData(accounting):
    """Test successful execution of StepAccounting module."""
    # Mock the StepAccounting module
    accounting.step_commons = {
        "applicationName": "Gauss",
    }
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
    accounting.step_commons["XMLSummary_o"] = prepare_XMLSummary_file(XML_SUMMARY_FILE, xml_content)

    assert not accounting.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=accounting.step_commons,
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"], "Execution should not succeed."

    assert not accounting.dsc.addRegister.called, "No accounting data should be added."


def test_accounting_previousError_fail(accounting):
    """Test StepAccounting with an intentional failure."""
    # Mock the StepAccounting module
    accounting.step_commons = {
        "applicationName": "Gauss",
    }
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
    accounting.step_commons["XMLSummary_o"] = prepare_XMLSummary_file(XML_SUMMARY_FILE, xml_content)

    accounting.BKstepID = "12345"
    accounting.stepProcPass = "Sim09m"
    accounting.eventType = "23103003"

    # Intentional error
    accounting.stepStat = "Failed"

    assert accounting.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=accounting.step_commons,
        step_number=step_number,
        step_id=step_id,
        # Intentional error
        stepStatus=S_ERROR(),
    )["OK"]

    assert accounting.dsc.addRegister.called, "Accounting data should be added."
