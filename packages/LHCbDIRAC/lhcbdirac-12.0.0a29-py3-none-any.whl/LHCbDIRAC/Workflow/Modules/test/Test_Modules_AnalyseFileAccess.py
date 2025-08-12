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
"""Test the AnalyseFileAccess module.
"""
import pytest

from pathlib import Path
from textwrap import dedent

from DIRAC import S_OK
from DIRAC.Resources.Catalog.PoolXMLCatalog import PoolXMLCatalog
from LHCbDIRAC.Core.Utilities.XMLSummaries import XMLSummary
from LHCbDIRAC.Workflow.Modules.AnalyseFileAccess import AnalyseFileAccess
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

# Helper functions
XML_SUMMARY_FILE = "XMLSummary.xml"
POOL_XML_CATALOG_FILE = "pool_xml_catalog.xml"


def prepare_XMLSummary_file(xml_summary, content):
    with open(xml_summary, "w") as f:
        f.write(content)
    return XMLSummary(xml_summary)


def prepare_PoolXMLCatalog_file(pool_xml_catalog, content):
    with open(pool_xml_catalog, "w") as f:
        f.write(content)
    return PoolXMLCatalog(xmlfile=pool_xml_catalog)


@pytest.fixture
def afa(mocker):
    """Fixture for AnalyseFileAccess module."""
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator")
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.ModuleBase._resolveInputVariables")
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.ModuleBase._resolveInputStep")
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.ModuleBase._getCurrentOwner", return_value="test_cl")

    afa = AnalyseFileAccess()
    afa.poolXMLCatName = POOL_XML_CATALOG_FILE
    afa.XMLSummary = XML_SUMMARY_FILE

    yield afa

    # Teardown
    Path(XML_SUMMARY_FILE).unlink(missing_ok=True)
    Path(POOL_XML_CATALOG_FILE).unlink(missing_ok=True)


