###############################################################################
# (c) Copyright 2022 CERN for the benefit of the LHCb Collaboration           #
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

import pytest
import yaml

import examples
from LbExec import Options as DefaultOptions
from LbExec.__main__ import parse_args
from LbExec.cli_utils import FunctionLoader, OptionsLoader

LBEXEC_CMD = ["lbexec"]
OPTIONS_FN = str(Path(__file__).parent / "example.yaml")
FUNCTION_SPEC = f"{examples.__name__}:do_nothing"
LBEXEC_EXAMPLE_CMD = LBEXEC_CMD + [FUNCTION_SPEC, OPTIONS_FN]


@pytest.fixture
def fake_options():
    options = DefaultOptions(**examples.options_data)
    return options


@pytest.mark.parametrize(
    "depth,module,valid,invalid",
    [
        # Invalid module names
        [0, "examples.py", ["examples:do_nothing"], ["examples:wrong_args"]],
        [0, "example2/__init__.py", ["example2:do_nothing"], ["example2:wrong_args"]],
        [
            1,
            "tests/examples.py",
            ["tests.examples:do_nothing"],
            ["tests.examples:wrong_args"],
        ],
        [
            1,
            "tests.examples",
            ["tests.examples:do_nothing"],
            ["tests.examples:wrong_args"],
        ],
        [0, "broken", [], []],
        # This test ensures that broken.__init__ isn't executed when we only
        # intend to statically analyse the sources
        [
            0,
            "broken/examples.py",
            ["broken.examples:something"],
            ["broken.examples:wrong_args"],
        ],
        # Invalid function name
        [
            0,
            "examples:do_something",
            ["examples:do_something_2022", "examples:do_something_2023"],
            ["examples:do_something_2024"],
        ],
    ],
)
def test_invalid_function(capsys, monkeypatch, depth, module, valid, invalid):
    monkeypatch.chdir(Path(examples.__file__).parent)
    for _ in range(depth):
        monkeypatch.chdir("..")
    monkeypatch.setattr(sys, "argv", LBEXEC_CMD + [module, OPTIONS_FN])

    with pytest.raises(SystemExit):
        FunctionLoader(module)

    captured = capsys.readouterr()
    assert captured.out == ""
    if valid:
        assert "Did you mean" in captured.err
        for suggestion in valid:
            assert suggestion in captured.err
    else:
        assert "Failed to find a suggested fix" in captured.err
    for suggestion in invalid:
        assert suggestion not in captured.err


def test_import_exception(capsys, monkeypatch):
    monkeypatch.chdir(Path(examples.__file__).parent)
    monkeypatch.setattr(sys, "argv", LBEXEC_CMD + ["broken:something", OPTIONS_FN])
    with pytest.raises(SystemExit):
        FunctionLoader("broken:something")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Traceback (most recent call last):" in captured.err
    assert "tests/broken/__init__.py" in captured.err
    assert "This module is broken" in captured.err
    assert len(captured.err.split("\n")) < 10, "The traceback failed to truncate!"


def test_function_exception(capsys, fake_options):
    function_spec = FunctionLoader(f"{examples.__name__}:bad_function")
    with pytest.raises(SystemExit):
        function_spec(fake_options)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Traceback (most recent call last):" in captured.err
    assert ", in bad_function" in captured.err
    assert "TypeError: Something is wrong" in captured.err
    assert len(captured.err.split("\n")) < 10, "The traceback failed to truncate!"


def test_function_exception_chain(capsys, fake_options):
    function_spec = FunctionLoader(f"{examples.__name__}:execption_with_chain")
    with pytest.raises(SystemExit):
        function_spec(fake_options)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "During handling of the above exception" in captured.err
    assert 'raise Exception("Exception 1")' in captured.err
    assert 'raise Exception("Exception 2")' in captured.err
    assert 'raise Exception("Exception 3")' in captured.err
    assert len(captured.err.split("\n")) < 25, "The traceback failed to truncate!"


# def test_invalid_return_type(capsys, fake_options):
#     function_spec = FunctionLoader(f"{examples.__name__}:return_none")
#     with pytest.raises(SystemExit):
#         function_spec(fake_options)
#     captured = capsys.readouterr()
#     assert captured.out == ""
#     assert "NoneType" in captured.err
#     assert " expected " in captured.err
#     print (captured.err)
#     assert "PyConf.application.ComponentConfig" in captured.err


def test_valid_return_type(capsys, fake_options):
    function_spec = FunctionLoader(f"{examples.__name__}:do_nothing")
    config = function_spec(fake_options)
    assert isinstance(config, DefaultOptions)
    captured = capsys.readouterr()
    assert captured.out == ""


@pytest.mark.parametrize(
    "gaudi_app_name,expected_app_name",
    [
        # ("DaVinci", "DaVinci"),
        # ("Moore", "Moore"),
        ("", "LbExec"),
    ],
)
def test_no_type_hint(capsys, monkeypatch, gaudi_app_name, expected_app_name):
    if gaudi_app_name != "":
        monkeypatch.setenv("GAUDIAPPNAME", gaudi_app_name)
    with pytest.raises(SystemExit):
        OptionsLoader(FunctionLoader(f"{examples.__name__}:no_type_hint"), OPTIONS_FN)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "You probably need to replace" in captured.err
    assert "def no_type_hint(options):" in captured.err
    assert f"from {expected_app_name} import Options" in captured.err
    assert "def no_type_hint(options: Options):" in captured.err


