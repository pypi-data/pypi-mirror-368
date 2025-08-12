# type: ignore
# pylint: skip-file
###############################################################################
# (c) Copyright 2022-2023 CERN for the benefit of the LHCb Collaboration      #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""Utilities for parsing the positional arguments to ``lbexec``.

This module provides two callable objects that can be used as types with
``argparse``. The majority of the code is for providing hints to the user about
what might be wrong in the case of errors.

``FunctionLoader``
------------------

Wrapper class which takes a function spec of the form ``module.name:callable``.
In the event of errors a best effort is made to advise the user of how to
correct the error. In the event the module to import or function raises an
exception tracebacks are rewritten to hide the implementation details of
``lbexec``.

``OptionsLoader``
------------------

Converts a '+' separated list of YAML file paths into an ``Application.Options``
object. The current application is discovered using the ``GAUDIAPPNAME``
environment variable. If required ``OVERRIDE_LBEXEC_APP`` can be passed to
override which application is loaded. This is used by projects created by
lb-dev where the value of ``GAUDIAPPNAME`` is ``${PROJECT_NAME}Dev``.
"""
import ast
import difflib
import inspect
import os
import re
import shlex
import sys
import traceback
from importlib import import_module
from importlib.machinery import SourceFileLoader
from pathlib import Path
from types import ModuleType
from typing import Callable, Optional, get_type_hints

import click

# with warnings.catch_warnings():
#     warnings.simplefilter("ignore", category=SyntaxWarning)
import pydantic
import yaml

from .options import OptionsBase

# Workaround for https://gitlab.cern.ch/lhcb/LHCb/-/issues/292
# import warnings


class FunctionLoader:
    """Class for parsing the function_spec argument to lbexec"""

    def __init__(self, spec: str):
        self.spec = spec
        try:
            self.module_name, self.func_name = spec.split(":", 1)
        except ValueError:
            _suggest_spec_fix(spec, spec)
            sys.exit(1)

        # Import the module, ensuring sys.path behaves the same way as
        # "python my_script.py" and is always restored to it's original value
        path_backup = sys.path
        try:
            module = self.__load_module()
        except Exception as e:
            if isinstance(e, ModuleNotFoundError) and Path(self.module_name).is_file():
                _suggest_spec_fix(spec, self.module_name, self.func_name)
                sys.exit(1)
            action_msg = f"import {self.module_name!r}"
            _raise_user_exception(e, action_msg, self)
        finally:
            sys.path = path_backup

        # Get the function
        try:
            self._function = getattr(module, self.func_name)
        except AttributeError:
            function_names = _guess_function_names(self.module_name, self.func_name)
            _suggest_module_fix(self.spec, self.module_name, function_names)
            sys.exit(1)

    def __load_module(self) -> ModuleType:
        if self.module_name.endswith(".py"):
            module_path = Path(self.module_name)
            if module_path.is_file():
                self.module_name = module_path.with_suffix("").name
                sys.path = [module_path.parent] + sys.path[1:]
                return SourceFileLoader(
                    self.module_name, str(module_path)
                ).load_module()
            if "/" in self.module_name:
                log_error(
                    f"{self.module_name} looks like a filename but it doesn't exist"
                )
                sys.exit(1)
            log_warn(f"{self.module_name} doesn't exist, assuming it's a Python module")
        sys.path = [os.getcwd()] + sys.path[1:]
        return import_module(self.module_name)

    def __call__(self, options: OptionsBase, *extra_args: list[str]):
        """Run the user provided function and validate the result"""

        try:
            config = self._function(options, *extra_args)
        except Exception as e:
            args = ", ".join(["options"] + [repr(x) for x in extra_args])
            action_msg = "call " + click.style(f"{self.spec}({args})", fg="green")
            _raise_user_exception(e, action_msg, self)

        # if not isinstance(config, ComponentConfig):
        #     log_error(f"{self._function!r} returned {type(config)}, "
        #               f"expected {ComponentConfig}")
        #     sys.exit(1)

        return config

    @property
    def OptionsClass(self) -> type[OptionsBase]:
        """Return the Options class used by the function"""
        valid_types = (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        )
        positional_param_names = [
            n
            for n, p in inspect.signature(self._function).parameters.items()
            if p.kind in valid_types
        ]
        if len(positional_param_names) == 0:
            raise TypeError(
                f"{self.spec} must accept one or more positional argument(s)"
            )
        type_hints = get_type_hints(self._function)
        options_arg = positional_param_names[0]
        if options_arg not in type_hints:
            log_error(f"Failed to find an options type hint for {self.spec}")
            _make_type_hint_suggestion(self._function, options_arg)
            sys.exit(1)
        OptionsClass = type_hints[options_arg]
        if not issubclass(OptionsClass, OptionsBase):
            log_error(f"OptionsClass for {self.spec} should inherit from OptionsBase")
            sys.exit(1)
        return OptionsClass


def OptionsLoader(function: FunctionLoader, options_spec: str) -> OptionsBase:
    """Convert a '+' separated list of paths to an Application.Options object."""
    if options_spec.endswith((".yaml", ".yml", ".json")):
        # Load and merge the various input YAML files
        options = {}
        for options_yaml in map(Path, re.split(r"(?<!\\)\+", options_spec)):
            if not options_yaml.is_file():
                log_error(f"{options_yaml} does not exist")
                sys.exit(1)
            options_data = yaml.safe_load(options_yaml.read_text())
            if not isinstance(options_data, dict):
                log_error(
                    f"{options_yaml} should contain a mapping but got {options_data!r}"
                )
                sys.exit(1)
            options.update(options_data)
    elif ":" in options_spec:
        if options_spec.startswith(":"):
            options_spec = function.spec.split(":", 1)[0] + options_spec
        # HACK: Abuse the FunctionLoader class to load the options
        options = FunctionLoader(options_spec)._function
        if not isinstance(options, dict):
            log_error(f"{options_spec} should point to a mapping but got {options!r}")
            sys.exit(1)
    else:
        raise NotImplementedError(f"Unrecognised {options_spec!r}")

    # Parse the merged YAML
    try:
        return function.OptionsClass.parse_obj(options)
    except pydantic.ValidationError as e:
        errors = e.errors()
        log_error(f"Failed to validate options! Found {len(errors)} errors:")
        for error in errors:
            extra_msg = ""
            if error["type"].startswith("extra") and len(error["loc"]) == 1:
                suggestions = difflib.get_close_matches(
                    error["loc"][0], function.OptionsClass.schema()["properties"], n=1
                )
                if suggestions:
                    extra_msg = click.style(
                        f"Did you mean {suggestions[0]!r}?", fg="green"
                    )
            locs = ", ".join(map(repr, error["loc"]))
            if locs == "'__root__'":
                click.echo(f" * {error['msg']}", err=True)
            else:
                click.echo(
                    f" * {click.style(error['msg'], fg='red')}: {locs} {extra_msg}",
                    err=True,
                )
        sys.exit(1)


def log_info(message):
    click.echo(click.style("INFO: ", fg="green") + message, err=True)


def log_warn(message):
    click.echo(click.style("WARN: ", fg="yellow") + message, err=True)


def log_error(message):
    click.echo(click.style("ERROR: ", fg="red") + message, err=True)


def _make_type_hint_suggestion(function: Callable, options_arg: str) -> str:
    # Try to guess what the application name should be
    app_name = os.environ.get("GAUDIAPPNAME", "GenericPython")
    if app_name == "GenericPython":
        app_name = "LbExec"

    original = inspect.getsource(function).split("\n")[0]
    # Try to guess how the Python code should look
    sig = inspect.signature(function)
    parameter_fixed = sig.parameters[options_arg].replace(annotation="to-be-replaced!")
    sig_fixed = sig.replace(
        parameters=[parameter_fixed] + list(sig.parameters.values())[1:]
    )
    fixed = original.replace(
        str(sig), str(sig_fixed).replace("'to-be-replaced!'", "Options")
    )
    # If the code is unchanged something went wrong
    if fixed == original:
        log_error("Failed to generate corrected Python code")
    else:
        log_error("*** You probably need to replace:")
        log_error(original)
        log_error("*** with:")
        log_error(f"from {app_name} import Options")
        log_error("")
        log_error(fixed)
        source_file = inspect.getsourcefile(function)
        _, lineno = inspect.getsourcelines(function)
        log_error(f"*** in {source_file}:{lineno}")


def _suggest_spec_fix(spec, module_name: str, func_name: Optional[str] = None):
    if os.path.isfile(module_name):
        filename = Path(module_name).absolute().relative_to(Path.cwd())
        module_name = str(filename.with_suffix("")).replace(os.sep, ".")
        if module_name.endswith(".__init__"):
            module_name = module_name[: -len(".__init__")]
        # If given, assume the user's function name is correct
        func_names = [func_name] if func_name else _guess_function_names(module_name)
    else:
        func_names = _guess_function_names(module_name)
    _suggest_module_fix(spec, module_name, func_names)


def _guess_function_names(
    module_name: str, function_name: Optional[str] = None
) -> list[str]:
    module_path = _guess_module_path(module_name)
    if not module_path:
        return []
    module_ast = ast.parse(module_path.read_text())
    functions = [
        node
        for node in ast.iter_child_nodes(module_ast)
        if isinstance(node, ast.FunctionDef)
    ]
    function_names = [
        function.name
        for function in functions
        if function.args.args and function.args.args[0].arg == "options"
    ]
    if function_name:
        function_names = difflib.get_close_matches(
            function_name, function_names, cutoff=0
        )
    return function_names


def _suggest_module_fix(spec: str, module_name: str, function_names: list[str]):
    log_error("There seems to be an issue with your function specification.")
    if function_names:
        click.echo("Did you mean one of these:\n", err=True)
        for maybe_function in function_names:
            argv = [Path(sys.argv[0]).name] + sys.argv[1:]
            original = shlex.join(argv)
            argv[sys.argv.index(spec)] = f"{module_name}:{maybe_function}"
            corrected = shlex.join(argv)
            _print_diff(original, corrected)
            click.echo(err=True)
    elif spec[-4:] == ".qmt":
        log_error(
            "Is it possible you are trying to run a .qmt test? If so, use qmtexec."
        )
    else:
        log_error("Failed to find a suggested fix")


def _print_diff(original: str, corrected: str):
    s = difflib.SequenceMatcher(None, original, corrected)
    s1 = s2 = ""
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        fg1 = fg2 = None
        if tag in ["replace", "delete"]:
            fg1 = "red"
        if tag in ["replace", "insert"]:
            fg2 = "green"
        s1 += click.style(s.a[i1:i2], fg=fg1)
        s2 += click.style(s.b[j1:j2], fg=fg2)
    click.echo(click.style(" Original: ", fg="red") + s1, err=True)
    click.echo(click.style("Corrected: ", fg="green") + s2, err=True)


def _raise_user_exception(e, action_msg, spec):
    module_path = str(_guess_module_path(spec.module_name))

    # Make a new trace back with everything above module_path removed
    total_frames = 0
    to_ignore = None
    for frame, _ in traceback.walk_tb(sys.exc_info()[2]):
        if to_ignore is None and frame.f_code.co_filename == module_path:
            to_ignore = total_frames
        total_frames += 1
    limit = to_ignore - total_frames if to_ignore else None
    traceback.print_exception(*sys.exc_info(), limit=limit)

    log_error(f"Failed to {action_msg}, see above for more information.")
    sys.exit(1)


def _guess_module_path(name: str) -> Optional[Path]:
    """Static implementation of ``importlib.util.find_spec``

    When calling ``find_spec("foo.bar")`` Python will execute ``foo/__init__.py``.
    This is required for correctness however when showing help messages we should
    avoid running any extra code so this function attempts to guess the path to
    the module's source.
    """
    from importlib.machinery import SourceFileLoader
    from importlib.util import find_spec

    top_module, *child_modules = name.split(".")

    sys.path.insert(0, os.getcwd())
    try:
        module_spec = find_spec(top_module)
    finally:
        sys.path.pop(0)

    if not (module_spec and child_modules):
        if isinstance(getattr(module_spec, "loader", None), SourceFileLoader):
            return Path(module_spec.loader.get_filename())
        return None

    if not module_spec.submodule_search_locations:
        return None
    module_path = Path(module_spec.submodule_search_locations[0])

    for name in child_modules:
        module_path = module_path / name
    if module_path.is_dir():
        module_path = module_path / "__init__.py"
    else:
        module_path = module_path.parent / f"{module_path.name}.py"

    return module_path if module_path.is_file() else None
