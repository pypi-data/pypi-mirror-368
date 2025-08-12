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
"""Test class for BookkeepingReport."""

import os
import time
import pytest
import xml.etree.ElementTree as ET

from pathlib import Path
from textwrap import dedent

import DIRAC
import LHCbDIRAC

from DIRAC import S_OK, S_ERROR
from LHCbDIRAC.Core.Utilities.XMLSummaries import XMLSummary
from LHCbDIRAC.Workflow.Modules.BookkeepingReport import BookkeepingReport
from LHCbDIRAC.Workflow.Modules.test.mock_Commons import (
    prod_id,
    prod_job_id,
    wms_job_id,
    workflowStatus,
    step_id,
    step_number,
    step_commons,
    wf_commons,
)


# Helper Functions
XML_SUMMARY_FILE = "XMLSummary.xml"
POOL_CATALOG_FILE = "pool_xml_catalog.xml"


def prepare_XMLSummary_file(xml_summary, content):
    with open(xml_summary, "w") as f:
        f.write(content)
    return XMLSummary(xml_summary)


def get_typed_parameter_value(name, root):
    """Find the value of a specific TypedParameter by its name."""
    for child in root:
        if child.tag == "TypedParameter" and child.attrib["Name"] == name:
            return child.attrib["Value"]
    return None


def get_output_file_details(output_file):
    """Extract details from an OutputFile element."""
    details = {
        "Name": output_file.attrib["Name"],
        "TypeName": output_file.attrib["TypeName"],
        "Parameters": {},
        "Replicas": [],
    }

    for elem in output_file:
        if elem.tag == "Parameter":
            details["Parameters"][elem.attrib["Name"]] = elem.attrib["Value"]
        elif elem.tag == "Replica":
            details["Replicas"].append({"Name": elem.attrib["Name"], "Location": elem.attrib["Location"]})

    return details


@pytest.fixture
def bkreport(mocker):
    """Fixture for BookkeepingReport module."""
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator")
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.ModuleBase._resolveInputVariables")
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.ModuleBase._resolveInputStep")

    bkreport = BookkeepingReport()
    mocker.patch.object(bkreport, "jobReport", autospec=True)
    bkreport.jobReport.setApplicationStatus.return_value = S_OK()

    step_commons[0]["listoutput"] = []
    step_commons[0]["inputData"] = []
    wf_commons[0].pop("BookkeepingLFNs", None)
    wf_commons[0].pop("LogFilePath", None)
    wf_commons[0].pop("ProductionOutputData", None)

    yield bkreport

    # Teardown
    xml_filename = f"bookkeeping_{step_id}.xml"
    Path(xml_filename).unlink(missing_ok=True)
    Path(XML_SUMMARY_FILE).unlink(missing_ok=True)
    Path(POOL_CATALOG_FILE).unlink(missing_ok=True)
    if bkreport.applicationLog:
        Path(bkreport.applicationLog).unlink(missing_ok=True)
    for output in step_commons[0]["listoutput"]:
        Path(output["outputDataName"]).unlink(missing_ok=True)


