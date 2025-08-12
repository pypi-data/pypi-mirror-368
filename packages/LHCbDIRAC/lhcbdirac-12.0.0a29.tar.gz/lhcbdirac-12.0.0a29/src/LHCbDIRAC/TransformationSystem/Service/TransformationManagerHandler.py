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
"""DISET request handler for the LHCbDIRAC/TransformationDB."""

from DIRAC import S_OK, S_ERROR
from DIRAC.TransformationSystem.Service.TransformationManagerHandler import TransformationManagerHandler as TManagerBase


class TransformationManagerHandlerMixin:
    types_deleteTransformation = [int]

    def export_deleteTransformation(self, transID):
        rc = self.getRemoteCredentials()
        author = rc.get("DN", rc.get("CN"))
        return self.transformationDB.deleteTransformation(transID, author=author)

    types_setHotFlag = [int, bool]

    def export_setHotFlag(self, transID, hotFlag):
        return self.transformationDB.setHotFlag(transID, hotFlag)

    #############################################################################
    #
    # Managing the BkQueries table
    #

    types_addBookkeepingQuery = [int, dict]

    @classmethod
    def export_addBookkeepingQuery(self, transID, queryDict):
        return self.transformationDB.addBookkeepingQuery(transID, queryDict)

    types_deleteBookkeepingQuery = [int]

    @classmethod
    def export_deleteBookkeepingQuery(self, transID):
        return self.transformationDB.deleteBookkeepingQuery(transID)

    types_getBookkeepingQuery = [int]

    @classmethod
    def export_getBookkeepingQuery(self, transID):
        return self.transformationDB.getBookkeepingQuery(transID)

    types_getBookkeepingQueries = [list]

    @classmethod
    def export_getBookkeepingQueries(self, transIDs):
        return self.transformationDB.getBookkeepingQueries(transIDs)

    types_getTransformationsWithBkQueries = [list]

    @classmethod
    def export_getTransformationsWithBkQueries(self, transIDs):
        return self.transformationDB.getTransformationsWithBkQueries(transIDs)

    types_setBookkeepingQueryEndRun = [int, int]

    @classmethod
    def export_setBookkeepingQueryEndRun(self, transID, runNumber):
        return self.transformationDB.setBookkeepingQueryEndRun(transID, runNumber)

    types_setBookkeepingQueryStartRun = [int, int]

    @classmethod
    def export_setBookkeepingQueryStartRun(self, transID, runNumber):
        return self.transformationDB.setBookkeepingQueryStartRun(transID, runNumber)

    types_addBookkeepingQueryRunList = [int, [list]]

    @classmethod
    def export_addBookkeepingQueryRunList(self, transID, runList):
        return self.transformationDB.addBookkeepingQueryRunList(transID, runList)

    #############################################################################
    #
    # Managing the TransformationRuns table
    #

    types_getTransformationRuns = []

    @classmethod
    def export_getTransformationRuns(self, condDict={}, orderAttribute=None, limit=None):
        return self.transformationDB.getTransformationRuns(condDict, orderAttribute=orderAttribute, limit=limit)

    types_insertTransformationRun = [int, int, str]

    @classmethod
    def export_insertTransformationRun(self, transID, runID, selectedSite=""):
        return self.transformationDB.insertTransformationRun(transID, runID, selectedSite="")

    types_getTransformationRunStats = [[int, list]]

    @classmethod
    def export_getTransformationRunStats(self, transIDs):
        if isinstance(transIDs, int):
            transIDs = [transIDs]
        return self.transformationDB.getTransformationRunStats(transIDs)

    types_addTransformationRunFiles = [int, int, list]

    @classmethod
    def export_addTransformationRunFiles(self, transID, runID, lfns):
        return self.transformationDB.addTransformationRunFiles(transID, runID, lfns)

    types_setParameterToTransformationFiles = [int, dict]

    @classmethod
    def export_setParameterToTransformationFiles(self, transID, lfnsDict):
        return self.transformationDB.setParameterToTransformationFiles(transID, lfnsDict)

    types_setTransformationRunStatus = [int, [int, list], str]

    @classmethod
    def export_setTransformationRunStatus(self, transID, runID, status):
        return self.transformationDB.setTransformationRunStatus(transID, runID, status)

    types_setTransformationRunsSite = [int, int, str]

    @classmethod
    def export_setTransformationRunsSite(self, transID, runID, assignedSE):
        return self.transformationDB.setTransformationRunsSite(transID, runID, assignedSE)

    #############################################################################
    #
    # Managing the RunsMetadata table
    #

    types_addRunsMetadata = [int, dict]

    @classmethod
    def export_addRunsMetadata(self, runID, metadataDict):
        """insert run metadata."""
        return self.transformationDB.setRunsMetadata(runID, metadataDict)

    types_updateRunsMetadata = [int, dict]

    @classmethod
    def export_updateRunsMetadata(self, runID, metadataDict):
        """insert run metadata."""
        return self.transformationDB.updateRunsMetadata(runID, metadataDict)

    types_getRunsMetadata = [[list, int]]

    @classmethod
    def export_getRunsMetadata(self, runID):
        """retrieve run metadata."""
        return self.transformationDB.getRunsMetadata(runID)

    types_deleteRunsMetadata = [int]

    @classmethod
    def export_deleteRunsMetadata(self, runID):
        """delete run metadata."""
        return self.transformationDB.deleteRunsMetadata(runID)

    types_getRunsInCache = [dict]

    @classmethod
    def export_getRunsInCache(self, condDict):
        """gets what's in."""
        return self.transformationDB.getRunsInCache(condDict)

    #############################################################################
    #
    # Managing the RunDestination table
    #

    types_getDestinationForRun = [[int, str, list]]

    @classmethod
    def export_getDestinationForRun(self, runIDs):
        """retrieve run destination for a single run or a list of runs."""
        if isinstance(runIDs, int):
            runIDs = [runIDs]
        if isinstance(runIDs, str):
            runIDs = [int(runIDs)]
        # expecting a list of long integers
        return self.transformationDB.getDestinationForRun(runIDs)

    types_getAllDestinationForRuns = [[int, str, list]]

    @classmethod
    def export_getAllDestinationForRuns(self, runIDs):
        """retrieve run destination and raw destination for a single run or a list of runs."""
        if isinstance(runIDs, int):
            runIDs = [runIDs]
        if isinstance(runIDs, str):
            runIDs = [int(runIDs)]
        # expecting a list of long integers
        return self.transformationDB.getAllDestinationForRuns(runIDs)

    types_setDestinationForRun = [int, str, str]

    @classmethod
    def export_setDestinationForRun(self, runID, destination, rawDestination):
        """set run destination."""
        return self.transformationDB.setDestinationForRun(runID, destination=destination, rawDestination=rawDestination)

    #############################################################################
    #
    # Managing the StoredJobDescription table
    #

    types_addStoredJobDescription = [int, str]

    @classmethod
    def export_addStoredJobDescription(self, transformationID, jobDescription):
        return self.transformationDB.addStoredJobDescription(transformationID, jobDescription)

    types_getStoredJobDescription = [int]

    @classmethod
    def export_getStoredJobDescription(self, transformationID):
        return self.transformationDB.getStoredJobDescription(transformationID)

    types_removeStoredJobDescription = [int]

    @classmethod
    def export_removeStoredJobDescription(self, transformationID):
        return self.transformationDB.removeStoredJobDescription(transformationID)

    types_getStoredJobDescriptionIDs = []

    @classmethod
    def export_getStoredJobDescriptionIDs(self):
        return self.transformationDB.getStoredJobDescriptionIDs()


class TransformationManagerHandler(TransformationManagerHandlerMixin, TManagerBase):
    pass
