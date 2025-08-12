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
import argparse
import sys

from . import main
from .cli_utils import FunctionLoader, OptionsLoader  # type: ignore


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--export", type=str, default="", required=False)
    parser.add_argument(
        "function",
        type=FunctionLoader,
        help="Function to call with the options that will return the configuration. "
        "Given in the form 'my_module:function_name'.",
    )
    parser.add_argument(
        "options",
        help="YAML data to populate the Application.Options object with. "
        "Multiple files can merged using 'file1.yaml+file2.yaml'.",
    )
    parser.add_argument("extra_args", nargs="*")

    kwargs = vars(parser.parse_args())
    kwargs["options"] = OptionsLoader(kwargs["function"], kwargs["options"])
    return main(**kwargs)


if __name__ == "__main__":
    sys.exit(parse_args())