# Test Scenarios
def test_bkreport_prod_mcsimulation_success(bkreport):
    """Test successful execution of BookkeepingReport module."""
    # Mock the BookkeepingReport module
    bkreport.applicationName = "Gauss"
    bkreport.applicationVersion = "v49r10"
    bkreport.jobType = "MCSimulation"

    # This was obtained from a previous module (likely GaudiApplication)
    wf_commons[0]["BookkeepingLFNs"] = ["/lhcb/LHCb/Collision16/SIM/00209455/0000/00209455_00001537_1.sim"]
    wf_commons[0]["LogFilePath"] = "/lhcb/LHCb/Collision16/LOG/00209455/0000/"
    wf_commons[0]["ProductionOutputData"] = ["/lhcb/LHCb/Collision16/SIM/00209455/0000/00209455_00001537_1.sim"]

    step_commons[0]["StartTime"] = time.time() - 1000

    # Add input and output files
    # Input data should be None as we use Gauss (MCSimulation)
    step_commons[0]["inputData"] = None
    step_commons[0]["listoutput"] = [
        {"outputDataName": "00209455_00001537_1.sim", "outputDataType": "sim"},
    ]
    bkreport.applicationLog = "application.log"
    Path(bkreport.applicationLog).touch()
    Path(step_commons[0]["listoutput"][0]["outputDataName"]).touch()

    # Mock the XMLSummary object
    xml_content = dedent(
        """<?xml version="1.0" encoding="UTF-8"?>
        <summary xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.0"
        xsi:noNamespaceSchemaLocation="$XMLSUMMARYBASEROOT/xml/XMLSummary.xsd">
            <success>True</success>
            <step>finalize</step>
            <usage>
                <stat useOf="MemoryMaximum" unit="KB">2129228.0</stat>
            </usage>
            <input />
            <output>
                <file GUID="F2A331E0-C977-11EE-8689-D85ED3091B7C" name="PFN:00209455_00001537_1.sim" status="full">1</file>
            </output>
            <counters>
                <counter name="ConversionFilter/event with gamma conversion from">1</counter>
                <counter name="GaussGeo.Hcal/#energy">77</counter>
                <counter name="GaussGeo.Hcal/#hits">2644</counter>
                <counter name="GaussGeo.Hcal/#subhits">6262</counter>
                <counter name="GaussGeo.Hcal/#tslots">8391</counter>
                <counter name="GaussGeo.Ecal/#energy">963</counter>
                <counter name="GaussGeo.Ecal/#hits">18139</counter>
                <counter name="GaussGeo.Ecal/#subhits">45169</counter>
                <counter name="GaussGeo.Ecal/#tslots">52237</counter>
                <counter name="CounterSummarySvc/handled">79</counter>
            </counters>
            <lumiCounters />
        </summary>
        """
    )

    step_commons[0]["XMLSummary_o"] = prepare_XMLSummary_file(XML_SUMMARY_FILE, xml_content)

    # Pool XML catalog content
    pool_xml_content = dedent(
        """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
        <!-- Edited By POOL -->
        <!DOCTYPE POOLFILECATALOG SYSTEM "InMemory">
        <POOLFILECATALOG>
        <File ID="F2A331E0-C977-11EE-8689-D85ED3091B7C">
            <physical>
            <pfn filetype="ROOT" name="00209455_00001537_1.sim"/>
            </physical>
            <logical/>
        </File>
        </POOLFILECATALOG>
        """
    )
    with open(POOL_CATALOG_FILE, "w") as f:
        f.write(pool_xml_content)

    # Execute the module
    assert bkreport.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=step_commons[0],
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"], "Execution should succeed."

    # Check if the XML report file is created
    xml_filename = f"bookkeeping_{step_id}.xml"
    assert Path(xml_filename).exists(), "XML report file not created."

    # Validate the XML file
    tree = ET.parse(xml_filename)
    root = tree.getroot()

    # Extract fields from the XML and perform further operations
    assert root.tag == "Job", "Root tag should be Job."
    assert root.attrib["ConfigName"] == "aConfigName"
    assert root.attrib["ConfigVersion"] == "aConfigVersion"
    assert root.attrib["Date"] == bkreport.ldate
    assert root.attrib["Time"] == bkreport.ltime

    assert get_typed_parameter_value("ProgramName", root) == bkreport.applicationName
    assert get_typed_parameter_value("ProgramVersion", root) == bkreport.applicationVersion
    assert get_typed_parameter_value("DiracVersion", root) == LHCbDIRAC.__version__
    assert get_typed_parameter_value("Name", root) == step_id
    assert float(get_typed_parameter_value("ExecTime", root)) > 1000
    assert get_typed_parameter_value("CPUTIME", root) == "0"

    assert get_typed_parameter_value("FirstEventNumber", root) == "1"
    assert get_typed_parameter_value("StatisticsRequested", root) == str(bkreport.numberOfEvents)
    assert get_typed_parameter_value("NumberOfEvents", root) == str(bkreport.xf_o.outputEventsTotal)

    assert get_typed_parameter_value("Production", root) == prod_id
    assert get_typed_parameter_value("DiracJobId", root) == str(wms_job_id)
    assert get_typed_parameter_value("Location", root) == DIRAC.siteName()
    assert get_typed_parameter_value("JobStart", root) == f"{bkreport.ldatestart} {bkreport.ltimestart}"
    assert get_typed_parameter_value("JobEnd", root) == f"{bkreport.ldate} {bkreport.ltime}"
    assert get_typed_parameter_value("JobType", root) == "MCSimulation"

    assert get_typed_parameter_value("WorkerNode", root)
    assert get_typed_parameter_value("WNMEMORY", root)
    assert get_typed_parameter_value("WNCPUPOWER", root)
    assert get_typed_parameter_value("WNMODEL", root)
    assert get_typed_parameter_value("WNCACHE", root)
    assert get_typed_parameter_value("WNCPUHS06", root)
    assert get_typed_parameter_value("NumberOfProcessors", root) == str(bkreport.numberOfProcessors)

    # Input should be empty
    input_file = root.find("InputFile")
    assert input_file is None, "InputFile element should not be present."

    # Output should not be empty
    output_files = root.findall("OutputFile")
    assert output_files, "No OutputFile elements found."

    first_output_details = get_output_file_details(output_files[0])
    assert first_output_details["Name"] == wf_commons[0]["ProductionOutputData"][0]
    assert first_output_details["TypeName"] == "SIM"
    assert first_output_details["Parameters"]["FileSize"] == "0"
    assert "CreationDate" in first_output_details["Parameters"]
    assert "MD5Sum" in first_output_details["Parameters"]
    assert "Guid" in first_output_details["Parameters"]

    second_output_details = get_output_file_details(output_files[1])
    assert os.path.basename(second_output_details["Name"]) == bkreport.applicationLog
    assert second_output_details["TypeName"] == "LOG"
    assert second_output_details["Parameters"]["FileSize"] == "0"
    assert "CreationDate" in second_output_details["Parameters"]
    assert "MD5Sum" in second_output_details["Parameters"]
    assert "Guid" in second_output_details["Parameters"]
    assert second_output_details["Replicas"] == [
        {
            "Name": f"http://lhcb-logs.cern.ch/storage{wf_commons[0]['LogFilePath']}/{bkreport.applicationLog}",
            "Location": "Web",
        }
    ]


