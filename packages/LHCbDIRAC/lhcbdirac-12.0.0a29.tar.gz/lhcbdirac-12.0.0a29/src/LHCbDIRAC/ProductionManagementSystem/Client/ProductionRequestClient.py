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
"""Module holding ProductionRequestClient class."""
from DIRAC.Core.Base.Client import Client, createClient

from DIRAC.Core.Utilities.ReturnValues import returnValueOrRaise, convertToReturnValue


@createClient("ProductionManagement/ProductionRequest")
class ProductionRequestClient(Client):
    """This class expose the methods of the Production Request Service."""

    def __init__(self, url=None, **kwargs):
        """c'tor.

        :param str url: can specify a specific URL
        """
        super().__init__(**kwargs)
        self.setServer("ProductionManagement/ProductionRequest")
        if url:
            self.setServer(url)

    @convertToReturnValue
    def getProductionRequest(self, requestIDList, columns=None):
        """Return the production request for the given request ID list.

        :param list requestIDList: list of request IDs
        :param list columns: list of columns to return, if None all columns are returned except 'RawRequest'
        :return: dictionary with request IDs as keys and their corresponding requests as values
        """
        result = returnValueOrRaise(self.executeRPC(requestIDList, columns, call="getProductionRequest"))
        # Convert the keys to int to reverse the conversion done by JEncode
        return {int(k): v for k, v in result.items()}

    @convertToReturnValue
    def getAllProductionProgress(self):
        """Return all the production progress."""
        result = returnValueOrRaise(self.executeRPC(call="getAllProductionProgress"))
        # Convert the keys to int to reverse the conversion done by JEncode
        return {int(k): {int(k2): v2 for k2, v2 in v.items()} for k, v in result.items()}

    @convertToReturnValue
    def getProductionRequestSummary(self, status, requestType):
        """Return all the production progress."""
        result = returnValueOrRaise(self.executeRPC(status, requestType, call="getProductionRequestSummary"))
        # Convert the keys to int to reverse the conversion done by JEncode
        return {int(k): v for k, v in result.items()}
