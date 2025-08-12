###############################################################################
# (c) Copyright 2022-2024 CERN for the benefit of the LHCb Collaboration      #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
from __future__ import annotations

__all__ = ["Options", "DataOptions", "SimulationOptions"]

import glob
import re
from enum import Enum
from itertools import product
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing_extensions import Annotated


class CompressionAlgs(str, Enum):
    """ROOT compression algorithms."""

    ZLIB = "ZLIB"
    LZMA = "LZMA"
    LZ4 = "LZ4"
    ZSTD = "ZSTD"


class CompressionSettings(BaseModel):
    """Compression configuration settings."""

    algorithm: CompressionAlgs = CompressionAlgs.ZSTD
    level: int = 4
    optimise_baskets: bool = True


class OptionsBase(BaseModel):
    xml_file_catalog: Optional[Path] = None
    """XML file catalog to use for mapping LFNs to PFNs."""
    output_file_: Annotated[str, Field(alias="output_file")]
    """Output file name, can contain {stream} to be replaced by the stream name."""
    compression: Optional[CompressionSettings] = None
    """Compression settings for the output file."""
    xml_summary_file: Optional[str] = None
    """XML summary file to write job information to."""
    n_threads: int = 1
    """Number of threads to use for execution."""
    evt_max: int = -1
    """Number of events to simulate."""
    first_evt: int = 0
    """The first event to process."""

    # Pydantic v2 configuration
    model_config = ConfigDict(use_enum_values=True, frozen=True, extra="forbid")

    @property
    def output_file(self) -> str:
        if "{stream}" in self.output_file_:
            raise ValueError(
                "output_file contains {stream} and get_output_file must be used instead."
            )
        return self.output_file_

    def get_output_file(self, stream: str) -> str:
        return self.output_file_.format(stream=stream)


class SimulationSeeds(BaseModel):
    """Seeds which simulation jobs can use to ensure reproducibility."""

    production_id: int
    """The transformation ID in LHCbDIRAC."""
    prod_job_id: int
    """The sequential job number within the transformation."""


class SimulationOptions(OptionsBase):
    """Base options class for simulation jobs."""

    seeds: SimulationSeeds
    """The seeds to use for the simulation."""

    @field_validator("evt_max")
    def validate_evt_max(cls, evt_max):
        if evt_max <= 0:
            raise ValueError("evt_max must be a positive integer when simulating")
        return evt_max


class DataOptions(OptionsBase):
    """Base options class for job which have input files."""

    input_files: list[str]
    """List of input files to process."""

    @field_validator("input_files", mode="before")
    def glob_input_files(cls, input_files):
        if isinstance(input_files, str):
            resolved_input_files = []
            for pattern in _expand_braces(input_files):
                if "*" not in pattern:
                    resolved_input_files.append(pattern)
                    continue
                if pattern.startswith("root://"):
                    raise NotImplementedError("Cannot glob with XRootD URLs")
                matches = glob.glob(pattern, recursive=True)
                if not matches:
                    raise ValueError(f"No input files found matching {pattern!r}")
                resolved_input_files += matches
            return resolved_input_files
        return input_files

    @model_validator(mode="before")
    def validate_input(cls, values):
        if not values.get("input_files"):
            raise ValueError("'input_files' is required.")
        return values


# For backwards compatibility
Options = DataOptions


def _expand_braces(text):
    """Perform bash-like brace expansion

    See: https://www.gnu.org/software/bash/manual/html_node/Brace-Expansion.html

    There are two notable deviations from the bash behaviour:
     * Duplicates are removed from the output
     * The order of the returned results can differ
    """
    seen = set()
    # HACK: Use a reserved unicode page to substitute patterns like {abc} that
    # don't contain a comma and should therefore have the curly braces preserved
    # in the output
    substitutions = {"\uE000": ""}
    for s in _expand_braces_impl(text, seen, substitutions):
        for k, v in reversed(substitutions.items()):
            s = s.replace(k, v)
        if s:
            yield s


def _expand_braces_impl(text, seen, substitutions):
    int_range_pattern = r"[\-\+]?[0-9]+(\.[0-9]+)?(\.\.[\-\+]?[0-9]+(\.[0-9]+)?){1,2}"
    char_range_pattern = r"([a-z]\.\.[a-z]|[A-Z]\.\.[A-Z])(\.\.[\-\+]?[0-9]+)?"
    patterns = [
        ",",
        r"([^{}]|{})*,([^{}]|{})+",
        r"([^{}]|{})+,([^{}]|{})*",
        int_range_pattern,
        char_range_pattern,
        r"([^{},]|{})+",
    ]
    spans = [m.span() for m in re.finditer(rf"{{({'|'.join(patterns)})}}", text)][::-1]
    if len(spans) == 0:
        if text not in seen:
            yield text
        seen.add(text)
        return

    alts = []
    for start, stop in spans:
        alt_full = text[start:stop]
        alt = alt_full[1:-1].split(",")
        is_int_range = re.fullmatch(rf"{{{int_range_pattern}}}", alt_full)
        is_char_range = re.fullmatch(rf"{{{char_range_pattern}}}", alt_full)
        if is_int_range or is_char_range:
            range_args = alt[0].split("..")
            leading_zeros = 0
            if any(
                len(x) > 1 and x.strip("-")[0] == "0" and x.strip("-") != "0"
                for x in range_args[:2]
            ):
                leading_zeros = max(map(len, range_args[:2]))
            start, stop = map(int if is_int_range else ord, range_args[:2])
            step = int(range_args[2]) if len(range_args) == 3 else 0
            step = 1 if step == 0 else abs(int(step))
            if stop < start:
                step = -step
            stop = stop + int(step / abs(step))
            alt = [
                f"{s:0{leading_zeros}d}" if is_int_range else chr(s)
                for s in range(start, stop, step)
            ]
        elif len(alt) == 1:
            substitution = chr(0xE000 + len(substitutions))
            substitutions[substitution] = alt_full
            alt = [substitution]
        alts.append(alt)

    for combo in product(*alts):
        replaced = list(text)
        for (start, stop), replacement in zip(spans, combo):
            # Add dummy charactors to prevent brace expansion being applied recursively
            # i.e. "{{0..1}2}" should become "{02}" "{12}" not "02" "12"
            replaced[start:stop] = f"\uE000{replacement}\uE000"

        yield from _expand_braces_impl("".join(replaced), seen, substitutions)
