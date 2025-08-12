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
from __future__ import annotations

import argparse
import ctypes
import re
import sys
import time
from collections import defaultdict

from .cli_utils import log_error, log_info, log_warn  # type: ignore
from .options import Options
from .utils import (
    get_output_filename,
    read_xml_file_catalog,
    resolve_input_files,
    write_summary_xml,
)

MDF_MERGE_CHUNK_SIZE = 1024 * 1024  # 1MB chunk size for merging MDF files


def skim_and_merge(options: Options, *extra_args):
    """Take given input files, merge specified object keys from them and write to a corresponding output file."""

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--write",
        action="append",
        help="Write to given file name the tree(s) matching a regular expression . e.g. --write XICP.ROOT='Xic.*/DecayTree'",
    )
    parser.add_argument(
        "--lumi-tuple",
        default="(GetIntegratedLuminosity|lumiTree)",
        help="Regular expression to match key containing Luminosity information. Set to 'none' to ignore.",
    )
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Allow trees in the input file(s) to be missing from the output files.",
    )
    parser.add_argument(
        "--allow-duplicates",
        action="store_true",
        help="Allow trees in the input file(s) to be copied to more than one output file.",
    )

    extra_opts = parser.parse_args(extra_args)

    if options.n_threads > 1:
        raise NotImplementedError

    import ROOT  # type: ignore

    def clean_directories(filename):
        log_info(f"-- clean up {filename} --")
        rf = ROOT.TFile.Open(filename, "UPDATE")  # pylint: disable=no-member
        for key in rf.GetListOfKeys():
            key_name = key.GetName()
            key_type = key.GetClassName()
            if key_type in ["TDirectory", "TDirectoryFile"]:
                key_object = rf.Get(key_name)
                # check that the tdir is empty
                if key_object.GetNkeys() == 0:
                    rf.rmdir(key_name)
                    log_info(f"{filename}: Cleaned up empty {key_type} {key_name}.")
                else:
                    log_info(
                        f"{filename}: Purging unnecessary cycles in non-empty {key_type} {key_name}."
                    )
                    key_object.Purge()
        rf.Close()

    compression_level = None
    if options.compression:
        # pylint: disable=no-member
        algorithms = {
            "ZLIB": ROOT.RCompressionSetting.EAlgorithm.kZLIB,
            "ZSTD": ROOT.RCompressionSetting.EAlgorithm.kZSTD,
            "LZ4": ROOT.RCompressionSetting.EAlgorithm.kLZ4,
            "LZMA": ROOT.RCompressionSetting.EAlgorithm.kLZMA,
        }
        algo = options.compression.algorithm
        level = options.compression.level
        if algo not in algorithms:
            log_error(f"Unknown compression algorithm {algo}")
            sys.exit(1)
        compression_level = algorithms[algo] * 100 + int(level)
        log_info(f"Compression specified as {algo}:{level} ({compression_level})")

    input_files = options.input_files
    if options.xml_file_catalog:
        file_catalog = read_xml_file_catalog(options.xml_file_catalog)
        input_files = resolve_input_files(options.input_files, file_catalog)

    output_files: set = set()
    all_trees: set = set()
    tree_keys = defaultdict(set)
    lumi_tree_key = None
    for input_file in input_files:
        rf = ROOT.TFile.Open(input_file)  # pylint: disable=no-member
        for key in rf.GetListOfKeys():
            key_name = key.GetName()
            key_type = key.GetClassName()

            # check if TDir is empty and should be ignored
            if key_type in ["TDirectory", "TDirectoryFile"]:
                key_object = rf.Get(key_name)
                # check whether the tdir is empty
                if key_object.GetNkeys() == 0:
                    log_info(
                        f"{input_file}: empty {key_type} {key_name} - not considered."
                    )
                    continue

            if re.match(extra_opts.lumi_tuple, key_name) is None:
                no_match = True
                for out_fn in get_output_filename(key_name, options, extra_opts):
                    no_match = False
                    tree_keys[out_fn].add(key_name)
                if no_match:  # FIXME can we do better?!
                    tree_keys[None].add(key_name)
            else:
                lumi_tree_key = key_name
                for out_fn in get_output_filename(
                    key_name, options, extra_opts, lumi_tree_key=lumi_tree_key
                ):
                    tree_keys[out_fn].add(key_name)
            all_trees.add(key_name)
        rf.Close()
        del rf

    if not lumi_tree_key and extra_opts.lumi_tuple != "none":
        log_info(
            f"Luminosity info directory {extra_opts.lumi_tuple} was not found in any input file."
        )

    # check for duplication
    for tree_name in all_trees:
        if lumi_tree_key == tree_name:
            continue  # duplicates are normal for the lumi trees.
        found = 0
        for trees in tree_keys.values():
            if tree_name in trees:
                found += 1
            if found > 1 and not extra_opts.allow_duplicates:
                log_error(
                    f"Duplicates of directory {tree_name} across more than one file. Set --allow-duplicates if this is intended."
                )
                sys.exit(1)

    for stream, tree_names in tree_keys.items():
        if stream is None:
            for tree_name in tree_names:
                log_warn(f"Tree {tree_name} is missing from output file(s).")
            if extra_opts.allow_missing:
                continue
            log_error(
                "Some directories of the input files would not be copied to any output files. Set --allow-missing if this is intended."
            )
            sys.exit(1)

        op_time = time.time()
        # isLocal, histoOneGo (?)
        merger = ROOT.TFileMerger(False, False)  # pylint: disable=no-member
        merger.SetPrintLevel(2)
        if options.compression:
            merger.SetFastMethod(not options.compression.optimise_baskets)

        for input_file in input_files:
            if not merger.AddFile(input_file):
                log_error(f"Couldn't add input file to merger: {input_file}")
                sys.exit(1)

        merge_opts = (
            ROOT.TFileMerger.kAll  # pylint: disable=no-member
            | ROOT.TFileMerger.kRegular  # pylint: disable=no-member
            | ROOT.TFileMerger.kOnlyListed  # pylint: disable=no-member
        )

        for tree_name in tree_names:
            log_info(
                f"SKIM directory {tree_name} FROM {len(input_files)} files ---> {options.get_output_file(stream)}"
            )
            merger.AddObjectNames(tree_name)

        if compression_level:
            merger.OutputFile(
                options.get_output_file(stream),
                "RECREATE",
                compression_level,
            )
        else:
            merger.OutputFile(options.get_output_file(stream), "RECREATE")
        output_files.add(options.get_output_file(stream))
        if not merger.PartialMerge(merge_opts):
            log_error("TFileMerger::PartialMerge failed!")
            sys.exit(1)

        # Explicitly delete TFileMerger as if not the file is not fully flushed to disk
        # and the later call to clean_directories will corrupt the file
        del merger

        log_info(f"    ... took {time.time() - op_time:.1f} seconds")

    for ofn in output_files:
        clean_directories(ofn)

    write_summary_xml(options, output_files)
    return options


