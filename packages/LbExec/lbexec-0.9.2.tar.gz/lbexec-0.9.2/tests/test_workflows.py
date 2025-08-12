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
import sys
from pathlib import Path

import numpy as np
import pytest
import skhep_testdata as hepdat
import uproot

from LbExec.__main__ import parse_args

LBEXEC_CMD = ["lbexec"]
OPTIONS_FN = str(Path(__file__).parent / "example.yaml")
OPTIONS_FN_COMPRESSION = str(Path(__file__).parent / "example_compression.yaml")
OPTIONS_FN_COMPRESSION_BAD = str(Path(__file__).parent / "example_compresion_bad.yaml")

OPTIONS_FN_SPLIT_WITH_EMPTY_TREES = str(
    Path(__file__).parent / "example_split_with_empty_trees.yaml"
)
OPTIONS_FN_SPLIT_WITH_EMPTY_TREES2 = str(
    Path(__file__).parent / "example_split_with_empty_trees_2.yaml"
)
OPTIONS_FN_SPLIT_WITH_EMPTY_TREES3 = str(
    Path(__file__).parent / "example_split_with_empty_trees_3.yaml"
)
OPTIONS_FN_SPLIT_WITH_EMPTY_TREES4 = str(
    Path(__file__).parent / "example_split_with_empty_trees_4.yaml"
)
OPTIONS_FN_SPLIT_WITH_EMPTY_TREES5 = str(
    Path(__file__).parent / "example_split_with_empty_trees_5.yaml"
)

OPTIONS_FN_SIMPLE_MERGE = str(Path(__file__).parent / "example_simple_merge.yaml")
OPTIONS_FN_SIMPLE_MERGE_WITH_STREAM = str(
    Path(__file__).parent / "example_simple_merge_single_filetype_with_stream.yaml"
)
OPTIONS_FN_SIMPLE_MERGE_SIMPLER = str(
    Path(__file__).parent / "example_simple_merge_simpler.yaml"
)
OPTIONS_FN_SIMPLE_MERGE_EMPTY_TREES = str(
    Path(__file__).parent / "example_simple_merge_empty_trees.yaml"
)
OPTIONS_FN_SIMPLE_MERGE_NO_LUMI_TREE = str(
    Path(__file__).parent / "example_simple_merge_no_lumi_tree.yaml"
)
OPTIONS_FN_SIMPLE_MERGE_NO_LUMI_TREE_MULTI = str(
    Path(__file__).parent / "example_simple_merge_no_lumi_tree_multi.yaml"
)
FUNCTION_SPEC = "LbExec:skim_files"
LBEXEC_EXAMPLE_CMD = LBEXEC_CMD + [FUNCTION_SPEC, OPTIONS_FN]


def getfkeys(rf):
    return [key.split(";")[0] for key in rf.keys()]


# if not os.path.exists("tests/test_files/tuple1.root"):
with uproot.open(hepdat.data_path("uproot-HZZ.root")) as rf:
    testtree = rf["events"].arrays(
        [
            "NMuon",
            "NElectron",
            "NPhoton",
            "MET_px",
            "MET_py",
            "MChadronicBottom_px",
            "MChadronicBottom_py",
            "MChadronicBottom_pz",
            "MChadronicWDecayQuark_px",
            "MChadronicWDecayQuark_py",
            "MChadronicWDecayQuark_pz",
            "MClepton_px",
            "MClepton_py",
            "MClepton_pz",
            "MCneutrino_px",
            "MCneutrino_py",
            "MCneutrino_pz",
            "NPrimaryVertices",
            "EventWeight",
        ]
    )
    testlumitree = rf["events"].arrays(
        [
            "EventWeight",
        ]
    )

f1 = uproot.recreate("tests/test_files/tuple1.root")
f1["events1/DecayTree"] = testtree
f1["events2/DecayTree"] = testtree
f1["GetIntegratedLuminosity/LumiTuple"] = testlumitree
f2 = uproot.recreate("tests/test_files/tuple2.root")
f2["events1/DecayTree"] = testtree
f2["events2/DecayTree"] = testtree
f2["GetIntegratedLuminosity/LumiTuple"] = testlumitree

f1 = uproot.recreate("tests/test_files/tuple1.stream1.root")
f1["events1/DecayTree"] = testtree
f1["events2/DecayTree"] = testtree
f1["GetIntegratedLuminosity/LumiTuple"] = testlumitree
f2 = uproot.recreate("tests/test_files/tuple2.stream1.root")
f2["events1/DecayTree"] = testtree
f2["events2/DecayTree"] = testtree
f2["GetIntegratedLuminosity/LumiTuple"] = testlumitree


