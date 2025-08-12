# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import argparse

from .._version import __version__
from .add_command import add_command
from .init_command import init_command
from .pull_command import pull_command
from .run_command import run_command


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-C",
        "--directory",
        type=str,
        help="directory with pully projects",
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.set_defaults(func=pull_command)

    subparsers = parser.add_subparsers(required=False)

    add_parser = subparsers.add_parser("add")
    add_parser.set_defaults(func=add_command)

    add_parser.add_argument("-g", "--group-id", action="extend", nargs="*", type=int)
    add_parser.add_argument("-G", "--group-path", action="extend", nargs="*", type=str)
    add_parser.add_argument("-p", "--project-id", action="extend", nargs="*", type=int)
    add_parser.add_argument(
        "-P", "--project-path", action="extend", nargs="*", type=str
    )

    init_parser = subparsers.add_parser("init")
    init_parser.set_defaults(func=init_command)

    pull_parser = subparsers.add_parser("pull")
    pull_parser.set_defaults(func=pull_command)

    run_parser = subparsers.add_parser("run")
    run_parser.set_defaults(func=run_command)
    run_parser.add_argument(
        "--output",
        choices=["show", "pully-log", "project-log"],
        default="show",
        help=(
            "What to do with command output. "
            "show to display in terminal, "
            "pully-log to add output to .pully.log, "
            "project-log to add output to .pully.log file in each repo."
        ),
    )

    run_parser.add_argument(
        "command",
        nargs="?",
        help="Command string to execute. If omitted, reads from stdin.",
    )

    return parser


def parse_args(args=None):
    parser = get_parser()
    return parser.parse_args(args=args)