def process_trees(process_tree_fn, branch_regex=".*", ignore_lumi_tree=True):
    """A helpful decorator which calls the decorated function for each tree encountered in the input file(s).

    The decorated function is provided both the tree name and an RDataFrame object which can be used to transform the tree.
    This RDataFrame object should be returned, as it is used to snapshot the transformed tree and store it in
    the output file.

    The decorator can be passed a `branch_regex` kwarg to select which branches should be saved in the output.
    """

    def entrypoint(options: Options):
        import ROOT

        input_files = options.input_files
        if options.xml_file_catalog:
            file_catalog = read_xml_file_catalog(options.xml_file_catalog)
            input_files = resolve_input_files(options.input_files, file_catalog)

        trees = []

        rf = ROOT.TFile.Open(input_files[0])  # pylint: disable=no-member
        for key in rf.GetListOfKeys():
            key_name = key.GetName()
            classname = key.GetClassName()
            print(f"{key_name}: {classname}")
            if classname == "TTree":
                trees.append(key_name)
            elif classname.startswith("TDirectory"):
                for key2 in rf.Get(key_name).GetListOfKeys():
                    if key2.GetClassName() == "TTree":
                        trees.append(f"{key_name}/{key2.GetName()}")

        print(f"Found in file: {trees}")

        rf.Close()
        del rf

        for tree_name in trees:
            out_opts = ROOT.RDF.RSnapshotOptions()  # pylint: disable=no-member
            out_opts.fMode = "UPDATE"  # In case the Tree name maps to the same file
            out_opts.fOverwriteIfExists = True
            print("Processing tree ", tree_name, "...")
            rdf = ROOT.RDataFrame(  # pylint: disable=no-member
                tree_name,
                input_files,
            )

            if (
                tree_name not in ["lumiTree", "GetIntegratedLuminosity/LumiTuple"]
                or not ignore_lumi_tree
            ):
                rdf = process_tree_fn(tree_name, rdf)

            rdf.Snapshot(
                tree_name,
                options.output_file,
                branch_regex,
                out_opts,
            )
            print(f"Snapshot of {tree_name} written to {options.output_file}.")
            del rdf

        write_summary_xml(
            options,
            {options.output_file},
        )

    return entrypoint


