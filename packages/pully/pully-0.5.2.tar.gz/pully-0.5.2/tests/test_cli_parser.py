# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import pytest

from pully.cli import parser


@pytest.mark.parametrize(
    "argv,funcname,expected",
    (
        (["init"], "init_command", dict()),
        (["add", "-p", "70752539"], "add_command", dict(project_id=[70752539])),
        (
            ["add", "-P", "saferatday0/badgie"],
            "add_command",
            dict(project_path=["saferatday0/badgie"]),
        ),
        (
            ["add", "-p", "70752539", "70752540", "-g", "78192659", "70752539"],
            "add_command",
            dict(project_id=[70752539, 70752540], group_id=[78192659, 70752539]),
        ),
        (
            ["add", "-g", "78192659", "70752539"],
            "add_command",
            dict(group_id=[78192659, 70752539]),
        ),
        (["add", "-G", "saferatday0"], "add_command", dict(group_path=["saferatday0"])),
        (
            ["add", "-G", "saferatday0", "dyff", "-g", "78192659", "70752539"],
            "add_command",
            dict(group_id=[78192659, 70752539], group_path=["saferatday0", "dyff"]),
        ),
        (["pull"], "pull_command", dict()),
        ([], "pull_command", dict()),
    ),
)
def test_parse_args(argv, funcname, expected):
    args = parser.parse_args(argv)
    assert args.func.__name__ == funcname
    for key, value in expected.items():
        assert getattr(args, key) == value