# Test scenarios
def test_analyseFileAccess_success(afa):
    """Analyze the file accesses from a pool xml catalog and the xml summary.

    We use test pool and summary xml files that correspond to 3 LFNs:
    * one that worked at the first attempt
    * one that worked at the second attempt
    * one that did not work at all
    """
    xml_content = dedent(
        """<?xml version="1.0" encoding="UTF-8"?>
        <summary xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.0"
        xsi:noNamespaceSchemaLocation="$XMLSUMMARYBASEROOT/xml/XMLSummary.xsd">
        <success>False</success>
        <step>finalize</step>
        <usage>
                <stat unit="KB" useOf="MemoryMaximum">1149708.0</stat>
        </usage>
        <input>
                <file GUID=""
                name="LFN:/lhcb/LHCb/Collision17/CHARMCOMPLETEEVENT.DST/00071907/0001/00071907_00016993_1.charmcompleteevent.dst"
                status="full">47847</file>
                <file GUID=""
                name="LFN:/lhcb/LHCb/Collision17/CHARMCOMPLETEEVENT.DST/00071501/0002/00071501_00024707_1.charmcompleteevent.dst"
                status="full">35009</file>
                <file GUID=""
                name="PFN:root://xrootd.echo.stfc.ac.uk/lhcb:prod/lhcb/LHCb/Collision17/CHARMCOMPLETEEVENT.DST/00071501/0002/00071501_00024707_1.charmcompleteevent.dstNOTEXISTING"
                status="fail">0</file>
                <file GUID=""
                name="LFN:/lhcb/LHCb/Collision17/CHARMCOMPLETEEVENT.DST/00071571/0002/00071571_00023182_1.charmcompleteevent.dst"
                status="fail">0</file>
                <file GUID=""
                name="PFN:root://xrootd.echo.stfc.ac.uk/lhcb:prod/lhcb/LHCb/Collision17/CHARMCOMPLETEEVENT.DST/00071571/0002/00071571_00023182_1.charmcompleteevent.dstWILLFAIL"
                status="fail">0</file>
                <file GUID=""
                name="PFN:root://marsedpm.in2p3.fr:1094//dpm/in2p3.fr/home/lhcb/LHCb/Collision17/CHARMCOMPLETEEVENT.DST/00071571/0002/00071571_00023182_1.charmcompleteevent.dstWILLFAIL"
                status="fail">0</file>
        </input>
        <output />
        <counters>
                <counter name="CounterSummarySvc/handled">82869</counter>
        </counters>
        <lumiCounters />
        </summary>
        """
    )
    afa.XMLSummary_o = prepare_XMLSummary_file(afa.XMLSummary, xml_content)

    pool_xml_content = dedent(
        """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
        <!DOCTYPE POOLFILECATALOG SYSTEM "InMemory">
        <POOLFILECATALOG>
        <File ID="B432CC7D-5526-E811-8835-0242AC110007">
            <physical>
                <pfn filetype="ROOT_All"
                name="root://xrootd.echo.stfc.ac.uk/lhcb:prod/lhcb/LHCb/Collision17/CHARMCOMPLETEEVENT.DST/00071907/0001/00071907_00016993_1.charmcompleteevent.dst"
                se="GOOD-DST"/>
                <pfn filetype="ROOT_All"
                name="root://marsedpm.in2p3.fr:1094//dpm/in2p3.fr/home/lhcb/LHCb/Collision17/CHARMCOMPLETEEVENT.DST/00071907/0001/00071907_00016993_1.charmcompleteevent.dst"
                se="NEVERUSED-DST"/>
            </physical>
            <logical>
                <lfn name="/lhcb/LHCb/Collision17/CHARMCOMPLETEEVENT.DST/00071907/0001/00071907_00016993_1.charmcompleteevent.dst"
                />
            </logical>
        </File>
        <File ID="2E826229-0822-E811-9FA0-0242AC11000A">
            <physical>
                <pfn filetype="ROOT_All"
                name="root://xrootd.echo.stfc.ac.uk/lhcb:prod/lhcb/LHCb/Collision17/CHARMCOMPLETEEVENT.DST/00071501/0002/00071501_00024707_1.charmcompleteevent.dstNOTEXISTING"
                se="BAD-DST"/>
                <pfn filetype="ROOT_All"
                name="root://marsedpm.in2p3.fr:1094//dpm/in2p3.fr/home/lhcb/LHCb/Collision17/CHARMCOMPLETEEVENT.DST/00071501/0002/00071501_00024707_1.charmcompleteevent.dst"
                se="GOOD-DST"/>
            </physical>
            <logical>
                <lfn name="/lhcb/LHCb/Collision17/CHARMCOMPLETEEVENT.DST/00071501/0002/00071501_00024707_1.charmcompleteevent.dst"
                />
            </logical>
        </File>
        <File ID="5A352884-4422-E811-8645-0242AC110006">
        <physical>
            <pfn filetype="ROOT_All"
            name="root://xrootd.echo.stfc.ac.uk/lhcb:prod/lhcb/LHCb/Collision17/CHARMCOMPLETEEVENT.DST/00071571/0002/00071571_00023182_1.charmcompleteevent.dstWILLFAIL"
            se="BAD-DST"/>
            <pfn filetype="ROOT_All"
            name="root://marsedpm.in2p3.fr:1094//dpm/in2p3.fr/home/lhcb/LHCb/Collision17/CHARMCOMPLETEEVENT.DST/00071571/0002/00071571_00023182_1.charmcompleteevent.dstWILLFAIL"
            se="OTHERBAD-DST"/>
        </physical>
        <logical>
            <lfn name="/lhcb/LHCb/Collision17/CHARMCOMPLETEEVENT.DST/00071571/0002/00071571_00023182_1.charmcompleteevent.dst"/>
        </logical>
        </File>
        </POOLFILECATALOG>
        """
    )
    afa.poolXMLCatName_o = prepare_PoolXMLCatalog_file(afa.poolXMLCatName, pool_xml_content)

    assert afa.execute(
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

    # Check that the commit was called 5 times
    afa.dsc.addRegister.call_count == 5
    # Get the arguments of addRegister
    arguments = afa.dsc.addRegister.call_args_list

    dataOperations = [argument[0][0].getContents() for argument in arguments]

    assert dataOperations[0]["OperationType"] == "fileAccess"
    assert dataOperations[0]["Source"] == "BAD-DST"
    assert dataOperations[0]["FinalStatus"] == "Failed"

    assert dataOperations[1]["OperationType"] == "fileAccess"
    assert dataOperations[1]["Source"] == "BAD-DST"
    assert dataOperations[1]["FinalStatus"] == "Failed"

    assert dataOperations[2]["OperationType"] == "fileAccess"
    assert dataOperations[2]["Source"] == "OTHERBAD-DST"
    assert dataOperations[2]["FinalStatus"] == "Failed"

    assert dataOperations[3]["OperationType"] == "fileAccess"
    assert dataOperations[3]["Source"] == "GOOD-DST"
    assert dataOperations[3]["FinalStatus"] == "Successful"

    assert dataOperations[4]["OperationType"] == "fileAccess"
    assert dataOperations[4]["Source"] == "GOOD-DST"
    assert dataOperations[4]["FinalStatus"] == "Successful"