def _get_mdf_event_size(buffer: ctypes.Array[ctypes.c_char]) -> int:
    """Extract the event size from the MDF buffer."""
    raw_bytes = buffer.raw
    size = int.from_bytes(raw_bytes[0:4], "little")
    for i in range(4, 12, 4):
        if int.from_bytes(raw_bytes[i : i + 4], "little") != size:
            raise ValueError("MDF file does not have a valid header.")
    return size


def merge_mdf(options: Options):
    """Merge MDF files into a single compressed output file."""
    from typing import BinaryIO, cast

    import ROOT  # type: ignore[import-untyped]
    import zstandard

    input_files = options.input_files
    if options.xml_file_catalog:
        file_catalog = read_xml_file_catalog(options.xml_file_catalog)
        input_files = resolve_input_files(options.input_files, file_catalog)

    output_ctx: BinaryIO
    if options.compression is None:
        print("Merging MDF files without compression...")
        output_ctx = open(options.output_file, "wb")
    elif options.compression.algorithm == "ZSTD":
        level = options.compression.level * 2
        print(f"Using Zstandard compressor with level {level}...")
        comp_params = zstandard.ZstdCompressionParameters.from_level(level)
        comp = zstandard.ZstdCompressor(compression_params=comp_params)
        raw_file = open(  # pylint: disable=consider-using-with
            options.output_file, "wb"
        )
        output_ctx = cast(BinaryIO, comp.stream_writer(raw_file))
    else:
        raise NotImplementedError(options.compression)

    bytes_read = 0
    next_progress_print = MDF_MERGE_CHUNK_SIZE * 100
    buffer = ctypes.create_string_buffer(MDF_MERGE_CHUNK_SIZE)
    start_time = time.time()
    with output_ctx as fh:
        for input_file in input_files:
            input_file = input_file.removeprefix("mdf:")
            print("Reading input file:", input_file)
            header_checked = False
            with ROOT.TFile.Open(  # pylint: disable=no-member
                f"{input_file}?filetype=raw"
            ) as rf:
                to_read = rf.GetSize()
                while to_read > 0:
                    requested = min(to_read, MDF_MERGE_CHUNK_SIZE)
                    failure = rf.ReadBuffer(buffer, requested)
                    if failure:
                        raise RuntimeError(f"Failed to read from file {input_file}.")
                    to_read -= requested
                    bytes_read += requested

                    # Safety check to make sure we're actually reading a valid MDF file
                    if not header_checked:
                        first_event_size = _get_mdf_event_size(buffer)
                        # If possible, check the second event header
                        if first_event_size + 12 < bytes_read:
                            second_buffer = ctypes.create_string_buffer(
                                buffer.raw[first_event_size:]
                            )
                            _get_mdf_event_size(second_buffer)
                        header_checked = True

                    if bytes_read >= next_progress_print:
                        print(
                            f"Status: {bytes_read / (1024 * 1024):.2f} MiB read and "
                            f"{fh.tell() / (1024 * 1024):.2f} MiB written "
                            f"in {time.time() - start_time:.2f} seconds."
                        )
                        next_progress_print += MDF_MERGE_CHUNK_SIZE * 100

                    fh.write(memoryview(buffer)[:requested])
        fh.flush()
        bytes_written = fh.tell()
        end_time = time.time()
        print(f"Total bytes read: {bytes_read} ({bytes_read / (1024 * 1024):.2f} MiB)")
        print(
            f"Total bytes written: {bytes_written} ({bytes_written / (1024 * 1024):.2f} MiB)"
        )
        print(f"Compression ratio: {bytes_written / bytes_read:.2f}")
        print(f"Total time taken: {end_time - start_time:.2f} seconds.")

    print(f"Finished merging MDF files into {options.output_file}.")
    write_summary_xml(options, {options.output_file})
