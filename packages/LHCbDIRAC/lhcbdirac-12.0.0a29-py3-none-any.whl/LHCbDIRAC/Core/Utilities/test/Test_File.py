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
import pytest
from pathlib import Path

from DIRAC import S_OK, S_ERROR
from DIRAC.Core.Utilities.ReturnValues import returnValueOrRaise
from LHCbDIRAC.Core.Utilities.File import getRootFileGUID, getRootFileGUIDs


EXAMPLE_DST_LOCAL = str(Path(__file__).parent / "example.dst")
EXAMPLE_DST_PATH = (
    "/eos/opendata/lhcb/Collision12/CHARM/"
    "LHCb_2012_Beam4000GeV_VeloClosed_MagDown_RealData_Reco14_Stripping21_CHARM_MDST/"
    "00041836/0000/00041836_00009718_1.charm.mdst"
)
EXAMPLE_DST_XROOTD = f"root://eospublic.cern.ch/{EXAMPLE_DST_PATH}"
EXAMPLE_DST_INVALID = "root://example.invalid//file.dst"

EXPECTED_GUIDS = {
    EXAMPLE_DST_LOCAL: "5FE9437E-D958-11EE-AB88-3CECEF1070AC",
    EXAMPLE_DST_XROOTD: "74D8A911-9B80-E411-B80C-E0CB4E29C513",
}


@pytest.mark.parametrize("fn", sorted(EXPECTED_GUIDS))
def test_getRootFileGUID(fn):
    assert getRootFileGUID(fn) == S_OK(EXPECTED_GUIDS[fn])


def test_getRootFileGUID_error():
    assert getRootFileGUID(EXAMPLE_DST_INVALID)["OK"] is False


def test_getRootFileGUIDs():
    result = returnValueOrRaise(getRootFileGUIDs([EXAMPLE_DST_LOCAL, EXAMPLE_DST_XROOTD, EXAMPLE_DST_INVALID]))
    assert set(result["Failed"]) == {EXAMPLE_DST_INVALID}
    assert result["Failed"][EXAMPLE_DST_INVALID].startswith("Error extracting GUID")

    assert result["Successful"] == {
        EXAMPLE_DST_LOCAL: EXPECTED_GUIDS[EXAMPLE_DST_LOCAL],
        EXAMPLE_DST_XROOTD: EXPECTED_GUIDS[EXAMPLE_DST_XROOTD],
    }