f2 = uproot.recreate("tests/test_files/tuple3.root")
f2["events2/DecayTree"] = testtree
f2["GetIntegratedLuminosity/LumiTuple"] = testlumitree

f2 = uproot.recreate("tests/test_files/tuple4.root")
f2["GetIntegratedLuminosity/LumiTuple"] = testlumitree

f2 = uproot.recreate("tests/test_files/tuple5.root")
f2["lumiTree"] = testlumitree

f2 = uproot.recreate("tests/test_files/tuple6.root")
f2["events1/DecayTree"] = testtree
f2["GetIntegratedLuminosity/LumiTuple"] = testlumitree


@pytest.mark.parametrize(
    "function_spec,options_spec,extra_args",
    [
        [
            "LbExec:skim_and_merge",
            OPTIONS_FN,
            ["--write", "EVENTS1=events1", "--write", "EVENTS2=events2"],
        ],
        [
            "LbExec:skim_and_merge",
            OPTIONS_FN_COMPRESSION,
            [
                "--write",
                "EVENTS1=events1",
                "--write",
                "EVENTS2=events2",
            ],
        ],
        [
            "LbExec:skim_and_merge",
            OPTIONS_FN_SPLIT_WITH_EMPTY_TREES,
            [
                "--write",
                "EVENTS1=events1",
                "--write",
                "EVENTS2=events2",
            ],
        ],
        [
            "LbExec:skim_and_merge",
            OPTIONS_FN_SPLIT_WITH_EMPTY_TREES2,
            [
                "--write",
                "EVENTS1=events1",
                "--write",
                "EVENTS2=events2",
            ],
        ],
        [
            "LbExec:skim_and_merge",
            OPTIONS_FN_SPLIT_WITH_EMPTY_TREES3,
            [
                "--write",
                "EVENTS1=events1",
                "--write",
                "EVENTS2=events2",
            ],
        ],
        [
            "LbExec:skim_and_merge",
            OPTIONS_FN_SPLIT_WITH_EMPTY_TREES4,
            [
                "--write",
                "EVENTS1=events1",
                "--write",
                "EVENTS2=events2",
            ],
        ],
        [
            "LbExec:skim_and_merge",
            OPTIONS_FN_SPLIT_WITH_EMPTY_TREES5,
            [
                "--write",
                "EVENTS1=events1",
                "--write",
                "EVENTS2=events2",
            ],
        ],
        [
            "LbExec:skim_and_merge",
            OPTIONS_FN,
            ["--write", "_EVENTS2=events2", "--allow-missing"],
        ],
        [
            "LbExec:skim_and_merge",
            OPTIONS_FN_SIMPLE_MERGE,
            [],
        ],
        [
            "LbExec:skim_and_merge",
            OPTIONS_FN_SIMPLE_MERGE_WITH_STREAM,
            [],
        ],
        [
            # duplicates
            "LbExec:skim_and_merge",
            OPTIONS_FN,
            [
                "--write",
                "__EVENTS1=events1",
                "--write",
                "__EVENTS2=events2",
                "--write",
                "__EVENTS22=events2",
                "--allow-duplicates",
            ],
        ],
        [
            "LbExec:skim_and_merge",
            OPTIONS_FN_SIMPLE_MERGE_EMPTY_TREES,
            [],
        ],
        [
            "LbExec:skim_and_merge",
            OPTIONS_FN_SIMPLE_MERGE_NO_LUMI_TREE,
            [],
        ],
        [
            "LbExec:skim_and_merge",
            OPTIONS_FN_SIMPLE_MERGE_NO_LUMI_TREE_MULTI,
            [],
        ],
        [
            "LbExec:skim_and_merge",
            OPTIONS_FN_SIMPLE_MERGE_SIMPLER,
            [],
        ],
    ],
)
def test_valid_workflow(capfd, monkeypatch, function_spec, options_spec, extra_args):
    monkeypatch.setattr(
        sys, "argv", LBEXEC_CMD + [function_spec, options_spec] + ["--"] + extra_args
    )

    parse_args()
    captured = capfd.readouterr()

    print(captured.out)
    print(captured.err)

    if options_spec in [OPTIONS_FN, OPTIONS_FN_COMPRESSION]:
        if "=events1" in extra_args:
            assert "SKIM directory events1" in captured.err
            with uproot.open("tests/test_files/output.EVENTS1.root") as rf:
                keys = getfkeys(rf)
                assert "GetIntegratedLuminosity/LumiTuple" in keys
                assert "events1/DecayTree" in keys
                assert "events2/DecayTree" not in keys
        with uproot.open("tests/test_files/output.EVENTS2.root") as rf:
            keys = getfkeys(rf)
            assert "GetIntegratedLuminosity/LumiTuple" in keys
            assert "events2/DecayTree" in keys
            assert "events1/DecayTree" not in keys

        if "=events2" in extra_args:
            assert "SKIM directory events2" in captured.err

    if "--allow-duplicates" in extra_args:
        with uproot.open("tests/test_files/output.__EVENTS1.root") as rf:
            keys = getfkeys(rf)
            assert "GetIntegratedLuminosity/LumiTuple" in keys
            assert "events2/DecayTree" not in keys
            assert "events1/DecayTree" in keys
        with uproot.open("tests/test_files/output.__EVENTS2.root") as rf:
            keys = getfkeys(rf)
            assert "GetIntegratedLuminosity/LumiTuple" in keys
            assert "events2/DecayTree" in keys
            assert "events1/DecayTree" not in keys
        with uproot.open("tests/test_files/output.__EVENTS22.root") as rf:
            keys = getfkeys(rf)
            assert "GetIntegratedLuminosity/LumiTuple" in keys
            assert "events2/DecayTree" in keys
            assert "events1/DecayTree" not in keys

    if options_spec == OPTIONS_FN_SIMPLE_MERGE_EMPTY_TREES:
        with uproot.open(
            "tests/test_files/example_simple_merge_empty_trees.root"
        ) as rf:
            keys = getfkeys(rf)
            assert "lumiTree" in keys
            assert "events1" not in keys
            assert "events2" not in keys

    if options_spec == OPTIONS_FN_SIMPLE_MERGE_WITH_STREAM:
        with uproot.open("tests/test_files/tuple_merged.stream1.root") as rf:
            keys = getfkeys(rf)
            assert "GetIntegratedLuminosity/LumiTuple" in keys
            assert "events1" in keys
            assert "events2" in keys
            assert rf["events1/DecayTree"].num_entries == 2421 * 2
            assert rf["events2/DecayTree"].num_entries == 2421 * 2
            assert rf["GetIntegratedLuminosity/LumiTuple"].num_entries == 2421 * 2

    if options_spec == OPTIONS_FN_SIMPLE_MERGE_SIMPLER:
        with uproot.open("tests/test_files/tuple_merged_simpler.root") as rf:
            keys = getfkeys(rf)
            assert "GetIntegratedLuminosity/LumiTuple" in keys
            assert "events1" in keys
            assert "events2" in keys
            assert rf["events1/DecayTree"].num_entries == 2421
            assert rf["events2/DecayTree"].num_entries == 2421
            assert rf["GetIntegratedLuminosity/LumiTuple"].num_entries == 2421

    if options_spec == OPTIONS_FN_SIMPLE_MERGE_NO_LUMI_TREE:
        with uproot.open(
            "tests/test_files/example_simple_merge_no_lumi_tree.root"
        ) as rf:
            keys = getfkeys(rf)
            assert len(keys) == 430
            assert (
                np.sum(
                    rf["VPHitEfficiencyMonitorSensor_100/xyResiduals"].counts(flow=True)
                )
                == 157124
            )
            assert (
                np.sum(
                    rf["VPHitEfficiencyMonitorSensor_100/xyResidualsProfile"].counts(
                        flow=True
                    )
                )
                == 157124
            )
            assert (
                np.sum(
                    rf["VPHitEfficiencyMonitorSensor_100/resCorrected"].counts(
                        flow=True
                    )
                )
                == 157124
            )
            assert (
                np.sum(
                    rf["VPHitEfficiencyMonitorSensor_100/hotEfficiencyASIC"].counts(
                        flow=True
                    )
                )
                == 5724
            )
    if options_spec == OPTIONS_FN_SIMPLE_MERGE_NO_LUMI_TREE_MULTI:
        with uproot.open(
            "tests/test_files/example_simple_merge_no_lumi_tree_multi.root"
        ) as rf:
            keys = getfkeys(rf)
            assert len(keys) == 430
            assert (
                np.sum(
                    rf["VPHitEfficiencyMonitorSensor_100/xyResiduals"].counts(flow=True)
                )
                == 157124 * 3
            )
            assert (
                np.sum(
                    rf["VPHitEfficiencyMonitorSensor_100/xyResidualsProfile"].counts(
                        flow=True
                    )
                )
                == 157124 * 3
            )
            assert (
                np.sum(
                    rf["VPHitEfficiencyMonitorSensor_100/resCorrected"].counts(
                        flow=True
                    )
                )
                == 157124 * 3
            )
            assert (
                np.sum(
                    rf["VPHitEfficiencyMonitorSensor_100/hotEfficiencyASIC"].counts(
                        flow=True
                    )
                )
                == 5724 * 3
            )

    if options_spec == OPTIONS_FN_SPLIT_WITH_EMPTY_TREES:
        with uproot.open("tests/test_files/et1_output.EVENTS1.root") as rf:
            keys = getfkeys(rf)
            assert rf["events1/DecayTree"].num_entries == 2421 * 2

        with uproot.open("tests/test_files/et1_output.EVENTS2.root") as rf:
            keys = getfkeys(rf)
            assert rf["events2/DecayTree"].num_entries == 2421 * 3

    if options_spec == OPTIONS_FN_SPLIT_WITH_EMPTY_TREES2:
        with uproot.open("tests/test_files/et2_output.EVENTS1.root") as rf:
            keys = getfkeys(rf)
            assert rf["events1/DecayTree"].num_entries == 2421 * 1
            assert rf["GetIntegratedLuminosity/LumiTuple"].num_entries == 2421 * 2

        with uproot.open("tests/test_files/et2_output.EVENTS2.root") as rf:
            keys = getfkeys(rf)
            assert rf["events2/DecayTree"].num_entries == 2421 * 1
            assert rf["GetIntegratedLuminosity/LumiTuple"].num_entries == 2421 * 2

    if options_spec == OPTIONS_FN_SPLIT_WITH_EMPTY_TREES3:
        with uproot.open("tests/test_files/et3_output.EVENTS1.root") as rf:
            keys = getfkeys(rf)
            assert "GetIntegratedLuminosity/LumiTuple" in keys
            assert "events1" not in keys
            assert "events2" not in keys
            assert rf["GetIntegratedLuminosity/LumiTuple"].num_entries == 2421 * 7

        with uproot.open("tests/test_files/et3_output.EVENTS2.root") as rf:
            keys = getfkeys(rf)
            assert "GetIntegratedLuminosity/LumiTuple" in keys
            assert "events1" not in keys
            assert "events2" not in keys
            assert rf["GetIntegratedLuminosity/LumiTuple"].num_entries == 2421 * 7

    if options_spec == OPTIONS_FN_SPLIT_WITH_EMPTY_TREES4:
        with uproot.open("tests/test_files/et4_output.EVENTS1.root") as rf:
            keys = getfkeys(rf)
            assert rf["events1/DecayTree"].num_entries == 2421 * 1
            assert rf["GetIntegratedLuminosity/LumiTuple"].num_entries == 2421 * 2

        with uproot.open("tests/test_files/et4_output.EVENTS2.root") as rf:
            keys = getfkeys(rf)
            assert rf["events2/DecayTree"].num_entries == 2421 * 1
            assert rf["GetIntegratedLuminosity/LumiTuple"].num_entries == 2421 * 2

    if options_spec == OPTIONS_FN_SPLIT_WITH_EMPTY_TREES5:
        with uproot.open("tests/test_files/et1_output.EVENTS1.root") as rf:
            keys = getfkeys(rf)
            assert rf["events1/DecayTree"].num_entries == 2421 * 2

        with uproot.open("tests/test_files/et1_output.EVENTS2.root") as rf:
            keys = getfkeys(rf)
            assert rf["events2/DecayTree"].num_entries == 2421 * 3


