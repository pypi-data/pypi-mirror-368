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
"""Utility functions for writing lbexec payloads."""
from __future__ import annotations

__all__ = [
    "read_xml_file_catalog",
    "extract_single_filetype_from_input_file",
    "resolve_input_files",
    "write_summary_xml",
    "get_output_filename",
]

import hashlib
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable, TypedDict

from .cli_utils import log_info  # type: ignore
from .options import DataOptions, OptionsBase, SimulationOptions

SUMMARY_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<summary xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.0" xsi:noNamespaceSchemaLocation="$XMLSUMMARYBASEROOT/xml/XMLSummary.xsd">
    <success>True</success>
    <step>finalize</step>
    <usage><stat unit="KB" useOf="MemoryMaximum">0</stat></usage>
{input_files}
    <output>
{output_files}
    </output>
</summary>
"""
XML_FILE_TEMPLATE = '     <file GUID="" name="{name}" status="full">{n}</file>'

EMPTY_XML_CATALOG = """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<!-- Edited By POOL -->
<!DOCTYPE POOLFILECATALOG SYSTEM "InMemory">
<POOLFILECATALOG>

</POOLFILECATALOG>
"""


class FileCatalogEntry(TypedDict):
    """Type for a file catalog entry."""

    name: str
    """The logical file name (LFN) or physical file name (PFN)."""
    pfn: str
    """The physical file name (PFN) associated with the LFN."""
    guid: str | None
    """The GUID of the file, if available."""


def read_xml_file_catalog(xml_file_catalog):
    """Lookup the LFN->PFN mapping from the XML file catalog."""
    if xml_file_catalog is None:
        return {}

    tree = ET.parse(xml_file_catalog)
    pfn_lookup: dict[str, list[str]] = {}  # type: ignore
    for file in tree.findall("./File"):
        lfns = [x.attrib.get("name") for x in file.findall("./logical/lfn")]
        pfns = [x.attrib.get("name") for x in file.findall("./physical/pfn")]
        if len(lfns) > 1:
            raise NotImplementedError(lfns)
        if lfns:
            lfn = lfns[0]
        elif len(pfns) > 1:
            raise NotImplementedError(pfns)
        else:
            lfn = pfns[0]
        pfn_lookup[f"LFN:{lfn}"] = pfns
    return pfn_lookup


def _hash_file(file_path: str | Path) -> str:
    """Calculate the MD5 hash of a file."""
    md5 = hashlib.md5()
    with Path(file_path).open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            md5.update(chunk)
    return md5.hexdigest().upper()


def add_to_xml_file_catalog(
    xml_file_catalog_path: Path, entries: Iterable[FileCatalogEntry]
):
    """Add entries to the XML file catalog preserving original formatting.

    We intentionally avoid xml.etree.ElementTree to keep:
      - XML declaration (with standalone attr)
      - Comments and DOCTYPE
      - Element ordering & indentation expected by tests
    The expected format (from tests) places <physical> before an empty <logical/>;
    no <lfn> element is written (the reader infers LFN from PFN).
    """
    if not xml_file_catalog_path.exists():
        xml_file_catalog_path.parent.mkdir(parents=True, exist_ok=True)
        xml_file_catalog_path.write_text(EMPTY_XML_CATALOG)

    text = xml_file_catalog_path.read_text()

    # Build insertion text
    file_blocks: list[str] = []
    for entry in entries:
        if (guid := entry.get("guid")) is None:
            h = _hash_file(entry["pfn"])
            guid = f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"
        # Physical first, then empty logical (no <lfn/> tag)
        block = [
            f'  <File ID="{guid}">',
            "    <physical>",
            f'      <pfn filetype="ROOT" name="{entry["pfn"]}"/>',
            "    </physical>",
            "    <logical/>",
            "  </File>",
            "",
        ]
        file_blocks.append("\n".join(block))

    insertion = "".join(file_blocks)
    # Insert before closing tag
    closing_tag = "</POOLFILECATALOG>"
    match text.count(closing_tag):
        case 0:
            raise ValueError(f"Invalid POOL file catalog: missing {closing_tag}")
        case 1:
            idx = text.index(closing_tag)
        case _:
            raise NotImplementedError("Multiple closing tags in POOL file catalog")
    # Preserve any preceding whitespace before closing tag
    new_text = text[:idx].rstrip() + "\n" + insertion + closing_tag + "\n"
    # Add the comment that it was edited by LbExec
    first_line, rest = new_text.split("\n", 1)
    new_text = f"{first_line}\n<!-- Edited By LbExec -->\n{rest}"
    # Write the new text back to the file
    xml_file_catalog_path.write_text(new_text)


def extract_single_filetype_from_input_file(options):
    def _extract(s):
        filename = s.split("/")[-1]
        parts = filename.split(".")
        if len(parts) >= 3:
            return parts[-2]
        raise NotImplementedError

    filetypes = set(_extract(infile) for infile in options.input_files)
    if len(filetypes) != 1:
        raise NotImplementedError(
            "Multiple input filetypes in input_files, when only one filetype was expected."
        )
    return filetypes.pop()


def resolve_input_files(input_files, file_catalog):
    """Resolve LFNs to PFNs using what was returned from read_xml_file_catalog."""
    resolved = []
    for input_file in input_files:
        if input_file.startswith("LFN:"):
            if input_file in file_catalog:
                print("Resolved", input_file, "to", file_catalog[input_file][0])
                input_file = file_catalog[input_file][0]
            else:
                raise ValueError(f"Could not resolve {input_file}: {file_catalog}")
        resolved.append(input_file)
    return resolved


def write_summary_xml(
    options: OptionsBase,
    output_files: Iterable[str],
    *,
    n_events: dict[str, int] | None = None,
):
    """Write a summary XML file with input and output files."""
    if n_events is None:
        n_events = {}
    match options:
        case SimulationOptions():
            input_files = []
        case DataOptions():
            input_files = options.input_files
        case _:
            raise NotImplementedError(f"Unsupported options type: {type(options)}")
    input_files_xml = [
        XML_FILE_TEMPLATE.format(
            name=name if name.startswith("LFN:") else f"PFN:{name}", n=1
        )
        for name in input_files
    ]
    if input_files_xml:
        input_files_xml.insert(0, "    <input>")
        input_files_xml.append("    </input>")

    summary_xml = SUMMARY_XML_TEMPLATE.format(
        input_files="\n".join(input_files_xml),
        output_files="\n".join(
            XML_FILE_TEMPLATE.format(
                # assume that every input file contributed to each output file
                name=f"PFN:{name}",
                n=n_events.get(name, len(input_files)),
            )
            for name in output_files
        ),
    )
    if options.xml_file_catalog:
        if not options.xml_file_catalog.exists():
            options.xml_file_catalog.parent.mkdir(parents=True, exist_ok=True)
            options.xml_file_catalog.write_text(EMPTY_XML_CATALOG)

    if options.xml_summary_file:
        log_info(f"Writing XML summary to {options.xml_summary_file}")
        Path(options.xml_summary_file).write_text(summary_xml)


def get_output_filename(key, options, extra_opts, lumi_tree_key=None):
    if not extra_opts.write:
        # assume we write one output filetype
        # if "output_file" contains {stream}, we need to infer the filetype
        # otherwise return options.output_file

        if "{stream}" not in options.output_file_:
            yield options.output_file
        else:
            # get input filetype, substitute it into {stream}, and yield
            yield extract_single_filetype_from_input_file(options)

    for mapstr in extra_opts.write or []:
        fn, rex = mapstr.split("=")
        if re.match(rex, key) or lumi_tree_key == key:
            yield fn
