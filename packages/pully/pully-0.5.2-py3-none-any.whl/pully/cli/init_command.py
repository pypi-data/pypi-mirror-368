# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import os.path
from pathlib import Path

from .. import pullyfile
from ..constants import BASE_DIR, PULLY_FILE_NAME
from ..pullyfile import PullyFile


def init_command(args):
    base_dir = Path(args.directory) if args.directory else BASE_DIR
    base_dir.mkdir(exist_ok=True, parents=True)
    full_path = os.path.join(base_dir, PULLY_FILE_NAME)
    if os.path.exists(full_path):
        print("pully file already exists")
        exit(1)
    print("creating empty pully workspace at", base_dir)
    new_config = PullyFile()
    pullyfile.dump(new_config, base_dir)
