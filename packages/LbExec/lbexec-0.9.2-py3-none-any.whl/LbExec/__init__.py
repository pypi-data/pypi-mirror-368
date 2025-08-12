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
__all__ = (
    "Options",
    "main",
    "skim_and_merge",
    "process_trees",
    "utils",
    "OptionsBase",
    "DataOptions",
    "SimulationOptions",
)

import sys

from . import utils
from .options import DataOptions, Options, OptionsBase, SimulationOptions
from .workflows import process_trees, skim_and_merge


def main(function, options, extra_args, export=""):  # pylint: disable=unused-argument
    """Run a job with lbexec.

    Args:
        function (callable): A callable that will return the Gaudi configuration
        options (Options): An initialised APP.Options object
        extra_args (list of str): list of strings to add the the call to ``function``

    Returns:
        return_code (int): The Gaudi process's return code
    """
    _ = function(options, *extra_args)

    # Ensure that any printout that has been made by the user provided function
    # has been flushed. Without this, non-interactive jobs such as tests end up
    # showing the print out in the middle of the Gaudi application log
    sys.stdout.flush()
    sys.stderr.flush()

    return 0
