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
import os
import struct
import tempfile
from pathlib import Path

import pytest

from LbExec.options import CompressionSettings, Options
from LbExec.workflows import _get_mdf_event_size, merge_mdf


@pytest.fixture
def temp_mdf_files(tmp_path):
    """Create temporary MDF files for testing."""
    files = []

    # Create first MDF file
    file1 = tmp_path / "test1.mdf"
    with open(file1, "wb") as f:
        # Event 1: size = 100 bytes (including 12-byte header)
        event1_size = 100
        header1 = struct.pack("<III", event1_size, event1_size, event1_size)
        data1 = b"\xAA" * (event1_size - 12)  # Fill with pattern

        # Event 2: size = 80 bytes (including 12-byte header)
        event2_size = 80
        header2 = struct.pack("<III", event2_size, event2_size, event2_size)
        data2 = b"\xBB" * (event2_size - 12)  # Fill with different pattern

        f.write(header1 + data1 + header2 + data2)
    files.append(str(file1))

    # Create second MDF file
    file2 = tmp_path / "test2.mdf"
    with open(file2, "wb") as f:
        # Event 3: size = 120 bytes (including 12-byte header)
        event3_size = 120
        header3 = struct.pack("<III", event3_size, event3_size, event3_size)
        data3 = b"\xCC" * (event3_size - 12)  # Fill with another pattern

        f.write(header3 + data3)
    files.append(str(file2))

    return files


@pytest.fixture
def mock_options_yaml(tmp_path):
    """Create a mock options YAML file."""
    yaml_content = """input_files:
- test_file1.mdf
- test_file2.mdf
n_threads: 1
output_file: merged_output.mdf
xml_summary_file: summary.xml
"""
    yaml_file = tmp_path / "test_options.yaml"
    yaml_file.write_text(yaml_content)
    return str(yaml_file)


def create_options_no_compression(input_files, tmp_path):
    """Create Options object without compression."""
    return Options(
        input_files=input_files,
        output_file=str(tmp_path / "output.mdf"),
        xml_summary_file=str(tmp_path / "summary.xml"),
        compression=None,
        n_threads=1,
    )


def create_options_with_compression(input_files, tmp_path):
    """Create Options object with ZSTD compression."""
    return Options(
        input_files=input_files,
        output_file=str(tmp_path / "output.mdf.zst"),
        xml_summary_file=str(tmp_path / "summary.xml"),
        compression=CompressionSettings(algorithm="ZSTD", level=3),
        n_threads=1,
    )


class TestMDFEventSize:
    """Tests for _get_mdf_event_size function."""

    def test_valid_mdf_header(self):
        """Test parsing a valid MDF event header."""
        import ctypes

        # Create a buffer with valid MDF header (size = 100)
        event_size = 100
        buffer_data = (
            struct.pack("<III", event_size, event_size, event_size) + b"\x00" * 50
        )
        buffer = ctypes.create_string_buffer(buffer_data)

        result = _get_mdf_event_size(buffer)
        assert result == event_size

    def test_invalid_mdf_header(self):
        """Test parsing an invalid MDF event header."""
        import ctypes

        # Create a buffer with invalid MDF header (mismatched sizes)
        buffer_data = struct.pack("<III", 100, 200, 100) + b"\x00" * 50
        buffer = ctypes.create_string_buffer(buffer_data)

        with pytest.raises(ValueError, match="MDF file does not have a valid header"):
            _get_mdf_event_size(buffer)


class TestMDFMerge:
    """Tests for merge_mdf function."""

    def test_merge_without_compression(self, temp_mdf_files, tmp_path):
        """Test merging MDF files without compression."""
        input_files = [f"mdf:{f}" for f in temp_mdf_files]
        options = create_options_no_compression(input_files, tmp_path)

        # Call merge_mdf function
        merge_mdf(options)

        # Verify output file exists
        output_file = tmp_path / "output.mdf"
        assert output_file.exists()

        # Verify output file contains merged data
        with open(output_file, "rb") as f:
            data = f.read()

        # Should contain all three events (100 + 80 + 120 = 300 bytes total)
        assert len(data) == 300

        # Verify the events are in the correct order
        # Event 1: header + 0xAA pattern
        assert data[0:12] == struct.pack("<III", 100, 100, 100)
        assert data[12:100] == b"\xAA" * 88

        # Event 2: header + 0xBB pattern
        assert data[100:112] == struct.pack("<III", 80, 80, 80)
        assert data[112:180] == b"\xBB" * 68

        # Event 3: header + 0xCC pattern
        assert data[180:192] == struct.pack("<III", 120, 120, 120)
        assert data[192:300] == b"\xCC" * 108

    def test_merge_with_compression(self, temp_mdf_files, tmp_path):
        """Test merging MDF files with ZSTD compression."""
        input_files = [f"mdf:{f}" for f in temp_mdf_files]
        options = create_options_with_compression(input_files, tmp_path)

        # Call merge_mdf function
        merge_mdf(options)

        # Verify output file exists
        output_file = tmp_path / "output.mdf.zst"
        assert output_file.exists()

        # Verify file is compressed (should be smaller than 300 bytes)
        assert output_file.stat().st_size < 300

        # Decompress and verify content
        import zstandard

        decompressor = zstandard.ZstdDecompressor()
        with open(output_file, "rb") as compressed_file:
            with decompressor.stream_reader(compressed_file) as reader:
                decompressed_data = reader.read()

        # Should contain all three events (100 + 80 + 120 = 300 bytes total)
        assert len(decompressed_data) == 300

        # Verify the events are in the correct order
        # Event 1: header + 0xAA pattern
        assert decompressed_data[0:12] == struct.pack("<III", 100, 100, 100)
        assert decompressed_data[12:100] == b"\xAA" * 88

    def test_unsupported_compression_algorithm(self, temp_mdf_files, tmp_path):
        """Test that unsupported compression algorithms raise NotImplementedError."""
        options = Options(
            input_files=[f"mdf:{temp_mdf_files[0]}"],
            output_file=str(tmp_path / "output.mdf"),
            xml_summary_file=str(tmp_path / "summary.xml"),
            compression=CompressionSettings(algorithm="LZMA", level=6),
            n_threads=1,
        )

        with pytest.raises(NotImplementedError):
            merge_mdf(options)


class TestMDFIntegration:
    """Integration tests for MDF merging workflow."""

    def test_mdf_file_structure(self, temp_mdf_files):
        """Test that the temp MDF files have the expected structure."""
        # Test first file (has two events)
        with open(temp_mdf_files[0], "rb") as f:
            # Read first event header
            header1_data = f.read(12)
            assert len(header1_data) == 12

            sizes1 = struct.unpack("<III", header1_data)
            assert sizes1 == (100, 100, 100)

            # Skip first event data
            f.read(100 - 12)

            # Read second event header
            header2_data = f.read(12)
            assert len(header2_data) == 12

            sizes2 = struct.unpack("<III", header2_data)
            assert sizes2 == (80, 80, 80)

        # Test second file (has one event)
        with open(temp_mdf_files[1], "rb") as f:
            # Read event header
            header_data = f.read(12)
            assert len(header_data) == 12

            sizes = struct.unpack("<III", header_data)
            assert sizes == (120, 120, 120)