def test_bkreport_prod_mcsimulation_noinputoutput_success(bkreport):
    """Test successful execution of BookkeepingReport module:

    * No input files because bkreport.stepInputData is empty
    * No output files because bkreport.stepOutputData is empty
    * No pool xml catalog
    * Simulation conditions because the application used is Gauss
    """
    # Mock the BookkeepingReport module
    bkreport.applicationName = "Gauss"
    bkreport.applicationVersion = "v49r10"
    bkreport.jobType = "MCSimulation"

    # This was obtained from a previous module (likely GaudiApplication)
    wf_commons[0]["BookkeepingLFNs"] = ["/lhcb/LHCb/Collision16/SIM/00209455/0000/00209455_00001537_1"]
    wf_commons[0]["LogFilePath"] = "/lhcb/LHCb/Collision16/LOG/00209455/0000/"
    wf_commons[0]["ProductionOutputData"] = ["/lhcb/LHCb/Collision16/SIM/00209455/0000/00209455_00001537_1"]

    step_commons[0]["StartTime"] = time.time() - 1000

    # Mock the XMLSummary object
    xml_content = dedent(
        """<?xml version="1.0" encoding="UTF-8"?>
        <summary xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.0"
        xsi:noNamespaceSchemaLocation="$XMLSUMMARYBASEROOT/xml/XMLSummary.xsd">
            <success>True</success>
            <step>finalize</step>
            <usage>
                <stat useOf="MemoryMaximum" unit="KB">2129228.0</stat>
            </usage>
            <input />
            <output>
                <file GUID="F2A331E0-C977-11EE-8689-D85ED3091B7C" name="PFN:00211518_00024143_1.sim" status="full">1</file>
            </output>
            <counters>
                <counter name="ConversionFilter/event with gamma conversion from">1</counter>
                <counter name="GaussGeo.Hcal/#energy">77</counter>
                <counter name="GaussGeo.Hcal/#hits">2644</counter>
                <counter name="GaussGeo.Hcal/#subhits">6262</counter>
                <counter name="GaussGeo.Hcal/#tslots">8391</counter>
                <counter name="GaussGeo.Ecal/#energy">963</counter>
                <counter name="GaussGeo.Ecal/#hits">18139</counter>
                <counter name="GaussGeo.Ecal/#subhits">45169</counter>
                <counter name="GaussGeo.Ecal/#tslots">52237</counter>
                <counter name="CounterSummarySvc/handled">79</counter>
            </counters>
            <lumiCounters />
        </summary>
        """
    )

    step_commons[0]["XMLSummary_o"] = prepare_XMLSummary_file(XML_SUMMARY_FILE, xml_content)

    # Execute the module
    assert bkreport.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=step_commons[0],
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"], "Execution should succeed."

    # Check if the XML report file is created
    xml_filename = f"bookkeeping_{step_id}.xml"
    assert Path(xml_filename).exists(), "XML report file not created."

    # Validate the XML file
    tree = ET.parse(xml_filename)
    root = tree.getroot()

    # Extract fields from the XML and perform further operations
    assert root.tag == "Job", "Root tag should be Job."
    assert root.attrib["ConfigName"] == "aConfigName"
    assert root.attrib["ConfigVersion"] == "aConfigVersion"
    assert root.attrib["Date"] == bkreport.ldate
    assert root.attrib["Time"] == bkreport.ltime

    assert get_typed_parameter_value("ProgramName", root) == bkreport.applicationName
    assert get_typed_parameter_value("ProgramVersion", root) == bkreport.applicationVersion
    assert get_typed_parameter_value("DiracVersion", root) == LHCbDIRAC.__version__
    assert get_typed_parameter_value("Name", root) == step_id
    assert float(get_typed_parameter_value("ExecTime", root)) > 1000
    assert get_typed_parameter_value("CPUTIME", root) == "0"

    assert get_typed_parameter_value("FirstEventNumber", root) == "1"
    assert get_typed_parameter_value("StatisticsRequested", root) == str(bkreport.numberOfEvents)
    assert get_typed_parameter_value("NumberOfEvents", root) == str(bkreport.xf_o.outputEventsTotal)

    assert get_typed_parameter_value("Production", root) == prod_id
    assert get_typed_parameter_value("DiracJobId", root) == str(wms_job_id)
    assert get_typed_parameter_value("Location", root) == DIRAC.siteName()
    assert get_typed_parameter_value("JobStart", root) == f"{bkreport.ldatestart} {bkreport.ltimestart}"
    assert get_typed_parameter_value("JobEnd", root) == f"{bkreport.ldate} {bkreport.ltime}"
    assert get_typed_parameter_value("JobType", root) == "MCSimulation"

    assert get_typed_parameter_value("WorkerNode", root)
    assert get_typed_parameter_value("WNMEMORY", root)
    assert get_typed_parameter_value("WNCPUPOWER", root)
    assert get_typed_parameter_value("WNMODEL", root)
    assert get_typed_parameter_value("WNCACHE", root)
    assert get_typed_parameter_value("WNCPUHS06", root)
    assert get_typed_parameter_value("NumberOfProcessors", root) == str(bkreport.numberOfProcessors)

    # Input should be empty
    input_file = root.find("InputFile")
    assert input_file is None, "InputFile element should not be present."

    # Output should be empty
    output_file = root.find("OutputFile")
    assert output_file is None, "OutputFile element should not be present."


