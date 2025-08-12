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
"""Unit tests for Workflow Module GaudiApplication."""
import json
import pytest

from pathlib import Path

from DIRAC import S_OK, S_ERROR
from DIRAC.DataManagementSystem.Client.test.mock_DM import dm_mock
from DIRAC.TransformationSystem.Client.FileReport import FileReport

from LHCbDIRAC.Core.Utilities.RunApplication import LHCbApplicationError, LHCbDIRACError
from LHCbDIRAC.Workflow.Modules.GaudiApplication import GaudiApplication
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


# Helper functions
@pytest.fixture
def gaudi(mocker):
    """Fixture for GaudiApplication module."""
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator")
    mocker.patch("LHCbDIRAC.Workflow.Modules.GaudiApplication.GaudiApplication._resolveInputVariables")

    gaudi = GaudiApplication(dm=dm_mock)
    mocker.patch.object(gaudi, "jobReport", autospec=True)
    gaudi.jobReport.setApplicationStatus.return_value = S_OK()

    wf_commons[0].pop("outputList", None)
    wf_commons[0].pop("BookkeepingLFNs", None)
    wf_commons[0].pop("LogFilePath", None)
    wf_commons[0].pop("ProductionOutputData", None)

    yield gaudi

    # Teardown
    Path("gaudi_extra_options.py").unlink(missing_ok=True)
    Path("DISABLE_WATCHDOG_CPU_WALLCLOCK_CHECK").unlink(missing_ok=True)
    fileName = f"{prod_id}_{prod_job_id}_{step_number}"
    Path(f"prodConf_{gaudi.applicationName}_{fileName}.json").unlink(missing_ok=True)
    Path(f"{fileName}.sim").unlink(missing_ok=True)
    Path(f"{fileName}.ift.dst").unlink(missing_ok=True)
    Path(f"{fileName}.dst").unlink(missing_ok=True)
    Path(f"{fileName}.hist").unlink(missing_ok=True)


