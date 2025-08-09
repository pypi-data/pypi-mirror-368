# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()

COMMAND_DIR = BASE_DIR / "cli"

SCHEMA_DIR = BASE_DIR / "schema"

TEMPLATE_DIR = BASE_DIR / "templates"

README_TEMPLATE_FILE = TEMPLATE_DIR / "README.md.j2"

COMMANDS = sorted(
    [path.stem for path in COMMAND_DIR.glob("*.py") if not path.stem.startswith("_")]
)

PROVIDER_DIR = BASE_DIR / "providers"

PROVIDERS = sorted(
    [path.stem for path in PROVIDER_DIR.glob("*.py") if not path.stem.startswith("_")]
    + [
        path.stem
        for path in PROVIDER_DIR.glob("*/")
        if path.is_dir() and not path.stem.startswith("_")
    ]
)

DEFAULT_PROVIDER = PROVIDERS[0]

WORKING_DIR = Path.cwd()

# this really should be based on the git project directory rather than the
# working directory but this works for now
PROJECT_DIR = WORKING_DIR

CONFIG_DIR_NAME = ".cici"

CICI_DIR = PROJECT_DIR / CONFIG_DIR_NAME

CICI_FILE = CICI_DIR / "config.yaml"