def test_bkreport_prod_mcreconstruction_success(bkreport):
    """Test successful execution of BookkeepingReport module."""
    # Mock the BookkeepingReport module
    bkreport.applicationName = "Boole"
    bkreport.applicationVersion = "v49r10"
    bkreport.jobType = "MCReconstruction"

    # This was obtained from a previous module (likely GaudiApplication)
    wf_commons[0]["BookkeepingLFNs"] = ["/lhcb/LHCb/Collision16/SIM/00209455/0000/00209455_00001537_1"]
    wf_commons[0]["LogFilePath"] = "/lhcb/LHCb/Collision16/LOG/00209455/0000/"
    wf_commons[0]["ProductionOutputData"] = ["/lhcb/LHCb/Collision16/SIM/00209455/0000/00209455_00001537_1"]

    step_commons[0]["StartTime"] = time.time() - 1000

    # Add input and output files
    step_commons[0]["inputData"] = "/lhcb/MC/2018/SIM/00212581/0000/00212581_00001446_1.sim"
    step_commons[0]["listoutput"] = [
        {"outputDataName": "00209455_00001537_1", "outputDataType": "digi"},
    ]
    bkreport.applicationLog = "application.log"
    Path(bkreport.applicationLog).touch()
    Path(step_commons[0]["listoutput"][0]["outputDataName"]).touch()

    # Mock the XMLSummary object
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
                        <file GUID="CCE96707-4BE9-E011-81CD-003048F35252" name="LFN:0209455_00001537_1.sim"
                        status="full">200</file>
                </input>
                <output>
                        <file GUID="229BBEF1-66E9-E011-BBD0-003048F35252" name="PFN:00012478_00000532_2.xdigi"
                        status="full">200</file>
                </output>
        </summary>
        """
    )

    step_commons[0]["XMLSummary_o"] = prepare_XMLSummary_file(XML_SUMMARY_FILE, xml_content)

    # Execute the module
    assert bkreport.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=step_commons[0],
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"], "Execution should succeed."

    # Check if the XML report file is created
    xml_filename = f"bookkeeping_{step_id}.xml"
    assert Path(xml_filename).exists(), "XML report file not created."

    # Validate the XML file
    tree = ET.parse(xml_filename)
    root = tree.getroot()

    # Extract fields from the XML and perform further operations
    assert root.tag == "Job", "Root tag should be Job."
    assert root.attrib["ConfigName"] == "aConfigName"
    assert root.attrib["ConfigVersion"] == "aConfigVersion"
    assert root.attrib["Date"] == bkreport.ldate
    assert root.attrib["Time"] == bkreport.ltime

    assert get_typed_parameter_value("ProgramName", root) == bkreport.applicationName
    assert get_typed_parameter_value("ProgramVersion", root) == bkreport.applicationVersion
    assert get_typed_parameter_value("DiracVersion", root) == LHCbDIRAC.__version__
    assert get_typed_parameter_value("Name", root) == step_id
    assert float(get_typed_parameter_value("ExecTime", root)) > 1000
    assert get_typed_parameter_value("CPUTIME", root) == "0"

    assert get_typed_parameter_value("FirstEventNumber", root) == "1"
    assert get_typed_parameter_value("StatisticsRequested", root) == str(bkreport.numberOfEvents)
    assert get_typed_parameter_value("NumberOfEvents", root) == str(bkreport.xf_o.inputEventsTotal)

    assert get_typed_parameter_value("Production", root) == prod_id
    assert get_typed_parameter_value("DiracJobId", root) == str(wms_job_id)
    assert get_typed_parameter_value("Location", root) == DIRAC.siteName()
    assert get_typed_parameter_value("JobStart", root) == f"{bkreport.ldatestart} {bkreport.ltimestart}"
    assert get_typed_parameter_value("JobEnd", root) == f"{bkreport.ldate} {bkreport.ltime}"
    assert get_typed_parameter_value("JobType", root) == "MCReconstruction"

    assert get_typed_parameter_value("WorkerNode", root)
    assert get_typed_parameter_value("WNMEMORY", root)
    assert get_typed_parameter_value("WNCPUPOWER", root)
    assert get_typed_parameter_value("WNMODEL", root)
    assert get_typed_parameter_value("WNCACHE", root)
    assert get_typed_parameter_value("WNCPUHS06", root)
    assert get_typed_parameter_value("NumberOfProcessors", root) == str(bkreport.numberOfProcessors)

    # Input should be empty
    input_file = root.find("InputFile")
    assert input_file is None, "InputFile element should not be present."

    # Output should not be empty
    output_files = root.findall("OutputFile")
    assert output_files, "No OutputFile elements found."

    first_output_details = get_output_file_details(output_files[0])
    assert first_output_details["Name"] == wf_commons[0]["ProductionOutputData"][0]
    assert first_output_details["TypeName"] == "DIGI"
    assert first_output_details["Parameters"]["FileSize"] == "0"
    assert "CreationDate" in first_output_details["Parameters"]
    assert "MD5Sum" in first_output_details["Parameters"]
    assert "Guid" in first_output_details["Parameters"]

    second_output_details = get_output_file_details(output_files[1])
    assert os.path.basename(second_output_details["Name"]) == bkreport.applicationLog
    assert second_output_details["TypeName"] == "LOG"
    assert second_output_details["Parameters"]["FileSize"] == "0"
    assert "CreationDate" in second_output_details["Parameters"]
    assert "MD5Sum" in second_output_details["Parameters"]
    assert "Guid" in second_output_details["Parameters"]
    assert second_output_details["Replicas"] == [
        {
            "Name": f"http://lhcb-logs.cern.ch/storage{wf_commons[0]['LogFilePath']}/{bkreport.applicationLog}",
            "Location": "Web",
        }
    ]

    # Because we are using Gauss, sim conditions should be present too
    simulation_condition = root.find("SimulationCondition")
    assert simulation_condition is None, "SimulationCondition element should not be present."


def test_bkreport_previousError_success(bkreport):
    """Test BookkeepingReport with a previous error."""
    # Mock the BookkeepingReport module
    bkreport.applicationName = "Gauss"
    bkreport.applicationVersion = "v49r10"
    bkreport.jobType = "MCSimulation"

    # Execute the module
    assert bkreport.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=step_commons[0],
        step_number=step_number,
        step_id=step_id,
        # An error occurred in a previous step
        stepStatus=S_ERROR(),
    )["OK"], "Execution should succeed."

    # Check if the XML report file is created
    xml_filename = f"bookkeeping_{step_id}.xml"
    assert not Path(xml_filename).exists(), "XML report file was created."
