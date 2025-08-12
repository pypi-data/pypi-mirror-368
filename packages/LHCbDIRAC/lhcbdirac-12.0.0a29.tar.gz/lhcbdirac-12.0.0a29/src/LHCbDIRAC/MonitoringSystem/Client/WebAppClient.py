###############################################################################
# (c) Copyright 2025 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

""" Module that contains client access to the WebApp handler.
"""

from DIRAC.Core.Base.Client import Client, createClient


@createClient("Monitoring/WebApp")
class WebAppClient(Client):
    """WebAppClient sets url for the WebAppHandler."""

    def __init__(self, url=None, **kwargs):
        """
        Sets URL for WebApp handler.

        :param str url: url of the WebAppHandler, defaults to "Monitoring/WebApp" if None
        :param kwargs: forwarded to the Base Client class
        """

        super().__init__(**kwargs)

        if not url:
            self.serverURL = "Monitoring/WebApp"

        else:
            self.serverURL = url
