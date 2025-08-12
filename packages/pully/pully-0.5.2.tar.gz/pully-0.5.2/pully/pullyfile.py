# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import datetime
from contextlib import contextmanager
from pathlib import Path

import msgspec

from .constants import PULLY_FILE_NAME


class PullyProject(msgspec.Struct, frozen=True):
    project_id: int
    local_path: str
    ssh_url: str
    instance: str = "https://gitlab.com"
    modified: datetime.datetime = msgspec.field(
        default_factory=datetime.datetime.utcnow
    )


class PullyGroup(msgspec.Struct, frozen=True):
    group_id: int
    local_path: str
    instance: str = "https://gitlab.com"
    modified: datetime.datetime = msgspec.field(
        default_factory=datetime.datetime.utcnow
    )


class PullyFile(msgspec.Struct, frozen=True):
    modified: datetime.datetime = msgspec.field(
        default_factory=datetime.datetime.utcnow
    )
    projects: dict[int, PullyProject] = msgspec.field(default_factory=dict)
    groups: dict[int, PullyGroup] = msgspec.field(default_factory=dict)


def dumps(config: PullyFile) -> str:
    return msgspec.json.format(msgspec.json.encode(config))


def dump(config: PullyFile, root_path: Path) -> str:
    with open(root_path / PULLY_FILE_NAME, "wb") as handle:
        handle.write(dumps(config))


def loads(text: str) -> PullyFile:
    return msgspec.json.decode(text, type=PullyFile)


def load(root_path: Path) -> PullyFile:
    try:
        with open(root_path / PULLY_FILE_NAME, "rb") as handle:
            return loads(handle.read())
    except FileNotFoundError:
        return PullyFile()


def find(start_path: Path) -> Path:
    pully_file_path = start_path / PULLY_FILE_NAME
    # print("searching", pully_file_path)
    if not pully_file_path.exists() or not pully_file_path.is_file():
        # filesystem root cannot be reliably determined but can check for loop
        # instead
        if start_path.resolve() == start_path.parent.resolve():
            raise FileNotFoundError(
                f"{PULLY_FILE_NAME} not found in any parent directory"
            )
        return find(start_path=start_path.parent)
    print("found pully file at", pully_file_path)
    return start_path


@contextmanager
def project_context(start_path: Path, search=False):
    if search:
        try:
            config_dir = find(start_path)
        except FileNotFoundError:
            #  if pullyfile does not exist, then create one in start_path
            config_dir = start_path
    else:
        config_dir = start_path

    old_config = load(config_dir)

    projects = {
        project_id: project_obj
        for project_id, project_obj in old_config.projects.items()
    }

    groups = {group_id: group_obj for group_id, group_obj in old_config.groups.items()}

    try:
        yield config_dir, projects, groups

    finally:
        new_config = PullyFile(projects=projects, groups=groups)
        dump(new_config, config_dir)