# Test scenarios
def test_gaudi_prod_mcsimulation_basic_success(mocker, gaudi):
    """Test basic MCSimulation success scenario with default values"""
    # Mock the GaudiApplication module (MCSimulation)
    run_app_mock = mocker.patch(
        "LHCbDIRAC.Core.Utilities.RunApplication.RunApplication.run",
        return_value=S_OK((0, "Completed successfully", "")),
    )
    gaudi.applicationName = "Gauss"
    gaudi.applicationVersion = "v49r10"
    gaudi.jobType = "MCSimulation"

    # Mock the inputs: there is no input data with MCSimulation jobs
    gaudi.stepInputData = []

    # Mock the outputs
    outputFileName = f"{prod_id}_{prod_job_id}_{step_number}.sim"
    step_commons[0]["listoutput"] = [{"outputDataName": outputFileName, "outputDataType": outputFileName.split(".")[1]}]
    Path(outputFileName).touch()

    assert gaudi.execute(
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

    # Check that the application was run
    run_app_mock.assert_called_once()

    # Check the outputs
    fileName = f"{prod_id}_{prod_job_id}_{step_number}"
    assert Path(f"{fileName}.sim").exists()
    assert not Path(f"gaudi_extra_options.py").exists()
    assert Path(f"prodConf_{gaudi.applicationName}_{fileName}.json").exists()
    assert not Path("DISABLE_WATCHDOG_CPU_WALLCLOCK_CHECK").exists()

    # Check if a production configuration file is created
    with open(f"prodConf_{gaudi.applicationName}_{fileName}.json") as f:
        prodConfContent = json.load(f)

    assert prodConfContent["application"]["name"] == gaudi.applicationName
    assert prodConfContent["application"]["version"] == gaudi.applicationVersion
    assert prodConfContent["application"]["number_of_processors"] == gaudi.numberOfProcessors
    assert prodConfContent["application"]["data_pkgs"] == []
    assert prodConfContent["application"]["event_timeout"] is None

    assert prodConfContent["options"]["files"] == []
    assert prodConfContent["options"]["processing_pass"] is None

    assert prodConfContent["db_tags"] == {}

    assert prodConfContent["input"]["files"] == []
    assert prodConfContent["input"]["first_event_number"] == gaudi.numberOfEvents * (int(prod_job_id) - 1) + 1
    assert prodConfContent["input"]["tck"] == gaudi.mcTCK
    assert prodConfContent["input"]["xml_file_catalog"] == gaudi.poolXMLCatName
    assert prodConfContent["input"]["xml_summary_file"] == ""
    assert prodConfContent["input"]["n_of_events"] == gaudi.numberOfEvents
    assert prodConfContent["input"]["run_number"] == int(prod_id) * 100 + int(prod_job_id)

    assert prodConfContent["output"]["prefix"] == ""
    assert prodConfContent["output"]["types"] == [step_commons[0]["listoutput"][0]["outputDataType"]]

    # Check if workflow_commons contain the outputs
    assert gaudi.workflow_commons["outputList"] == step_commons[0]["listoutput"]
    assert gaudi.workflow_commons["BookkeepingLFNs"] == [
        f"/lhcb/{wf_commons[0]['configName']}/{wf_commons[0]['configVersion']}/SIM/00000123/0000/{outputFileName}"
    ]
    assert gaudi.workflow_commons["LogFilePath"] == [
        f"/lhcb/{wf_commons[0]['configName']}/{wf_commons[0]['configVersion']}/LOG/00000123/0000"
    ]
    assert gaudi.workflow_commons["ProductionOutputData"] == [
        f"/lhcb/{wf_commons[0]['configName']}/{wf_commons[0]['configVersion']}/SIM/00000123/0000/{outputFileName}"
    ]

    # Validate jobReport calls
    expected_calls = [
        (f"{gaudi.applicationName} step {step_number}", True),
        (f"{gaudi.applicationName} {gaudi.applicationVersion} Successful", True),
    ]

    actual_calls = gaudi.jobReport.setApplicationStatus.call_args_list
    actual_calls_args = [(call_args[0][0], call_args[0][1]) for call_args in actual_calls]

    assert len(actual_calls_args) == len(expected_calls), "Unexpected number of calls to setApplicationStatus"
    for expected_call in expected_calls:
        assert expected_call in actual_calls_args, f"Expected call {expected_call} not found in actual calls"


def test_gaudi_user_mcsimulation_basic_success(mocker, gaudi):
    """Test basic user application success scenario with default values:

      * should contain a gaudi_extra_options.py file
      * first_event_number should be built upon numberOfEvents
      * no output should be added in workflow_commons

    This should actually be a very rare case as the user would need to create a workflow by himself/herself.
    """
    # Mock the GaudiApplication module (MCSimulation)
    run_app_mock = mocker.patch(
        "LHCbDIRAC.Core.Utilities.RunApplication.RunApplication.run",
        return_value=S_OK((0, "Completed successfully", "")),
    )
    gaudi.applicationName = "Gauss"
    gaudi.applicationVersion = "v49r10"

    # This is a user job: gaudi_extra_options.py should be created
    gaudi.jobType = "User"

    # Mock the inputs: there is no input data with Gauss jobs
    gaudi.stepInputData = []

    # Mock the outputs
    outputFileName = f"{prod_id}_{prod_job_id}_{step_number}.sim"
    step_commons[0]["listoutput"] = [{"outputDataName": outputFileName, "outputDataType": outputFileName.split(".")[1]}]
    Path(outputFileName).touch()

    assert gaudi.execute(
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

    # Check that the application was run
    run_app_mock.assert_called_once()

    # Check the outputs
    fileName = f"{prod_id}_{prod_job_id}_{step_number}"
    assert Path(f"{fileName}.sim").exists()
    assert Path(f"gaudi_extra_options.py").exists()
    assert Path(f"prodConf_{gaudi.applicationName}_{fileName}.json").exists()
    assert not Path("DISABLE_WATCHDOG_CPU_WALLCLOCK_CHECK").exists()

    # Check if a gaudi_extra_options file is created
    with open(f"gaudi_extra_options.py") as f:
        gaudi_extra_options = f.read()

    # The application used is gauss, so Gaudi should not be imported
    assert "from Gaudi.Configuration import *" not in gaudi_extra_options
    assert "from Gauss.Configuration import *" in gaudi_extra_options

    # There is no input data, so the following content should not be present
    assert "EventSelector().Input" not in gaudi_extra_options
    assert "FileCatalog().Catalogs= [" in gaudi_extra_options

    # The job is using Gauss but is a user job, so the following content should not be present
    assert 'GaussGen = GenInit("GaussGen")' not in gaudi_extra_options
    assert "GaussGen.RunNumber" not in gaudi_extra_options
    assert "GaussGen.FirstEventNumber" not in gaudi_extra_options

    # The number of events should be set as the number of events is defined
    assert "ApplicationMgr().EvtMax =" in gaudi_extra_options

    # Check if a production configuration file is created
    with open(f"prodConf_{gaudi.applicationName}_{fileName}.json") as f:
        prodConfContent = json.load(f)

    assert prodConfContent["application"]["name"] == gaudi.applicationName
    assert prodConfContent["application"]["version"] == gaudi.applicationVersion
    assert prodConfContent["application"]["number_of_processors"] == gaudi.numberOfProcessors
    assert prodConfContent["application"]["data_pkgs"] == []
    assert prodConfContent["application"]["event_timeout"] is None

    assert prodConfContent["options"]["files"] == ["gaudi_extra_options.py"]
    assert prodConfContent["options"]["processing_pass"] is None

    assert prodConfContent["db_tags"] == {}

    assert prodConfContent["input"]["files"] == []
    assert prodConfContent["input"]["first_event_number"] == gaudi.numberOfEvents * (int(prod_job_id) - 1) + 1
    assert prodConfContent["input"]["tck"] == gaudi.mcTCK
    assert prodConfContent["input"]["xml_file_catalog"] == gaudi.poolXMLCatName
    assert prodConfContent["input"]["xml_summary_file"] == ""
    assert prodConfContent["input"]["n_of_events"] == gaudi.numberOfEvents
    assert prodConfContent["input"]["run_number"] == int(prod_id) * 100 + int(prod_job_id)

    assert prodConfContent["output"]["prefix"] == ""
    assert prodConfContent["output"]["types"] == []

    # Check if workflow_commons contain the outputs
    assert "outputList" not in gaudi.workflow_commons
    assert "BookkeepingLFNs" not in gaudi.workflow_commons
    assert "LogFilePath" not in gaudi.workflow_commons
    assert "ProductionOutputData" not in gaudi.workflow_commons

    # Validate jobReport calls
    expected_calls = [
        (f"{gaudi.applicationName} step {step_number}", True),
        (f"{gaudi.applicationName} {gaudi.applicationVersion} Successful", True),
    ]

    actual_calls = gaudi.jobReport.setApplicationStatus.call_args_list
    actual_calls_args = [(call_args[0][0], call_args[0][1]) for call_args in actual_calls]

    assert len(actual_calls_args) == len(expected_calls), "Unexpected number of calls to setApplicationStatus"
    for expected_call in expected_calls:
        assert expected_call in actual_calls_args, f"Expected call {expected_call} not found in actual calls"


def test_gaudi_prod_mcsimulation_optionsLine_success(mocker, gaudi):
    """Test prod mcsimulation application with the optionsLine parameter set:

    * should contain a gaudi_extra_options.py file
    * gaudi_extra_options.py should contain information related to GaussGen
    """
    # Mock the GaudiApplication module (MCSimulation)
    run_app_mock = mocker.patch(
        "LHCbDIRAC.Core.Utilities.RunApplication.RunApplication.run",
        return_value=S_OK((0, "Completed successfully", "")),
    )
    gaudi.applicationName = "Gauss"
    gaudi.applicationVersion = "v49r10"

    # This is a MCSimulation job with optionsLine: gaudi_extra_options.py should be created
    gaudi.jobType = "MCSimulation"
    gaudi.optionsLine = "test"

    # Mock the inputs: there is no input data with Gauss jobs
    gaudi.stepInputData = []

    # Mock the outputs
    outputFileName = f"{prod_id}_{prod_job_id}_{step_number}.sim"
    step_commons[0]["listoutput"] = [{"outputDataName": outputFileName, "outputDataType": outputFileName.split(".")[1]}]
    Path(outputFileName).touch()

    assert gaudi.execute(
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

    # Check that the application was run
    run_app_mock.assert_called_once()

    # Check the outputs
    fileName = f"{prod_id}_{prod_job_id}_{step_number}"
    assert Path(f"{fileName}.sim").exists()
    assert Path(f"gaudi_extra_options.py").exists()
    assert Path(f"prodConf_{gaudi.applicationName}_{fileName}.json").exists()
    assert not Path("DISABLE_WATCHDOG_CPU_WALLCLOCK_CHECK").exists()

    # Check if a gaudi_extra_options file is created
    with open(f"gaudi_extra_options.py") as f:
        gaudi_extra_options = f.read()

    # The application used is gauss, so Gaudi should not be imported
    assert "from Gaudi.Configuration import *" not in gaudi_extra_options
    assert "from Gauss.Configuration import *" in gaudi_extra_options

    # There is no input data, so the following content should not be present
    assert "EventSelector().Input" not in gaudi_extra_options
    assert "FileCatalog().Catalogs= [" in gaudi_extra_options

    # The job is using Gauss but is a user job, so the following content should not be present
    assert 'GaussGen = GenInit("GaussGen")' in gaudi_extra_options
    assert "GaussGen.RunNumber" in gaudi_extra_options
    assert "GaussGen.FirstEventNumber" in gaudi_extra_options

    # The number of events should be set as the number of events is defined
    assert "ApplicationMgr().EvtMax =" in gaudi_extra_options

    # Check if a production configuration file is created
    with open(f"prodConf_{gaudi.applicationName}_{fileName}.json") as f:
        prodConfContent = json.load(f)

    assert prodConfContent["application"]["name"] == gaudi.applicationName
    assert prodConfContent["application"]["version"] == gaudi.applicationVersion
    assert prodConfContent["application"]["number_of_processors"] == gaudi.numberOfProcessors
    assert prodConfContent["application"]["data_pkgs"] == []
    assert prodConfContent["application"]["event_timeout"] is None

    assert prodConfContent["options"]["files"] == ["gaudi_extra_options.py"]
    assert prodConfContent["options"]["processing_pass"] is None

    assert prodConfContent["db_tags"] == {}

    assert prodConfContent["input"]["files"] == []
    assert prodConfContent["input"]["first_event_number"] == gaudi.numberOfEvents * (int(prod_job_id) - 1) + 1
    assert prodConfContent["input"]["tck"] == gaudi.mcTCK
    assert prodConfContent["input"]["xml_file_catalog"] == gaudi.poolXMLCatName
    assert prodConfContent["input"]["xml_summary_file"] == ""
    assert prodConfContent["input"]["n_of_events"] == gaudi.numberOfEvents
    assert prodConfContent["input"]["run_number"] == int(prod_id) * 100 + int(prod_job_id)

    assert prodConfContent["output"]["prefix"] == ""
    assert prodConfContent["output"]["types"] == []

    # Validate jobReport calls
    expected_calls = [
        (f"{gaudi.applicationName} step {step_number}", True),
        (f"{gaudi.applicationName} {gaudi.applicationVersion} Successful", True),
    ]

    actual_calls = gaudi.jobReport.setApplicationStatus.call_args_list
    actual_calls_args = [(call_args[0][0], call_args[0][1]) for call_args in actual_calls]

    assert len(actual_calls_args) == len(expected_calls), "Unexpected number of calls to setApplicationStatus"
    for expected_call in expected_calls:
        assert expected_call in actual_calls_args, f"Expected call {expected_call} not found in actual calls"


def test_gaudi_prod_mcsimulation_optionFilesList_success(mocker, gaudi):
    """Test MCSimulation success scenario with option files that take the form of a list.

    * options should then appear in the prodConf.json file under the '/options/files' section
    """
    # Mock the GaudiApplication module (MCSimulation)
    run_app_mock = mocker.patch(
        "LHCbDIRAC.Core.Utilities.RunApplication.RunApplication.run",
        return_value=S_OK((0, "Completed successfully", "")),
    )
    gaudi.applicationName = "Gauss"
    gaudi.applicationVersion = "v49r10"
    gaudi.jobType = "MCSimulation"

    # List of options files
    optionsFile = [
        "$APPCONFIGOPTS/Gauss/Beam6500GeV-mu100-2017-nu1.6.py",
        "$APPCONFIGOPTS/Gauss/EnableSpillover-25ns.py;",
        "$APPCONFIGOPTS/Gauss/DataType-2017.py",
        "$APPCONFIGOPTS/Gauss/RICHRandomHits.py"
        "$DECFILESROOT/options/@{eventType}.py"
        "$LBPYTHIA8ROOT/options/Pythia8.py"
        "$APPCONFIGOPTS/Gauss/G4PL_FTFP_BERT_EmNoCuts.py"
        "$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py",
    ]
    gaudi.optionsFile = ";".join(optionsFile)

    # Mock the inputs: there is no input data with MCSimulation jobs
    gaudi.stepInputData = []

    # Mock the outputs
    outputFileName = f"{prod_id}_{prod_job_id}_{step_number}.sim"
    step_commons[0]["listoutput"] = [{"outputDataName": outputFileName, "outputDataType": outputFileName.split(".")[1]}]
    Path(outputFileName).touch()

    assert gaudi.execute(
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

    # Check that the application was run
    run_app_mock.assert_called_once()

    # Check the outputs
    fileName = f"{prod_id}_{prod_job_id}_{step_number}"
    assert Path(f"{fileName}.sim").exists()
    assert not Path(f"gaudi_extra_options.py").exists()
    assert Path(f"prodConf_{gaudi.applicationName}_{fileName}.json").exists()
    assert not Path("DISABLE_WATCHDOG_CPU_WALLCLOCK_CHECK").exists()

    # Check if a production configuration file is created
    with open(f"prodConf_{gaudi.applicationName}_{fileName}.json") as f:
        prodConfContent = json.load(f)

    assert prodConfContent["application"]["name"] == gaudi.applicationName
    assert prodConfContent["application"]["version"] == gaudi.applicationVersion
    assert prodConfContent["application"]["number_of_processors"] == gaudi.numberOfProcessors
    assert prodConfContent["application"]["data_pkgs"] == []
    assert prodConfContent["application"]["event_timeout"] is None

    assert prodConfContent["options"]["files"] == gaudi.optionsFile.split(";")
    assert prodConfContent["options"]["processing_pass"] is None

    assert prodConfContent["db_tags"] == {}

    assert prodConfContent["input"]["files"] == []
    assert prodConfContent["input"]["first_event_number"] == gaudi.numberOfEvents * (int(prod_job_id) - 1) + 1
    assert prodConfContent["input"]["tck"] == gaudi.mcTCK
    assert prodConfContent["input"]["xml_file_catalog"] == gaudi.poolXMLCatName
    assert prodConfContent["input"]["xml_summary_file"] == ""
    assert prodConfContent["input"]["n_of_events"] == gaudi.numberOfEvents
    assert prodConfContent["input"]["run_number"] == int(prod_id) * 100 + int(prod_job_id)

    assert prodConfContent["output"]["prefix"] == ""
    assert prodConfContent["output"]["types"] == [step_commons[0]["listoutput"][0]["outputDataType"]]

    # Validate jobReport calls
    expected_calls = [
        (f"{gaudi.applicationName} step {step_number}", True),
        (f"{gaudi.applicationName} {gaudi.applicationVersion} Successful", True),
    ]

    actual_calls = gaudi.jobReport.setApplicationStatus.call_args_list
    actual_calls_args = [(call_args[0][0], call_args[0][1]) for call_args in actual_calls]

    assert len(actual_calls_args) == len(expected_calls), "Unexpected number of calls to setApplicationStatus"
    for expected_call in expected_calls:
        assert expected_call in actual_calls_args, f"Expected call {expected_call} not found in actual calls"


def test_gaudi_prod_mcsimulation_optionFilesJson_success(mocker, gaudi):
    """Test MCSimulation success scenario with option files that take the form of a json content.

    * Options should then appear in prodConf.json under the '/options' section.
    """
    # Mock the GaudiApplication module (MCSimulation)
    run_app_mock = mocker.patch(
        "LHCbDIRAC.Core.Utilities.RunApplication.RunApplication.run",
        return_value=S_OK((0, "Completed successfully", "")),
    )
    gaudi.applicationName = "Gauss"
    gaudi.applicationVersion = "v49r10"
    gaudi.jobType = "MCSimulation"

    # JSON Options file
    gaudi.optionsFile = '{"option1": "test1", "option2": "test2"}'

    # Mock the inputs: there is no input data with MCSimulation jobs
    gaudi.stepInputData = []

    # Mock the outputs
    outputFileName = f"{prod_id}_{prod_job_id}_{step_number}.sim"
    step_commons[0]["listoutput"] = [{"outputDataName": outputFileName, "outputDataType": outputFileName.split(".")[1]}]
    Path(outputFileName).touch()

    assert gaudi.execute(
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

    # Check that the application was run
    run_app_mock.assert_called_once()

    # Check the outputs
    fileName = f"{prod_id}_{prod_job_id}_{step_number}"
    assert Path(f"{fileName}.sim").exists()
    assert not Path(f"gaudi_extra_options.py").exists()
    assert Path(f"prodConf_{gaudi.applicationName}_{fileName}.json").exists()
    assert not Path("DISABLE_WATCHDOG_CPU_WALLCLOCK_CHECK").exists()

    # Check if a production configuration file is created
    with open(f"prodConf_{gaudi.applicationName}_{fileName}.json") as f:
        prodConfContent = json.load(f)

    assert prodConfContent["application"]["name"] == gaudi.applicationName
    assert prodConfContent["application"]["version"] == gaudi.applicationVersion
    assert prodConfContent["application"]["number_of_processors"] == gaudi.numberOfProcessors
    assert prodConfContent["application"]["data_pkgs"] == []
    assert prodConfContent["application"]["event_timeout"] is None

    assert "files" not in prodConfContent["options"]
    assert "processing_pass" not in prodConfContent["options"]

    assert prodConfContent["options"]["option1"] == "test1"
    assert prodConfContent["options"]["option2"] == "test2"

    assert prodConfContent["db_tags"] == {}

    assert prodConfContent["input"]["files"] == []
    assert prodConfContent["input"]["first_event_number"] == gaudi.numberOfEvents * (int(prod_job_id) - 1) + 1
    assert prodConfContent["input"]["tck"] == gaudi.mcTCK
    assert prodConfContent["input"]["xml_file_catalog"] == gaudi.poolXMLCatName
    assert prodConfContent["input"]["xml_summary_file"] == ""
    assert prodConfContent["input"]["n_of_events"] == gaudi.numberOfEvents
    assert prodConfContent["input"]["run_number"] == int(prod_id) * 100 + int(prod_job_id)

    assert prodConfContent["output"]["prefix"] == ""
    assert prodConfContent["output"]["types"] == [step_commons[0]["listoutput"][0]["outputDataType"]]

    # Validate jobReport calls
    expected_calls = [
        (f"{gaudi.applicationName} step {step_number}", True),
        (f"{gaudi.applicationName} {gaudi.applicationVersion} Successful", True),
    ]

    actual_calls = gaudi.jobReport.setApplicationStatus.call_args_list
    actual_calls_args = [(call_args[0][0], call_args[0][1]) for call_args in actual_calls]

    assert len(actual_calls_args) == len(expected_calls), "Unexpected number of calls to setApplicationStatus"
    for expected_call in expected_calls:
        assert expected_call in actual_calls_args, f"Expected call {expected_call} not found in actual calls"


def test_gaudi_prod_mcsimulation_firstEventNumber_success(mocker, gaudi):
    """Test MCSimulation success scenario when it is a test job:

    * first_event_number should be built upon maxNumberOfEvents if defined
    """
    # Mock the GaudiApplication module (MCSimulation)
    run_app_mock = mocker.patch(
        "LHCbDIRAC.Core.Utilities.RunApplication.RunApplication.run",
        return_value=S_OK((0, "Completed successfully", "")),
    )
    gaudi.applicationName = "Gauss"
    gaudi.applicationVersion = "v49r10"

    # The first_event_number should be built upon numberOfEvents
    gaudi.jobType = "MCSimulation"
    gaudi.maxNumberOfEvents = 1000
    gaudi.numberOfEvents = 100

    # Mock the inputs: there is no input data with MCSimulation jobs
    gaudi.stepInputData = []

    # Mock the outputs
    outputFileName = f"{prod_id}_{prod_job_id}_{step_number}.sim"
    step_commons[0]["listoutput"] = [{"outputDataName": outputFileName, "outputDataType": outputFileName.split(".")[1]}]
    Path(outputFileName).touch()

    assert gaudi.execute(
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
    # Check that the application was run
    run_app_mock.assert_called_once()

    # Check the outputs
    fileName = f"{prod_id}_{prod_job_id}_{step_number}"
    assert Path(f"{fileName}.sim").exists()
    assert not Path(f"gaudi_extra_options.py").exists()
    assert Path(f"prodConf_{gaudi.applicationName}_{fileName}.json").exists()
    assert not Path("DISABLE_WATCHDOG_CPU_WALLCLOCK_CHECK").exists()

    # Check if a production configuration file is created
    with open(f"prodConf_{gaudi.applicationName}_{fileName}.json") as f:
        prodConfContent = json.load(f)

    assert prodConfContent["application"]["name"] == gaudi.applicationName
    assert prodConfContent["application"]["version"] == gaudi.applicationVersion
    assert prodConfContent["application"]["number_of_processors"] == gaudi.numberOfProcessors
    assert prodConfContent["application"]["data_pkgs"] == []
    assert prodConfContent["application"]["event_timeout"] is None

    assert prodConfContent["options"]["files"] == []
    assert prodConfContent["options"]["processing_pass"] is None

    assert prodConfContent["options"]["files"] == []
    assert prodConfContent["options"]["processing_pass"] is None

    assert prodConfContent["db_tags"] == {}

    assert prodConfContent["input"]["files"] == []
    assert prodConfContent["input"]["first_event_number"] == gaudi.maxNumberOfEvents * (int(prod_job_id) - 1) + 1
    assert prodConfContent["input"]["tck"] == gaudi.mcTCK
    assert prodConfContent["input"]["xml_file_catalog"] == gaudi.poolXMLCatName
    assert prodConfContent["input"]["xml_summary_file"] == ""
    assert prodConfContent["input"]["n_of_events"] == gaudi.numberOfEvents
    assert prodConfContent["input"]["run_number"] == int(prod_id) * 100 + int(prod_job_id)

    assert prodConfContent["output"]["prefix"] == ""
    assert prodConfContent["output"]["types"] == [step_commons[0]["listoutput"][0]["outputDataType"]]

    # Validate jobReport calls
    expected_calls = [
        (f"{gaudi.applicationName} step {step_number}", True),
        (f"{gaudi.applicationName} {gaudi.applicationVersion} Successful", True),
    ]

    actual_calls = gaudi.jobReport.setApplicationStatus.call_args_list
    actual_calls_args = [(call_args[0][0], call_args[0][1]) for call_args in actual_calls]

    assert len(actual_calls_args) == len(expected_calls), "Unexpected number of calls to setApplicationStatus"
    for expected_call in expected_calls:
        assert expected_call in actual_calls_args, f"Expected call {expected_call} not found in actual calls"


def test_gaudi_prod_mcsimulation_slowComputingResource_success(mocker, gaudi):
    """Test Gaudi success scenario when we are executing an application on a slow running machine:

    * Config.getValue("/LocalSite/CPUNormalizationFactor") should be set to a value < 10
    * In prodConf.json, "event_timeout" should be set
    """
    # Mock the GaudiApplication module (MCSimulation)
    run_app_mock = mocker.patch(
        "LHCbDIRAC.Core.Utilities.RunApplication.RunApplication.run",
        return_value=S_OK((0, "Completed successfully", "")),
    )
    gaudi.applicationName = "Gauss"
    gaudi.applicationVersion = "v49r10"

    # The first_event_number should be built upon numberOfEvents
    gaudi.jobType = "MCSimulation"

    # Mock gConfig
    cpuNormalizationFactor = 9
    mocker.patch("DIRAC.gConfig.getValue", return_value=cpuNormalizationFactor)

    # Mock the inputs: there is no input data with MCSimulation jobs
    gaudi.stepInputData = []

    # Mock the outputs
    outputFileName = f"{prod_id}_{prod_job_id}_{step_number}.sim"
    step_commons[0]["listoutput"] = [{"outputDataName": outputFileName, "outputDataType": outputFileName.split(".")[1]}]
    Path(outputFileName).touch()

    assert gaudi.execute(
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
    # Check that the application was run
    run_app_mock.assert_called_once()

    # Check the outputs
    fileName = f"{prod_id}_{prod_job_id}_{step_number}"
    assert Path(f"{fileName}.sim").exists()
    assert not Path(f"gaudi_extra_options.py").exists()
    assert Path(f"prodConf_{gaudi.applicationName}_{fileName}.json").exists()
    assert not Path("DISABLE_WATCHDOG_CPU_WALLCLOCK_CHECK").exists()

    # Check if a production configuration file is created
    with open(f"prodConf_{gaudi.applicationName}_{fileName}.json") as f:
        prodConfContent = json.load(f)

    assert prodConfContent["application"]["name"] == gaudi.applicationName
    assert prodConfContent["application"]["version"] == gaudi.applicationVersion
    assert prodConfContent["application"]["number_of_processors"] == gaudi.numberOfProcessors
    assert prodConfContent["application"]["data_pkgs"] == []
    assert prodConfContent["application"]["event_timeout"] == int(3600 * 10 / cpuNormalizationFactor)

    assert prodConfContent["options"]["files"] == []
    assert prodConfContent["options"]["processing_pass"] is None

    assert prodConfContent["options"]["files"] == []
    assert prodConfContent["options"]["processing_pass"] is None

    assert prodConfContent["db_tags"] == {}

    assert prodConfContent["input"]["files"] == []
    assert prodConfContent["input"]["first_event_number"] == gaudi.numberOfEvents * (int(prod_job_id) - 1) + 1
    assert prodConfContent["input"]["tck"] == gaudi.mcTCK
    assert prodConfContent["input"]["xml_file_catalog"] == gaudi.poolXMLCatName
    assert prodConfContent["input"]["xml_summary_file"] == ""
    assert prodConfContent["input"]["n_of_events"] == gaudi.numberOfEvents
    assert prodConfContent["input"]["run_number"] == int(prod_id) * 100 + int(prod_job_id)

    assert prodConfContent["output"]["prefix"] == ""
    assert prodConfContent["output"]["types"] == [step_commons[0]["listoutput"][0]["outputDataType"]]

    # Validate jobReport calls
    expected_calls = [
        (f"{gaudi.applicationName} step {step_number}", True),
        (f"{gaudi.applicationName} {gaudi.applicationVersion} Successful", True),
    ]

    actual_calls = gaudi.jobReport.setApplicationStatus.call_args_list
    actual_calls_args = [(call_args[0][0], call_args[0][1]) for call_args in actual_calls]

    assert len(actual_calls_args) == len(expected_calls), "Unexpected number of calls to setApplicationStatus"
    for expected_call in expected_calls:
        assert expected_call in actual_calls_args, f"Expected call {expected_call} not found in actual calls"


def test_gaudi_prod_mcsimulation_dbtags_success(mocker, gaudi):
    """Test Gaudi success scenario when we are executing an application with ddbtags/condb/dq tags:

    * DDDBTag, condDBTag, dqTag should appear in prodConf.json under the `db_tags` section
    """
    # Mock the GaudiApplication module (MCSimulation)
    run_app_mock = mocker.patch(
        "LHCbDIRAC.Core.Utilities.RunApplication.RunApplication.run",
        return_value=S_OK((0, "Completed successfully", "")),
    )
    gaudi.applicationName = "Gauss"
    gaudi.applicationVersion = "v49r10"

    # The first_event_number should be built upon numberOfEvents
    gaudi.jobType = "MCSimulation"

    # Add some tags
    gaudi.DDDBTag = "dddb-20170721"
    gaudi.condDBTag = "sim-20170721-vc-md100"
    gaudi.dqTag = "v1r0"

    # Mock the inputs: there is no input data with MCSimulation jobs
    gaudi.stepInputData = []

    # Mock the outputs
    outputFileName = f"{prod_id}_{prod_job_id}_{step_number}.sim"
    step_commons[0]["listoutput"] = [{"outputDataName": outputFileName, "outputDataType": outputFileName.split(".")[1]}]
    Path(outputFileName).touch()

    assert gaudi.execute(
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
    # Check that the application was run
    run_app_mock.assert_called_once()

    # Check the outputs
    fileName = f"{prod_id}_{prod_job_id}_{step_number}"
    assert Path(f"{fileName}.sim").exists()
    assert not Path(f"gaudi_extra_options.py").exists()
    assert Path(f"prodConf_{gaudi.applicationName}_{fileName}.json").exists()
    assert not Path("DISABLE_WATCHDOG_CPU_WALLCLOCK_CHECK").exists()

    # Check if a production configuration file is created
    with open(f"prodConf_{gaudi.applicationName}_{fileName}.json") as f:
        prodConfContent = json.load(f)

    assert prodConfContent["application"]["name"] == gaudi.applicationName
    assert prodConfContent["application"]["version"] == gaudi.applicationVersion
    assert prodConfContent["application"]["number_of_processors"] == gaudi.numberOfProcessors
    assert prodConfContent["application"]["data_pkgs"] == []

    assert prodConfContent["options"]["files"] == []
    assert prodConfContent["options"]["processing_pass"] is None

    assert prodConfContent["options"]["files"] == []
    assert prodConfContent["options"]["processing_pass"] is None

    # Tags should be present in the prodConf.json file
    assert prodConfContent["db_tags"]["dddb_tag"] == gaudi.DDDBTag
    assert prodConfContent["db_tags"]["conddb_tag"] == gaudi.condDBTag
    assert prodConfContent["db_tags"]["dq_tag"] == gaudi.dqTag

    assert prodConfContent["input"]["files"] == []
    assert prodConfContent["input"]["first_event_number"] == gaudi.numberOfEvents * (int(prod_job_id) - 1) + 1
    assert prodConfContent["input"]["tck"] == gaudi.mcTCK
    assert prodConfContent["input"]["xml_file_catalog"] == gaudi.poolXMLCatName
    assert prodConfContent["input"]["xml_summary_file"] == ""
    assert prodConfContent["input"]["n_of_events"] == gaudi.numberOfEvents
    assert prodConfContent["input"]["run_number"] == int(prod_id) * 100 + int(prod_job_id)

    assert prodConfContent["output"]["prefix"] == ""
    assert prodConfContent["output"]["types"] == [step_commons[0]["listoutput"][0]["outputDataType"]]

    # Validate jobReport calls
    expected_calls = [
        (f"{gaudi.applicationName} step {step_number}", True),
        (f"{gaudi.applicationName} {gaudi.applicationVersion} Successful", True),
    ]

    actual_calls = gaudi.jobReport.setApplicationStatus.call_args_list
    actual_calls_args = [(call_args[0][0], call_args[0][1]) for call_args in actual_calls]

    assert len(actual_calls_args) == len(expected_calls), "Unexpected number of calls to setApplicationStatus"
    for expected_call in expected_calls:
        assert expected_call in actual_calls_args, f"Expected call {expected_call} not found in actual calls"


def test_gaudi_prod_merge_basic_success(mocker, gaudi):
    """Test Merge success scenario:

    * Should disable the watchdog CPU wallclock check.
    """
    # Mock the GaudiApplication module (Merge)
    run_app_mock = mocker.patch(
        "LHCbDIRAC.Core.Utilities.RunApplication.RunApplication.run",
        return_value=S_OK((0, "Completed successfully", "")),
    )
    mocker.patch(
        "LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient.BookkeepingClient.getFileMetadata",
        return_value=S_OK(
            {
                "Successful": {
                    "00104340_00142122_1": {
                        "ADLER32": None,
                        "FileType": "DST",
                        "FullStat": None,
                        "GotReplica": "Yes",
                        "DataqualityFlag": "OK",
                        "EventStat": 101,
                        "EventType": 12365501,
                        "FileSize": 1000,
                        "GUID": "7EA19086-1E36-E611-9457-001E67398520",
                        "RunNumber": 93718,
                    },
                }
            }
        ),
    )
    gaudi.applicationName = "LHCb"
    gaudi.applicationVersion = "v49r10"
    gaudi.jobType = "Merge"

    # Mock the inputs: this is needed for the Merge job
    gaudi.stepInputData = ["/lhcb/LHCb/IFT.DST/00104340/0010/00104340_00142122_1.ift.dst"]

    # Mock the outputs
    outputFileName = f"{prod_id}_{prod_job_id}_{step_number}.dst"
    step_commons[0]["listoutput"] = [
        {"outputDataName": outputFileName, "outputDataType": outputFileName.split(".")[-1]}
    ]
    Path(outputFileName).touch()

    assert gaudi.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        # wms_job_id is set, so DISABLE_WATCHDOG_CPU_WALLCLOCK_CHECK should exist
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=step_commons[0],
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"]

    # Check that the application was run
    run_app_mock.assert_called_once()

    # Check the outputs
    fileName = f"{prod_id}_{prod_job_id}_{step_number}"
    assert Path(f"{fileName}.dst").exists()
    assert not Path(f"gaudi_extra_options.py").exists()
    assert Path(f"prodConf_{gaudi.applicationName}_{fileName}.json").exists()
    assert Path("DISABLE_WATCHDOG_CPU_WALLCLOCK_CHECK").exists()

    # Check if a production configuration file is created
    with open(f"prodConf_{gaudi.applicationName}_{fileName}.json") as f:
        prodConfContent = json.load(f)

    assert prodConfContent["application"]["name"] == gaudi.applicationName
    assert prodConfContent["application"]["version"] == gaudi.applicationVersion
    assert prodConfContent["application"]["number_of_processors"] == gaudi.numberOfProcessors
    assert prodConfContent["application"]["data_pkgs"] == []
    assert prodConfContent["application"]["event_timeout"] is None

    assert prodConfContent["options"]["files"] == []
    assert prodConfContent["options"]["processing_pass"] is None

    assert prodConfContent["db_tags"] == {}

    assert prodConfContent["input"]["files"] == [f"LFN:{inputData}" for inputData in gaudi.stepInputData]
    assert prodConfContent["input"]["first_event_number"] == 0
    assert prodConfContent["input"]["tck"] == gaudi.mcTCK
    assert prodConfContent["input"]["xml_file_catalog"] == gaudi.poolXMLCatName
    assert prodConfContent["input"]["xml_summary_file"] == ""
    assert prodConfContent["input"]["n_of_events"] == gaudi.numberOfEvents
    assert "run_number" not in prodConfContent["input"]

    assert prodConfContent["output"]["prefix"] == ""
    assert prodConfContent["output"]["types"] == [step_commons[0]["listoutput"][0]["outputDataType"]]

    # Check if workflow_commons contain the outputs
    assert gaudi.workflow_commons["outputList"] == step_commons[0]["listoutput"]
    assert gaudi.workflow_commons["BookkeepingLFNs"] == [
        f"/lhcb/{wf_commons[0]['configName']}/{wf_commons[0]['configVersion']}/DST/00000123/0000/{outputFileName}"
    ]
    assert gaudi.workflow_commons["LogFilePath"] == [
        f"/lhcb/{wf_commons[0]['configName']}/{wf_commons[0]['configVersion']}/LOG/00000123/0000"
    ]
    assert gaudi.workflow_commons["ProductionOutputData"] == [
        f"/lhcb/{wf_commons[0]['configName']}/{wf_commons[0]['configVersion']}/DST/00000123/0000/{outputFileName}"
    ]

    # Validate jobReport calls
    expected_calls = [
        (f"{gaudi.applicationName} step {step_number}", True),
        (f"{gaudi.applicationName} {gaudi.applicationVersion} Successful", True),
    ]

    actual_calls = gaudi.jobReport.setApplicationStatus.call_args_list
    actual_calls_args = [(call_args[0][0], call_args[0][1]) for call_args in actual_calls]

    assert len(actual_calls_args) == len(expected_calls), "Unexpected number of calls to setApplicationStatus"
    for expected_call in expected_calls:
        assert expected_call in actual_calls_args, f"Expected call {expected_call} not found in actual calls"


def test_gaudi_prod_merge_histogram_success(mocker, gaudi):
    """Test Merge success scenario but there is only an histogram file as input

    * The histogram should appear in the outputs
    """
    # Mock the GaudiApplication module (Merge)
    run_app_mock = mocker.patch(
        "LHCbDIRAC.Core.Utilities.RunApplication.RunApplication.run",
        return_value=S_OK((0, "Completed successfully", "")),
    )
    gaudi.applicationName = "LHCb"
    gaudi.applicationVersion = "v49r10"
    gaudi.jobType = "Merge"

    # Mock the inputs: this is needed for the Merge job
    gaudi.stepInputData = ["/lhcb/LHCb/HIST/00104340/0010/00104340_00142122_1.hist"]

    # Mock the outputs
    outputFileName = f"{prod_id}_{prod_job_id}_{step_number}.hist"
    step_commons[0]["listoutput"] = [
        {"outputDataName": outputFileName, "outputDataType": outputFileName.split(".")[-1]}
    ]
    Path(outputFileName).touch()

    assert gaudi.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        # wms_job_id is set, so DISABLE_WATCHDOG_CPU_WALLCLOCK_CHECK should exist
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=step_commons[0],
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"]

    # Check that the application was run
    run_app_mock.assert_called_once()

    # Check the outputs
    fileName = f"{prod_id}_{prod_job_id}_{step_number}"
    assert Path(f"{fileName}.hist").exists()
    assert not Path(f"gaudi_extra_options.py").exists()
    assert Path(f"prodConf_{gaudi.applicationName}_{fileName}.json").exists()
    assert Path("DISABLE_WATCHDOG_CPU_WALLCLOCK_CHECK").exists()

    # Check if a production configuration file is created
    with open(f"prodConf_{gaudi.applicationName}_{fileName}.json") as f:
        prodConfContent = json.load(f)

    assert prodConfContent["application"]["name"] == gaudi.applicationName
    assert prodConfContent["application"]["version"] == gaudi.applicationVersion
    assert prodConfContent["application"]["number_of_processors"] == gaudi.numberOfProcessors
    assert prodConfContent["application"]["data_pkgs"] == []
    assert prodConfContent["application"]["event_timeout"] is None

    assert prodConfContent["options"]["files"] == []
    assert prodConfContent["options"]["processing_pass"] is None

    assert prodConfContent["db_tags"] == {}

    assert prodConfContent["input"]["files"] == [f"LFN:{inputData}" for inputData in gaudi.stepInputData]
    assert prodConfContent["input"]["first_event_number"] == 0
    assert prodConfContent["input"]["tck"] == gaudi.mcTCK
    assert prodConfContent["input"]["xml_file_catalog"] == gaudi.poolXMLCatName
    assert prodConfContent["input"]["xml_summary_file"] == ""
    assert prodConfContent["input"]["n_of_events"] == gaudi.numberOfEvents
    assert "run_number" not in prodConfContent["input"]

    assert prodConfContent["output"]["prefix"] == ""
    assert prodConfContent["output"]["types"] == [step_commons[0]["listoutput"][0]["outputDataType"]]

    # Check if workflow_commons contain the outputs
    assert gaudi.workflow_commons["outputList"] == step_commons[0]["listoutput"]
    assert gaudi.workflow_commons["BookkeepingLFNs"] == [
        f"/lhcb/{wf_commons[0]['configName']}/{wf_commons[0]['configVersion']}/HIST/00000123/0000/{outputFileName}"
    ]
    assert gaudi.workflow_commons["LogFilePath"] == [
        f"/lhcb/{wf_commons[0]['configName']}/{wf_commons[0]['configVersion']}/LOG/00000123/0000"
    ]
    assert gaudi.workflow_commons["ProductionOutputData"] == [
        f"/lhcb/{wf_commons[0]['configName']}/{wf_commons[0]['configVersion']}/HIST/00000123/0000/{outputFileName}"
    ]

    # Validate jobReport calls
    expected_calls = [
        (f"{gaudi.applicationName} step {step_number}", True),
        (f"{gaudi.applicationName} {gaudi.applicationVersion} Successful", True),
    ]

    actual_calls = gaudi.jobReport.setApplicationStatus.call_args_list
    actual_calls_args = [(call_args[0][0], call_args[0][1]) for call_args in actual_calls]

    assert len(actual_calls_args) == len(expected_calls), "Unexpected number of calls to setApplicationStatus"
    for expected_call in expected_calls:
        assert expected_call in actual_calls_args, f"Expected call {expected_call} not found in actual calls"


def test_gaudi_prod_merge_histogramDST_success(mocker, gaudi):
    """Test Merge success scenario but there is an histogram file and a dst file as input

    * The histogram should be removed from the outputs
    """
    # Mock the GaudiApplication module (Merge)
    run_app_mock = mocker.patch(
        "LHCbDIRAC.Core.Utilities.RunApplication.RunApplication.run",
        return_value=S_OK((0, "Completed successfully", "")),
    )
    mocker.patch(
        "LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient.BookkeepingClient.getFileMetadata",
        return_value=S_OK(
            {
                "Successful": {
                    "00104340_00142122_1": {
                        "ADLER32": None,
                        "FileType": "DST",
                        "FullStat": None,
                        "GotReplica": "Yes",
                        "DataqualityFlag": "OK",
                        "EventStat": 101,
                        "EventType": 12365501,
                        "FileSize": 1000,
                        "GUID": "7EA19086-1E36-E611-9457-001E67398520",
                        "RunNumber": 93718,
                    },
                }
            }
        ),
    )
    gaudi.applicationName = "LHCb"
    gaudi.applicationVersion = "v49r10"
    gaudi.jobType = "Merge"

    # Mock the inputs: this is needed for the Merge job
    gaudi.stepInputData = ["/lhcb/LHCb/HIST/00104340/0010/00104340_00142122_1.dst"]

    # Mock the outputs: 2 files, one histogram and one dst
    # The idea: the histogram does not exist and should not raise an error when searching for the outputs
    outputFileName = f"{prod_id}_{prod_job_id}_{step_number}"
    step_commons[0]["listoutput"] = [
        {"outputDataName": f"{outputFileName}.hist", "outputDataType": "hist"},
        {"outputDataName": f"{outputFileName}.dst", "outputDataType": "dst"},
    ]
    Path(f"{outputFileName}.dst").touch()

    assert gaudi.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        # wms_job_id is set, so DISABLE_WATCHDOG_CPU_WALLCLOCK_CHECK should exist
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=step_commons[0],
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"]

    # Check that the application was run
    run_app_mock.assert_called_once()

    # Check the outputs
    fileName = f"{prod_id}_{prod_job_id}_{step_number}"
    assert Path(f"{fileName}.dst").exists()
    assert not Path(f"gaudi_extra_options.py").exists()
    assert Path(f"prodConf_{gaudi.applicationName}_{fileName}.json").exists()
    assert Path("DISABLE_WATCHDOG_CPU_WALLCLOCK_CHECK").exists()

    # Check if a production configuration file is created
    with open(f"prodConf_{gaudi.applicationName}_{fileName}.json") as f:
        prodConfContent = json.load(f)

    assert prodConfContent["application"]["name"] == gaudi.applicationName
    assert prodConfContent["application"]["version"] == gaudi.applicationVersion
    assert prodConfContent["application"]["number_of_processors"] == gaudi.numberOfProcessors
    assert prodConfContent["application"]["data_pkgs"] == []
    assert prodConfContent["application"]["event_timeout"] is None

    assert prodConfContent["options"]["files"] == []
    assert prodConfContent["options"]["processing_pass"] is None

    assert prodConfContent["db_tags"] == {}

    assert prodConfContent["input"]["files"] == [f"LFN:{inputData}" for inputData in gaudi.stepInputData]
    assert prodConfContent["input"]["first_event_number"] == 0
    assert prodConfContent["input"]["tck"] == gaudi.mcTCK
    assert prodConfContent["input"]["xml_file_catalog"] == gaudi.poolXMLCatName
    assert prodConfContent["input"]["xml_summary_file"] == ""
    assert prodConfContent["input"]["n_of_events"] == gaudi.numberOfEvents
    assert "run_number" not in prodConfContent["input"]

    assert prodConfContent["output"]["prefix"] == ""
    assert prodConfContent["output"]["types"] == [step_commons[0]["listoutput"][0]["outputDataType"]]

    # Check if workflow_commons contain the outputs: the histogram should not be there
    assert gaudi.workflow_commons["outputList"] == step_commons[0]["listoutput"]
    assert gaudi.workflow_commons["BookkeepingLFNs"] == [
        f"/lhcb/{wf_commons[0]['configName']}/{wf_commons[0]['configVersion']}/DST/00000123/0000/{outputFileName}.dst"
    ]
    assert gaudi.workflow_commons["LogFilePath"] == [
        f"/lhcb/{wf_commons[0]['configName']}/{wf_commons[0]['configVersion']}/LOG/00000123/0000"
    ]
    assert gaudi.workflow_commons["ProductionOutputData"] == [
        f"/lhcb/{wf_commons[0]['configName']}/{wf_commons[0]['configVersion']}/DST/00000123/0000/{outputFileName}.dst"
    ]

    # Validate jobReport calls
    expected_calls = [
        (f"{gaudi.applicationName} step {step_number}", True),
        (f"{gaudi.applicationName} {gaudi.applicationVersion} Successful", True),
    ]

    actual_calls = gaudi.jobReport.setApplicationStatus.call_args_list
    actual_calls_args = [(call_args[0][0], call_args[0][1]) for call_args in actual_calls]

    assert len(actual_calls_args) == len(expected_calls), "Unexpected number of calls to setApplicationStatus"
    for expected_call in expected_calls:
        assert expected_call in actual_calls_args, f"Expected call {expected_call} not found in actual calls"


def test_gaudi_prod_merge_noJobID_success(mocker, gaudi):
    """Test Merge success scenario without JobID:

    * DISABLE_WATCHDOG_CPU_WALLCLOCK_CHECK file should not exist
    """
    # Mock the GaudiApplication module (Merge)
    run_app_mock = mocker.patch(
        "LHCbDIRAC.Core.Utilities.RunApplication.RunApplication.run",
        return_value=S_OK((0, "Completed successfully", "")),
    )
    mocker.patch(
        "LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient.BookkeepingClient.getFileMetadata",
        return_value=S_OK(
            {
                "Successful": {
                    "00104340_00142122_1": {
                        "ADLER32": None,
                        "FileType": "IFT.DST",
                        "FullStat": None,
                        "GotReplica": "Yes",
                        "DataqualityFlag": "OK",
                        "EventStat": 101,
                        "EventType": 12365501,
                        "FileSize": 1000,
                        "GUID": "7EA19086-1E36-E611-9457-001E67398520",
                        "RunNumber": 93718,
                    },
                }
            }
        ),
    )
    gaudi.applicationName = "LHCb"
    gaudi.applicationVersion = "v49r10"
    gaudi.jobType = "Merge"

    # Mock the inputs: this is needed for the Merge job
    gaudi.stepInputData = ["/lhcb/LHCb/IFT.DST/00104340/0010/00104340_00142122_1.ift.dst"]

    # Mock the outputs
    outputFileName = f"{prod_id}_{prod_job_id}_{step_number}.ift.dst"
    step_commons[0]["listoutput"] = [
        {"outputDataName": outputFileName, "outputDataType": outputFileName.split("_")[-1]}
    ]
    Path(outputFileName).touch()

    # wms_job_id is not set, so DISABLE_WATCHDOG_CPU_WALLCLOCK_CHECK should not exist
    assert gaudi.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=step_commons[0],
        step_number=step_number,
        step_id=step_id,
        stepStatus=S_OK(),
    )["OK"]

    # Check that the application was run
    run_app_mock.assert_called_once()

    # Check the outputs
    fileName = f"{prod_id}_{prod_job_id}_{step_number}"
    assert Path(f"{fileName}.ift.dst").exists()
    assert not Path(f"gaudi_extra_options.py").exists()
    assert Path(f"prodConf_{gaudi.applicationName}_{fileName}.json").exists()
    assert not Path("DISABLE_WATCHDOG_CPU_WALLCLOCK_CHECK").exists()

    # Check if a production configuration file is created
    with open(f"prodConf_{gaudi.applicationName}_{fileName}.json") as f:
        prodConfContent = json.load(f)

    assert prodConfContent["application"]["name"] == gaudi.applicationName
    assert prodConfContent["application"]["version"] == gaudi.applicationVersion
    assert prodConfContent["application"]["number_of_processors"] == gaudi.numberOfProcessors
    assert prodConfContent["application"]["data_pkgs"] == []
    assert prodConfContent["application"]["event_timeout"] is None

    assert prodConfContent["options"]["files"] == []
    assert prodConfContent["options"]["processing_pass"] is None

    assert prodConfContent["db_tags"] == {}

    assert prodConfContent["input"]["files"] == [f"LFN:{inputData}" for inputData in gaudi.stepInputData]
    assert prodConfContent["input"]["first_event_number"] == 0
    assert prodConfContent["input"]["tck"] == gaudi.mcTCK
    assert prodConfContent["input"]["xml_file_catalog"] == gaudi.poolXMLCatName
    assert prodConfContent["input"]["xml_summary_file"] == ""
    assert prodConfContent["input"]["n_of_events"] == gaudi.numberOfEvents
    assert "run_number" not in prodConfContent["input"]

    assert prodConfContent["output"]["prefix"] == ""
    assert prodConfContent["output"]["types"] == [step_commons[0]["listoutput"][0]["outputDataType"]]

    # Validate jobReport calls: 0 because no jobID present
    gaudi.jobReport.setApplicationStatus.assert_not_called()


def test_gaudi_previous_error_success(mocker, gaudi):
    """Test GaudApplication when there was a previous error in the workflow/step: stepStatus = S_ERROR."""
    # Mock the GaudiApplication module
    run_app_mock = mocker.patch(
        "LHCbDIRAC.Core.Utilities.RunApplication.RunApplication.run",
        return_value=S_OK((0, "Completed successfully", "")),
    )
    gaudi.applicationName = "Gauss"
    gaudi.applicationVersion = "v49r10"
    gaudi.jobType = "MCSimulation"

    assert gaudi.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=step_commons[0],
        step_number=step_number,
        step_id=step_id,
        # Here we have an error in the workflow/step
        stepStatus=S_ERROR(),
    )["OK"]

    # Check that the application was not run
    run_app_mock.assert_not_called()

    # Check the outputs
    fileName = f"{prod_id}_{prod_job_id}_{step_number}"
    assert not Path(f"{fileName}.sim").exists()
    assert not Path(f"gaudi_extra_options.py").exists()
    assert not Path(f"prodConf_{gaudi.applicationName}_{fileName}.json").exists()

    gaudi.jobReport.setApplicationStatus.assert_not_called()


def test_gaudi_prod_merge_bkerror_fail(mocker, gaudi):
    """Test Merge scenario where there is a Bookkeeping error:

    * Should disable the watchdog CPU wallclock check.
    """
    # Mock the GaudiApplication module (Merge)
    run_app_mock = mocker.patch(
        "LHCbDIRAC.Core.Utilities.RunApplication.RunApplication.run",
        return_value=S_OK((0, "Completed successfully", "")),
    )
    mocker.patch(
        "LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient.BookkeepingClient.getFileMetadata",
        side_effect=S_ERROR("Bookkeeping error"),
    )
    gaudi.applicationName = "LHCb"
    gaudi.applicationVersion = "v49r10"
    gaudi.jobType = "Merge"

    # Mock the inputs: this is needed for the Merge job
    gaudi.stepInputData = ["/lhcb/LHCb/IFT.DST/00104340/0010/00104340_00142122_1.ift.dst"]

    # Mock the outputs
    outputFileName = f"{prod_id}_{prod_job_id}_{step_number}.ift.dst"
    step_commons[0]["listoutput"] = [
        {"outputDataName": outputFileName, "outputDataType": outputFileName.split("_")[-1]}
    ]
    Path(outputFileName).touch()

    assert not gaudi.execute(
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

    # Check that the application was run
    run_app_mock.assert_not_called()

    # Check the outputs
    fileName = f"{prod_id}_{prod_job_id}_{step_number}"
    assert Path(f"{fileName}.ift.dst").exists()
    assert not Path(f"gaudi_extra_options.py").exists()
    assert not Path(f"prodConf_{gaudi.applicationName}_{fileName}.json").exists()
    assert Path("DISABLE_WATCHDOG_CPU_WALLCLOCK_CHECK").exists()

    # Validate jobReport calls
    expected_calls = [
        ("Error in GaudiApplication module", True),
    ]

    actual_calls = gaudi.jobReport.setApplicationStatus.call_args_list
    actual_calls_args = [(call_args[0][0], call_args[0][1]) for call_args in actual_calls]

    assert len(actual_calls_args) == len(expected_calls), "Unexpected number of calls to setApplicationStatus"
    for expected_call in expected_calls:
        assert expected_call in actual_calls_args, f"Expected call {expected_call} not found in actual calls"


def test_gaudi_prod_merge_differentInputs_fail(mocker, gaudi):
    """Test Merge scenario where multiple inputs of different types are present:

    * should raise an exception ValueError
    """
    # Mock the GaudiApplication module (Merge)
    run_app_mock = mocker.patch(
        "LHCbDIRAC.Core.Utilities.RunApplication.RunApplication.run",
        return_value=S_OK((0, "Completed successfully", "")),
    )
    mocker.patch(
        "LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient.BookkeepingClient.getFileMetadata",
        return_value=S_OK(
            {
                "Successful": {
                    "00104340_00142122_1": {
                        "ADLER32": None,
                        "FileType": "DST",
                        "FullStat": None,
                        "GotReplica": "Yes",
                        "DataqualityFlag": "OK",
                        "EventStat": 101,
                        "EventType": 12365501,
                        "FileSize": 1000,
                        "GUID": "7EA19086-1E36-E611-9457-001E67398520",
                        "RunNumber": 93718,
                    },
                    "00104340_00142122_2": {
                        "ADLER32": None,
                        "FileType": "HIST",
                        "FullStat": None,
                        "GotReplica": "Yes",
                        "DataqualityFlag": "OK",
                        "EventStat": 101,
                        "EventType": 12365501,
                        "FileSize": 1000,
                        "GUID": "7EA19086-1E36-E611-9457-001E67398520",
                        "RunNumber": 93718,
                    },
                }
            }
        ),
    )
    gaudi.applicationName = "LHCb"
    gaudi.applicationVersion = "v49r10"
    gaudi.jobType = "Merge"

    # Mock the inputs: this is needed for the Merge job
    gaudi.stepInputData = [
        "/lhcb/LHCb/IFT.DST/00104340/0010/00104340_00142122_1.dst",
        "/lhcb/LHCb/IFT.DST/00104340/0010/00104340_00142122_2.hist",
    ]

    # Mock the outputs
    outputFileName = f"{prod_id}_{prod_job_id}_{step_number}.dst"
    step_commons[0]["listoutput"] = [
        {"outputDataName": outputFileName, "outputDataType": outputFileName.split("_")[-1]}
    ]

    assert not gaudi.execute(
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

    # Check that the application was run
    run_app_mock.assert_not_called()

    # Check the outputs
    fileName = f"{prod_id}_{prod_job_id}_{step_number}"
    assert not Path(f"gaudi_extra_options.py").exists()
    assert not Path(f"prodConf_{gaudi.applicationName}_{fileName}.json").exists()
    assert Path("DISABLE_WATCHDOG_CPU_WALLCLOCK_CHECK").exists()

    # Validate jobReport calls
    expected_calls = [
        ("Error in GaudiApplication module", True),
    ]

    actual_calls = gaudi.jobReport.setApplicationStatus.call_args_list
    actual_calls_args = [(call_args[0][0], call_args[0][1]) for call_args in actual_calls]

    assert len(actual_calls_args) == len(expected_calls), "Unexpected number of calls to setApplicationStatus"
    for expected_call in expected_calls:
        assert expected_call in actual_calls_args, f"Expected call {expected_call} not found in actual calls"


def test_gaudi_outputexception_fail(mocker, gaudi):
    """Test GaudApplication when the application ends successfully but the output is not present."""
    # Mock the GaudiApplication module
    run_app_mock = mocker.patch(
        "LHCbDIRAC.Core.Utilities.RunApplication.RunApplication.run",
        return_value=S_OK((0, "Completed successfully", "")),
    )
    gaudi.applicationName = "Gauss"
    gaudi.applicationVersion = "v49r10"
    gaudi.jobType = "MCSimulation"

    # Mock the outputs: we don't create the sim file here
    outputFileName = f"{prod_id}_{prod_job_id}_{step_number}.ift.dst"
    step_commons[0]["listoutput"] = [
        {"outputDataName": outputFileName, "outputDataType": outputFileName.split("_")[-1]}
    ]

    assert not gaudi.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=step_commons[0],
        step_number=step_number,
        step_id=step_id,
        # Here we have an error in the workflow/step
        stepStatus=S_OK(),
    )["OK"]

    # Check that the application was run
    run_app_mock.assert_called_once()

    # Check the outputs
    fileName = f"{prod_id}_{prod_job_id}_{step_number}"
    assert not Path(f"{fileName}.sim").exists()

    # Validate jobReport calls
    expected_calls = [
        (f"{gaudi.applicationName} step {step_number}", True),
        ("Error in GaudiApplication module", True),
    ]

    actual_calls = gaudi.jobReport.setApplicationStatus.call_args_list
    actual_calls_args = [(call_args[0][0], call_args[0][1]) for call_args in actual_calls]

    assert len(actual_calls_args) == len(expected_calls), "Unexpected number of calls to setApplicationStatus"
    for expected_call in expected_calls:
        assert expected_call in actual_calls_args, f"Expected call {expected_call} not found in actual calls"


def test_gaudi_appexception_fail(mocker, gaudi):
    """Test GaudApplication when there was an application exception during the execution."""
    # Mock the GaudiApplication module
    run_app_mock = mocker.patch(
        "LHCbDIRAC.Core.Utilities.RunApplication.RunApplication.run", side_effect=LHCbApplicationError("App exception")
    )
    gaudi.applicationName = "Gauss"
    gaudi.applicationVersion = "v49r10"
    gaudi.jobType = "MCSimulation"

    assert not gaudi.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=step_commons[0],
        step_number=step_number,
        step_id=step_id,
        # Here we have an error in the workflow/step
        stepStatus=S_OK(),
    )["OK"]

    # Check that the application was run
    run_app_mock.assert_called_once()

    # Check the outputs
    fileName = f"{prod_id}_{prod_job_id}_{step_number}"
    assert not Path(f"{fileName}.sim").exists()

    # Validate jobReport calls
    expected_calls = [
        (f"{gaudi.applicationName} step {step_number}", True),
        ("LHCbApplicationError('App exception')", True),
    ]

    actual_calls = gaudi.jobReport.setApplicationStatus.call_args_list
    actual_calls_args = [(call_args[0][0], call_args[0][1]) for call_args in actual_calls]

    assert len(actual_calls_args) == len(expected_calls), "Unexpected number of calls to setApplicationStatus"
    for expected_call in expected_calls:
        assert expected_call in actual_calls_args, f"Expected call {expected_call} not found in actual calls"


def test_gaudi_lhcbdiracexception_fail(mocker, gaudi):
    """Test GaudApplication when there was a lhcbdirac exception during the execution."""
    # Mock the GaudiApplication module
    run_app_mock = mocker.patch(
        "LHCbDIRAC.Core.Utilities.RunApplication.RunApplication.run", side_effect=LHCbDIRACError("LHCbDIRAC exception")
    )
    gaudi.applicationName = "Gauss"
    gaudi.applicationVersion = "v49r10"
    gaudi.jobType = "MCSimulation"

    assert not gaudi.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=step_commons[0],
        step_number=step_number,
        step_id=step_id,
        # Here we have an error in the workflow/step
        stepStatus=S_OK(),
    )["OK"]

    # Check that the application was run
    run_app_mock.assert_called_once()

    # Check the outputs
    fileName = f"{prod_id}_{prod_job_id}_{step_number}"
    assert not Path(f"{fileName}.sim").exists()

    # Validate jobReport calls
    expected_calls = [
        (f"{gaudi.applicationName} step {step_number}", True),
        ("LHCbDIRACError('LHCbDIRAC exception')", True),
    ]

    actual_calls = gaudi.jobReport.setApplicationStatus.call_args_list
    actual_calls_args = [(call_args[0][0], call_args[0][1]) for call_args in actual_calls]

    assert len(actual_calls_args) == len(expected_calls), "Unexpected number of calls to setApplicationStatus"
    for expected_call in expected_calls:
        assert expected_call in actual_calls_args, f"Expected call {expected_call} not found in actual calls"


def test_gaudi_unknownexception_fail(mocker, gaudi):
    """Test GaudApplication when there was an unknown exception during the execution."""
    # Mock the GaudiApplication module
    run_app_mock = mocker.patch(
        "LHCbDIRAC.Core.Utilities.RunApplication.RunApplication.run", side_effect=RuntimeError("Unknown exception")
    )
    gaudi.applicationName = "Gauss"
    gaudi.applicationVersion = "v49r10"
    gaudi.jobType = "MCSimulation"

    assert not gaudi.execute(
        production_id=prod_id,
        prod_job_id=prod_job_id,
        wms_job_id=wms_job_id,
        workflowStatus=workflowStatus,
        wf_commons=wf_commons[0],
        step_commons=step_commons[0],
        step_number=step_number,
        step_id=step_id,
        # Here we have an error in the workflow/step
        stepStatus=S_OK(),
    )["OK"]

    # Check that the application was run
    run_app_mock.assert_called_once()

    # Check the outputs
    fileName = f"{prod_id}_{prod_job_id}_{step_number}"
    assert not Path(f"{fileName}.sim").exists()

    # Validate jobReport calls
    expected_calls = [
        (f"{gaudi.applicationName} step {step_number}", True),
        ("Error in GaudiApplication module", True),
    ]

    actual_calls = gaudi.jobReport.setApplicationStatus.call_args_list
    actual_calls_args = [(call_args[0][0], call_args[0][1]) for call_args in actual_calls]

    assert len(actual_calls_args) == len(expected_calls), "Unexpected number of calls to setApplicationStatus"
    for expected_call in expected_calls:
        assert expected_call in actual_calls_args, f"Expected call {expected_call} not found in actual calls"
