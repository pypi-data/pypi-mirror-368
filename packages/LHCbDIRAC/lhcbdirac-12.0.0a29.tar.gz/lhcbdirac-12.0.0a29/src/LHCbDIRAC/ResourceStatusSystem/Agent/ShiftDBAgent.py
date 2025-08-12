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
"""LHCbDIRAC.ResourceStatusSystem.Agent.ShiftDBAgent.

ShiftDBAgent.__bases__:
  DIRAC.Core.Base.AgentModule.AgentModule
"""
# FIXME: should add a "DryRun" option to run in certification setup
from urllib.request import urlopen
from urllib.error import URLError
import json
import requests

from DIRAC import gConfig, S_OK, S_ERROR
from DIRAC.Core.Base.AgentModule import AgentModule
from DIRAC.Interfaces.API.DiracAdmin import DiracAdmin

AGENT_NAME = "ResourceStatus/ShiftDBAgent"


class ShiftDBAgent(AgentModule):
    """This agent queries the LHCb ShiftDB and gets the emails of each piquet
    Then, populates the eGroup associated
    The e-groups admin should be : lhcb-grid-experiment-egroup-admins
    """

    def __init__(self, *args, **kwargs):
        AgentModule.__init__(self, *args, **kwargs)

        # Members initialization

        # ShiftDB url where to find shifter emails
        self.lbshiftdburl = "https://lbshiftdb.cern.ch/list_email"

        self.roles = {}
        self.roleShifters = {}
        self.newShifters = {}

        self.diracAdmin = None

    def initialize(self, *args, **kwargs):
        """Initialize."""

        # === Configuration ===
        self.client_id = self.am_getOption("client_id")
        self.client_secret = self.am_getOption("client_secret")

        self.keycloak_api_token_endpoint = "https://auth.cern.ch/auth/realms/cern/api-access/token"
        self.authzsvc_endpoint = "https://authorization-service-api.web.cern.ch/api/v1.0/"

        self.lbshiftdburl = self.am_getOption("lbshiftdburl", self.lbshiftdburl)

        self.diracAdmin = DiracAdmin()

        return S_OK()

    def beginExecution(self):
        self.log.info("Getting roles from CS")
        _section = self.am_getModuleParam("section")
        self.roles = gConfig.getSections(f"{_section}/roles")
        self.eGroups = {}

        for role in self.roles["Value"]:
            eGroup = gConfig.getValue(f"{_section}/roles/{role}/eGroup")
            if eGroup:
                self.eGroups[role] = eGroup
                self.log.debug(f"Found {role} : {eGroup} ")

        return S_OK()

    def execute(self):
        """Execution."""

        #
        # === Get API Token ===
        self.log.info("Getting API token...")
        try:
            token_resp = requests.post(
                self.keycloak_api_token_endpoint,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "audience": "authorization-service-api",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            token_resp.raise_for_status()
            self.api_token = token_resp.json()["access_token"]
            self.log.info("Token received.\n")
        except Exception as e:
            self.log.error("Failed to get API token:", e)

        self.roleShifters = {}
        self.newShifters = {}

        self.log.info("Getting role emails")

        for role, eGroup in self.eGroups.items():
            self.roles[role] = eGroup

            ccid = self.__getRoleCCID(role)
            if not ccid["OK"]:
                self.log.error(ccid["Message"])
                # We do not return, we keep execution to clean old shifters
                ccid["Value"] = None

            ccid = ccid["Value"]
            self.roleShifters[eGroup] = (ccid, role)

            self.log.info(f"{role} -> {ccid}")

        self.log.info("Setting role CCIDs")
        for eGroup, roleTuple in self.roleShifters.items():
            ccid, role = roleTuple
            if ccid is not None:
                setCCID = self.__setRoleCCID(eGroup, ccid, role)
                if not setCCID["OK"]:
                    self.log.error(setCCID["Message"])

        for newShifterRole, shifterEgroup in self.newShifters.items():
            self.log.info(f"Notifying role {newShifterRole}")
            res = self.__notifyNewShifter(newShifterRole, shifterEgroup)
            if not res["OK"]:
                self.log.error(res["Message"])

        return S_OK()

    def __getRoleCCID(self, role):
        """Get role CCID from shiftDB."""

        try:
            web = urlopen(self.lbshiftdburl, timeout=60)
        except URLError as e:
            return S_ERROR(f"Cannot open URL: {self.lbshiftdburl}, error {e}")

        CCIDperson = []
        listCCID = []

        for line in web.readlines():
            for item in json.loads(line):
                if role in item["role"]:
                    # There are three shifts per day, so we take into account what time is it
                    # before sending the email.
                    CCIDperson = {"id": (self.__getEmailCCID(item["email"])["data"][0]["personId"])}
                    listCCID.append(CCIDperson)

        if not listCCID:
            return S_ERROR("CCID not found")

        return S_OK(listCCID)

    def __getEmailCCID(self, email):
        """Get the CCID of the corresponding email"""

        email_resp = requests.get(
            f"{self.authzsvc_endpoint}Identity/by_email/{email}", headers={"Authorization": f"Bearer {self.api_token}"}
        )
        email_resp.raise_for_status()
        return email_resp.json()

    def __setRoleCCID(self, group_id, ccid, role):
        """Set CCID in eGroup."""

        lastShifterList = []
        lastShifterDelete = {}
        lastShifterDeleteUPN = []

        self.log.info("Getting current group identity members...")
        members_resp = requests.get(
            f"{self.authzsvc_endpoint}Group/{group_id}/members/identities",
            headers={"Authorization": f"Bearer {self.api_token}"},
        )
        members_resp.raise_for_status()
        for i in members_resp.json()["data"]:
            lastShifterList.append(i["personId"])
            lastShifterDelete[i["personId"]] = i["upn"]

        for lastShifter in lastShifterList:
            if lastShifter not in ccid:
                self.log.info(f"{lastShifter} is not anymore shifter, deleting ...")
                lastShifterDeleteUPN.append(lastShifterDelete[lastShifter])

        self.__removeMember(lastShifterDeleteUPN, group_id)

        # Adding a member means it will be the only one in the eGroup, as it is overwritten
        if ccid:
            res = self.__addMember(ccid, group_id, role)
            self.log.info(ccid)
            if not res["OK"]:
                self.log.error(res["Message"])
                return res
            self.log.info(f"{ccid} added successfully to the eGroup for role {role}")

        self.newShifters[role] = group_id

        return S_OK()

    def __removeMember(self, upns, group_id):
        self.log.info("Removing", f"UPNs {upns} to group {group_id}...")
        del_resp = requests.delete(
            f"{self.authzsvc_endpoint}Group/{group_id}/members/identities/",
            headers={"Authorization": f"Bearer {self.api_token}", "Content-Type": "application/json"},
            json=upns,
        )
        if del_resp.ok:
            self.log.info("Members deleted successfully.")
            for identity in del_resp.json()["data"]:
                self.log.verbose(identity["memberIdentity"]["id"], " has been removed")
        else:
            message = "Failed to remove members."
            if del_resp.status_code == 400:
                self.log.error(f"{message} No member to delete")
            else:
                self.log.error(message, f"{del_resp.status_code}: {del_resp.text}")

    def __addMember(self, ccid, group_id, role):
        """Adds a new member to the group."""

        self.log.info(f"Adding member {ccid} to Group {group_id} for role {role}")

        post_resp = requests.post(
            f"{self.authzsvc_endpoint}Group/{group_id}/members/identities/",
            headers={"Authorization": f"Bearer {self.api_token}", "Content-Type": "application/json"},
            json=ccid,
        )

        if not post_resp.ok:
            self.log.error("Failed to add members.", f"{post_resp.status_code}: {post_resp.text}")
            return S_ERROR(post_resp.text)

        self.log.info("Members added successfully.")
        for identity in post_resp.json()["data"]:
            self.log.verbose(identity["identityId"], " has been added")
        return S_OK()

    def __notifyNewShifter(self, role, eGroup):
        """Sends an email to the shifter ( if any ) at the beginning of the shift
        period."""

        if role != "Production":
            self.log.info(f"No email body defined for {role} role")
            return S_OK()
        body = __productionBody__

        prodRole = self.roles["Production"]
        geocRole = self.roles["Grid Expert"]
        body = body % (self.roleShifters[prodRole][0], self.roleShifters[geocRole][0])

        # Hardcoded Concezio's email to avoid dirac@mail.cern.ch be rejected by smtp server
        res = self.diracAdmin.sendMail(
            f"{eGroup}@cern.ch", "Shifter information", body, fromAddress="concezio.bozzi@cern.ch"
        )
        return res


__productionBody__ = """Dear GEOC,

this is an (automatic) mail to welcome you on the grid operations shifts.
In order to facilitate your shift activities we wanted to provide you some pointers,
where you could find more information about shifts, the activities and your duties during this period.

http://lhcb-shifters.web.cern.ch/


LHCbDIRAC portal
https://lhcb-portal-dirac.cern.ch/DIRAC


The logbook for LHCb operations, where all activities concerning offline operation are being logged.
https://lblogbook.cern.ch/Operations/
"""
