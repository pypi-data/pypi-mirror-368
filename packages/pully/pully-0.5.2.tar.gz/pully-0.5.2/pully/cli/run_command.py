# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import subprocess
import sys
from pathlib import Path

from termcolor import colored

from .. import pullyfile
from ..constants import BASE_DIR, PULLY_LOG
from ..pullyfile import PullyProject


def run_commands(commands, repo_dir, stdout, stderr):
    for command in commands:
        subprocess.run(
            command,
            cwd=repo_dir,
            text=True,
            check=True,
            shell=True,
            stdout=stdout,
            stderr=stderr,
        )


def run_commands_in_project(
    config_dir: Path, project: PullyProject, log_path: Path, commands
):
    repo_dir = config_dir / project.local_path
    if not repo_dir.exists():
        print(
            colored("skipping", "yellow"),
            f"{repo_dir} not found, run pull to clone project",
        )
        return
    try:
        if log_path:
            with open(log_path, "a") as output_stream:
                output_stream.write(f"--------- {project.local_path} ---------\n")
                output_stream.flush()
                run_commands(commands, repo_dir, output_stream, subprocess.STDOUT)
                output_stream.write(f"-----------------------------------\n")
        else:
            print(f"--------- {project.local_path} ---------")
            run_commands(commands, repo_dir, None, None)
            print("-----------------------------------")
    except subprocess.CalledProcessError:
        print(
            colored("failed", "red"),
            project.local_path,
        )


def run_command(args):
    base_dir = Path(args.directory) if args.directory else BASE_DIR

    if args.command:
        commands = [args.command]
    else:
        commands = [command.strip() for command in sys.stdin]

    try:
        with pullyfile.project_context(base_dir, search=not args.directory) as context:
            config_dir, projects, groups = context
            if args.output == "pully-log":
                log_path = config_dir / PULLY_LOG
            else:
                log_path = None
            for project_id, project in projects.items():
                if args.output == "project-log":
                    log_path = config_dir / project.local_path / PULLY_LOG
                run_commands_in_project(config_dir, project, log_path, commands)
    except FileNotFoundError:
        print(f"No pullyfile found for {base_dir}")