@pytest.mark.parametrize(
    "function_spec,options_spec,extra_args",
    [
        [
            # no missing objects
            "LbExec:skim_and_merge",
            OPTIONS_FN,
            ["--write", "_EVENTS2=events2"],
        ],
        [
            # no duplicates
            "LbExec:skim_and_merge",
            OPTIONS_FN,
            [
                "--write",
                "EVENTS1=events1",
                "--write",
                "EVENTS2=events2",
                "--write",
                "EVENTS22=events2",
            ],
        ],
        [  # nonsense algorithm name
            "LbExec:skim_and_merge",
            OPTIONS_FN_COMPRESSION_BAD,
            [
                "--write",
                "EVENTS1=events1",
                "--write",
                "EVENTS2=events2",
            ],
        ],
    ],
)
def test_invalid_workflow(capfd, monkeypatch, function_spec, options_spec, extra_args):
    monkeypatch.setattr(
        sys, "argv", LBEXEC_CMD + [function_spec, options_spec] + ["--"] + extra_args
    )
    with pytest.raises(SystemExit):
        parse_args()
    captured = capfd.readouterr()

    if "EVENTS22=events2" in extra_args:
        assert "Duplicates of directory" in captured.err

    if "_EVENTS22=events2" in extra_args:
        assert (
            "Some directories of the input files would not be copied to any output files"
            in captured.err
        )

    if OPTIONS_FN_COMPRESSION == options_spec:
        assert "Unknown compression algorithm" in captured.err
