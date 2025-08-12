# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import datetime

from pully.pullyfile import PullyFile, PullyProject, dumps, loads

PULLYFILE1 = """{
  "modified": "2025-07-12T09:11:39.335143",
  "projects": {
    "70326944": {
      "project_id": 70326944,
      "local_path": "saferatday0/library/ansible",
      "ssh_url": "git@gitlab.com:saferatday0/library/ansible.git",
      "instance": "https://gitlab.com",
      "modified": "2025-07-12T09:11:38.396391"
    }
  },
  "groups": {}
}"""


def test_pullyfile_loads():
    pullyfile = loads(PULLYFILE1)
    assert pullyfile.modified == datetime.datetime(2025, 7, 12, 9, 11, 39, 335143)
    assert pullyfile.projects[70326944].project_id == 70326944
    assert (
        pullyfile.projects[70326944].ssh_url
        == "git@gitlab.com:saferatday0/library/ansible.git"
    )
    assert pullyfile.projects[70326944].local_path == "saferatday0/library/ansible"
    assert pullyfile.projects[70326944].instance == "https://gitlab.com"
    assert pullyfile.projects[70326944].modified == datetime.datetime(
        2025, 7, 12, 9, 11, 38, 396391
    )
    assert len(pullyfile.groups) == 0


def test_pullyfile_dumps():
    pullyfile = PullyFile(
        modified=datetime.datetime(2025, 7, 12, 9, 11, 39, 335143),
        projects={
            70326944: PullyProject(
                project_id=70326944,
                ssh_url="git@gitlab.com:saferatday0/library/ansible.git",
                local_path="saferatday0/library/ansible",
                instance="https://gitlab.com",
                modified=datetime.datetime(2025, 7, 12, 9, 11, 38, 396391),
            )
        },
        groups={},
    )
    text = dumps(pullyfile).decode()
    assert PULLYFILE1 == text
