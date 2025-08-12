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

from pathlib import Path

import pytest

from LbExec.utils import add_to_xml_file_catalog, read_xml_file_catalog

EXAMPLES_DIR = Path(__file__).parent / "xml_catalogs"


def test_read_xml_file_catalog():
    catalog = read_xml_file_catalog(EXAMPLES_DIR / "sim.xml")
    assert catalog is not None
    assert catalog["LFN:00246778_00000001_1.sim"] == [
        "00246778_00000001_1.sim"
    ], "LFN to PFN mapping is incorrect"


def test_read_empty_xml_file_catalog():
    catalog = read_xml_file_catalog(EXAMPLES_DIR / "empty.xml")
    assert catalog == {}, "Empty XML file catalog should return an empty dictionary"


def test_add_to_xml_file_catalog(tmp_path: Path):
    catalog_path = tmp_path / "test_catalog.xml"
    entries = [
        {
            "name": "LFN:00246778_00000001_1.sim",
            "pfn": "00246778_00000001_1.sim",
            "guid": "F8AB17CA-92AF-11EF-B4F6-34800DFEACB4",
        }
    ]
    add_to_xml_file_catalog(catalog_path, entries)
    expected = (
        (EXAMPLES_DIR / "sim.xml")
        .read_text()
        .replace(
            "<!-- Edited By POOL -->",
            "<!-- Edited By LbExec -->\n<!-- Edited By POOL -->",
        )
    )
    assert (
        catalog_path.read_text() == expected
    ), "Adding to XML file catalog did not produce the expected output"


def test_add_to_xml_file_catalog_without_guid(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    catalog_path = tmp_path / "test_catalog_no_guid.xml"
    catalog_path.write_text((EXAMPLES_DIR / "sim.xml").read_text())
    (tmp_path / "dummy.dat").write_bytes(b"Dummy data for testing")
    entries = [
        {
            "name": "LFN:dummy.dat",
            "pfn": "dummy.dat",
            "guid": None,
        }
    ]
    monkeypatch.chdir(tmp_path)
    add_to_xml_file_catalog(catalog_path, entries)
    expected = (
        (EXAMPLES_DIR / "sim_plus.xml")
        .read_text()
        .replace(
            "<!-- Edited By POOL -->",
            "<!-- Edited By LbExec -->\n<!-- Edited By POOL -->",
        )
    )
    assert (
        catalog_path.read_text() == expected
    ), "Adding to XML file catalog without GUID did not produce the expected output"
