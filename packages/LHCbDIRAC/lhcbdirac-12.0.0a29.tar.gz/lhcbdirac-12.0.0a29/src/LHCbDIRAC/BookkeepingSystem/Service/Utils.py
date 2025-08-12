###############################################################################
# (c) Copyright 2025 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
from __future__ import annotations

from functools import partial

from DIRAC import gLogger

default = "ALL"


def buildCallForGetFilesWithMetadata(bkkDB, in_dict):
    configName = in_dict.get("ConfigName", default)
    configVersion = in_dict.get("ConfigVersion", default)
    conddescription = in_dict.get(
        "ConditionDescription",  # old single
        in_dict.get("SimulationConditions", in_dict.get("DataTakingConditions", default)),
    )
    processing = in_dict.get("ProcessingPass", default)
    evt = in_dict.get("EventType", in_dict.get("EventTypeId", default))
    production = in_dict.get("Production", default)
    filetype = in_dict.get("FileType", default)
    quality = in_dict.get("DataQuality", in_dict.get("DataQualityFlag", in_dict.get("Quality", default)))
    visible = in_dict.get("Visible", "Y")
    replicaFlag = in_dict.get("ReplicaFlag", "Yes")
    startDate = in_dict.get("StartDate", None)
    endDate = in_dict.get("EndDate", None)
    runnumbers = in_dict.get("RunNumber", in_dict.get("RunNumbers", []))
    startRunID = in_dict.get("StartRun", None)
    endRunID = in_dict.get("EndRun", None)
    tcks = in_dict.get("TCK")
    jobStart = in_dict.get("JobStartDate", None)
    jobEnd = in_dict.get("JobEndDate", None)
    smog2States = in_dict.get("SMOG2", None)
    extendedDQOK = in_dict.get("ExtendedDQOK", None)

    method = bkkDB.getFilesWithMetadata
    force_kwargs = {}
    if parameters := in_dict.get("OnlyParameters", None):
        force_kwargs["parameters"] = parameters
    if seed_md5 := in_dict.get("SampleSeedMD5", None):
        force_kwargs["seed_md5"] = seed_md5
    if sample_max := in_dict.get("SampleMax", None):
        force_kwargs["sample_max"] = sample_max

    if force_kwargs:
        # Only the new implementation supports this
        method = partial(bkkDB._newdb.getFilesWithMetadata, **force_kwargs)
    else:
        # TODO: Can be replaced with GETFILESWITHMETADATA_NAME_TO_COL
        parameters = [
            "FileName",
            "EventStat",
            "FileSize",
            "CreationDate",
            "JobStart",
            "JobEnd",
            "WorkerNode",
            "FileType",
            "RunNumber",
            "FillNumber",
            "FullStat",
            "DataqualityFlag",
            "EventInputStat",
            "TotalLuminosity",
            "Luminosity",
            "InstLuminosity",
            "TCK",
            "GUID",
            "ADLER32",
            "EventType",
            "MD5SUM",
            "VisibilityFlag",
            "JobId",
            "GotReplica",
            "InsertTimeStamp",
        ]

    if "EventTypeId" in in_dict:
        gLogger.verbose("The EventTypeId has to be replaced by EventType!")

    if "Quality" in in_dict:
        gLogger.verbose("The Quality has to be replaced by DataQuality!")

    args = (
        configName,
        configVersion,
        conddescription,
        processing,
        evt,
        production,
        filetype,
        quality,
        visible,
        replicaFlag,
        startDate,
        endDate,
        runnumbers,
        startRunID,
        endRunID,
        tcks,
        jobStart,
        jobEnd,
        None,
        smog2States,
        extendedDQOK,
    )
    return method, args, parameters
