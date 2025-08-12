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
"""DISET request handler for the LHCbDIRAC/WebAppHandler."""

from DIRAC import gLogger, S_OK, S_ERROR
from DIRAC.MonitoringSystem.Service.WebAppHandler import WebAppHandler as DIRACWebAppHandler


class WebAppHandler(DIRACWebAppHandler):

    types_getTransformationRunsSummaryWeb = [dict, list, int, int]

    def export_getTransformationRunsSummaryWeb(self, selectDict, sortList, startItem, maxItems):
        """Get the summary of the transformation run information for a given page
        in the generic format."""

        # Obtain the timing information from the selectDict
        last_update = selectDict.get("LastUpdate", None)
        if last_update:
            del selectDict["LastUpdate"]
        fromDate = selectDict.get("FromDate", None)
        if fromDate:
            del selectDict["FromDate"]
        if not fromDate:
            fromDate = last_update
        toDate = selectDict.get("ToDate", None)
        if toDate:
            del selectDict["ToDate"]
        # Sorting instructions. Only one for the moment.
        if sortList:
            orderAttribute = sortList[0][0] + ":" + sortList[0][1]
        else:
            orderAttribute = None

        # Get the transformations that match the selection
        res = self.transformationDB.getTransformationRuns(
            condDict=selectDict, older=toDate, newer=fromDate, orderAttribute=orderAttribute
        )
        if not res["OK"]:
            self.log.error("TransformationManager.getTransformationRuns()", res["Message"])
            return res

        # Prepare the standard structure now within the resultDict dictionary
        resultDict = {}
        trList = res["Records"]
        # Create the total records entry
        nTrans = len(trList)
        resultDict["TotalRecords"] = nTrans
        # Create the ParameterNames entry
        paramNames = res["ParameterNames"]
        resultDict["ParameterNames"] = list(paramNames)

        # Add the job states to the ParameterNames entry
        # taskStateNames   = ['Created','Running','Submitted','Failed','Waiting','Done','Stalled']
        # resultDict['ParameterNames'] += ['Jobs_'+x for x in taskStateNames]
        # Add the file states to the ParameterNames entry
        fileStateNames = [
            "PercentProcessed",
            "Processed",
            "Unused",
            "Assigned",
            "Total",
            "Problematic",
            "ApplicationCrash",
            "MaxReset",
        ]
        resultDict["ParameterNames"] += ["Files_" + x for x in fileStateNames]

        # Get the transformations which are within the selected window
        if nTrans == 0:
            return S_OK(resultDict)
        ini = startItem
        last = ini + maxItems
        if ini >= nTrans:
            return S_ERROR("Item number out of range")
        if last > nTrans:
            last = nTrans
        transList = trList[ini:last]
        if not transList:
            return S_OK(resultDict)

        # Obtain the run statistics for the requested transformations
        transIDs = []
        for transRun in transList:
            transRunDict = dict(zip(paramNames, transRun))
            transID = int(transRunDict["TransformationID"])
            if transID not in transIDs:
                transIDs.append(transID)
        res = self.transformationDB.getTransformationRunStats(transIDs)
        if not res["OK"]:
            return res
        transRunStatusDict = res["Value"]

        statusDict = {}
        # Add specific information for each selected transformation/run
        for transRun in transList:
            transRunDict = dict(zip(paramNames, transRun))
            transID = transRunDict["TransformationID"]
            runID = transRunDict["RunNumber"]
            if transID not in transRunStatusDict or runID not in transRunStatusDict[transID]:
                for state in fileStateNames:
                    transRun.append(0)
                continue
            # Update the status counters
            status = transRunDict["Status"]
            statusDict[status] = statusDict.setdefault(status, 0) + 1

            # Populate the run file statistics
            fileDict = transRunStatusDict[transID][runID]
            if fileDict["Total"] == 0:
                fileDict["PercentProcessed"] = 0
            else:
                processed = fileDict.get("Processed", 0)
                fileDict["PercentProcessed"] = f"{int(processed * 1000.0 / fileDict['Total']) / 10.0:.1f}"
            for state in fileStateNames:
                if fileDict and state in fileDict:
                    transRun.append(fileDict[state])
                else:
                    transRun.append(0)

            # Get the statistics on the number of jobs for the transformation
            # res = database.getTransformationTaskRunStats(transID)
            # taskDict = {}
            # if res['OK'] and res['Value']:
            #  taskDict = res['Value']
            # for state in taskStateNames:
            #  if taskDict and taskDict.has_key(state):
            #    trans.append(taskDict[state])
            #  else:
            #    trans.append(0)

        resultDict["Records"] = transList
        resultDict["Extras"] = statusDict
        return S_OK(resultDict)
