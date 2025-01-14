# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import argparse
import json
import logging

from _telemetry._loggerfactory import _LoggerFactory, track
from azureml.core import Run
from constants import RAIToolType
from rai_component_utilities import (copy_dashboard_info_file,
                                     create_rai_insights_from_port_path,
                                     save_to_output_port)

from responsibleai import RAIInsights

_logger = logging.getLogger(__file__)
_ai_logger = None


def _get_logger():
    global _ai_logger
    if _ai_logger is None:
        _ai_logger = _LoggerFactory.get_logger(__file__)
    return _ai_logger


_get_logger()


def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()

    parser.add_argument("--rai_insights_dashboard", type=str, required=True)
    parser.add_argument("--max_depth", type=int)
    parser.add_argument("--num_leaves", type=int)
    parser.add_argument("--min_child_samples", type=int)
    parser.add_argument("--filter_features", type=json.loads, help="List")
    parser.add_argument("--error_analysis_path", type=str)

    # parse args
    args = parser.parse_args()

    # Patch issue with argument passing
    if isinstance(args.filter_features, list) and len(args.filter_features) == 0:
        args.filter_features = None

    # return args
    return args


@track(_get_logger)
def main(args):
    my_run = Run.get_context()
    # Load the RAI Insights object
    rai_i: RAIInsights = create_rai_insights_from_port_path(
        my_run, args.rai_insights_dashboard
    )

    # Add the error analysis
    rai_i.error_analysis.add(
        max_depth=args.max_depth,
        num_leaves=args.num_leaves,
        min_child_samples=args.min_child_samples,
        filter_features=args.filter_features,
    )
    _logger.info("Added error analysis")

    # Compute
    rai_i.compute()
    _logger.info("Computation complete")

    # Save
    save_to_output_port(rai_i, args.error_analysis_path, RAIToolType.ERROR_ANALYSIS)
    _logger.info("Saved to output port")

    # Copy the dashboard info file
    copy_dashboard_info_file(args.rai_insights_dashboard, args.error_analysis_path)

    _logger.info("Completing")


# run script
if __name__ == "__main__":
    # add space in logs
    print("*" * 60)
    print("\n\n")

    # parse args
    args = parse_args()

    # run main function
    main(args)

    # add space in logs
    print("*" * 60)
    print("\n\n")