def test_no_type_hint_unknown_app(capsys, monkeypatch):
    # monkeypatch.delenv("GAUDIAPPNAME")
    with pytest.raises(SystemExit):
        OptionsLoader(FunctionLoader(f"{examples.__name__}:no_type_hint"), OPTIONS_FN)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "You probably need to replace" in captured.err
    assert "def no_type_hint(options):" in captured.err
    assert "def no_type_hint(options: Options):" in captured.err


def test_bad_type_hint(capsys):
    with pytest.raises(SystemExit):
        OptionsLoader(FunctionLoader(f"{examples.__name__}:bad_type_hint"), OPTIONS_FN)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "should inherit from OptionsBase" in captured.err


@pytest.mark.parametrize(
    "options_arg", [f"{OPTIONS_FN}+i-am-missing.yaml", "i-am-missing.yaml"]
)
def test_options_file_not_found(capsys, options_arg):
    with pytest.raises(SystemExit):
        OptionsLoader(FunctionLoader(FUNCTION_SPEC), options_arg)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "i-am-missing.yaml does not exist" in captured.err


def test_options_invalid(capsys, tmp_path):
    reference_options = yaml.safe_load(Path(OPTIONS_FN).read_text())
    options1 = {}
    options2 = {}
    key_corrections = {}
    for i, (k, v) in enumerate(reference_options.items()):
        if i % 2 == 0:
            options1[k] = v
        else:
            bad_key = f"{k[:-3]}{-2}{-3}{k[-1]}"
            key_corrections[bad_key] = k
            options2[bad_key] = v
    options1_fn = tmp_path / "options1.yaml"
    options1_fn.write_text(yaml.safe_dump(options1))
    options2_fn = tmp_path / "options2.yaml"
    options2_fn.write_text(yaml.safe_dump(options2))

    with pytest.raises(SystemExit):
        OptionsLoader(FunctionLoader(FUNCTION_SPEC), f"{options1_fn}+{options2_fn}")

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Failed to validate options!" in captured.err
    for bad_key, good_key in key_corrections.items():
        assert f"'{bad_key}' Did you mean '{good_key}'?" in captured.err


# def test_dry_run(capsys, monkeypatch):
#     monkeypatch.setattr(sys, "argv", LBEXEC_EXAMPLE_CMD + ["--dry-run"])

#     exit_code = parse_args()
#     captured = capsys.readouterr()
#     assert exit_code == 0, captured
#     assert captured.out == ""
#     assert "this is a dry-run" in captured.err


# def test_dry_run_with_output_unknown(capsys, monkeypatch, tmp_path):
#     output = tmp_path / "name.cpp"
#     output.unlink(missing_ok=True)

#     monkeypatch.setattr(
#         sys, "argv",
#         LBEXEC_EXAMPLE_CMD + ["--dry-run", "--export",
#                               str(output)])

#     with pytest.raises(
#             NotImplementedError, match=r"Unrecognised format '.cpp'"):
#         parse_args()
#     captured = capsys.readouterr()
#     assert captured.out == ""
#     assert not output.exists()


# @pytest.mark.parametrize(
#     "name",
#     ["-", "output.json", "ouput.yaml", "ouput.yaml", "ouput.opts"],
# )
# def test_dry_run_with_output(capsys, monkeypatch, tmp_path, name):
#     monkeypatch.chdir(tmp_path)
#     monkeypatch.setattr(sys, "argv",
#                         LBEXEC_EXAMPLE_CMD + ["--dry-run", "--export", name])

#     exit_code = parse_args()
#     captured = capsys.readouterr()
#     assert exit_code == 0, captured
#     if name == "-":
#         ouput_text = captured.out
#     else:
#         assert captured.out == ""
#         ouput_text = (tmp_path / name).read_text()
#     assert "ApplicationMgr.EvtMax" in ouput_text
#     assert "this is a dry-run" in captured.err


# FIXME Currently only one Gaudi.Application object can be used per process so
# we have to disable all but one of these tests. Will be fixed by:
# https://gitlab.cern.ch/gaudi/Gaudi/-/merge_requests/1368/
@pytest.mark.parametrize(
    "function_spec,options_spec",
    [
        [f"{examples.__name__}:do_nothing", OPTIONS_FN],
        [f"tests/examples.py:do_nothing", OPTIONS_FN],
        # [f"{examples.__file__}:do_nothing", OPTIONS_FN],
        # [f"{examples.__name__}:do_nothing", f"{examples.__name__}:options_data"],
        # [f"{examples.__file__}:do_nothing", f"{examples.__file__}:options_data"],
        # [f"{examples.__name__}:do_nothing", ":options_data"],
        # [f"{examples.__file__}:do_nothing", ":options_data"],
    ],
)
def test_valid(capfd, monkeypatch, function_spec, options_spec):
    monkeypatch.setattr(sys, "argv", LBEXEC_CMD + [function_spec, options_spec])

    parse_args()
    captured = capfd.readouterr()

    # assert WELCOME_MSG in captured.out
    # assert "Application Manager Terminated successfully" in captured.out
    assert captured.err == ""
