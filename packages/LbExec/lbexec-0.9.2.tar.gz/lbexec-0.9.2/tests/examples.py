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
from LbExec import Options

bad_options_data = {
    "data_type": "Upgrade",
    "simulation": True,
    "dddb_tag": "dddb-20210617",
    "conddb_tag": "sim-20210617-vc-md100",
    "output_file": "spruce_passthrough2.dst",
    "output_type": "ROOT",
    "evt_max": 0,
}

options_data = {
    "input_files": [
        "test_files/input1.root",
        "test_files/input2.root",
    ],
    "output_file": "test_files/output.root",
}
options_data_with_stream = {
    "input_files": [
        "test_files/input1.root",
        "test_files/input2.root",
    ],
    "output_file": "test_files/output.{stream}.root",
}


def do_nothing(options: Options):
    # noop
    return options


def bad_function(options: Options):
    raise TypeError("Something is wrong")


def execption_with_chain(options: Options):
    try:
        try:
            raise Exception("Exception 1")
        except Exception:
            raise Exception("Exception 2")
    except Exception:
        raise Exception("Exception 3")


def return_none(options: Options):
    return None


def do_something_2022(options: Options):
    return do_nothing(None)


def do_something_2023(options: Options, *args):
    return do_nothing(None)


def do_something_2024(arg1, arg2):
    return do_nothing(None)


def wrong_args():
    return do_nothing(None)


def no_type_hint(options):
    return do_nothing(options)


def bad_type_hint(options: int):
    return do_nothing(options)
