# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import os
from pathlib import Path

from appdirs import user_cache_dir, user_config_dir  # type: ignore
from decouple import Config, RepositoryIni  # type: ignore

CONFIG_FILE = Path(
    os.environ.get(
        "CICI_CONFIG_FILE", Path(user_config_dir("cici-tools")) / "config.ini"
    )
)

if not CONFIG_FILE.exists():
    CONFIG_FILE.parent.mkdir(exist_ok=True, parents=True)
    CONFIG_FILE.touch()

_config = Config(RepositoryIni(CONFIG_FILE))

CACHE_DIR = _config("CICI_CACHE_DIR", cast=Path, default=user_cache_dir("cici-tools"))

CACHE_TIMEOUT = _config("CICI_CACHE_TIMEOUT", cast=int, default=43200)

GITLAB_URL = _config("CICI_GITLAB_URL", default="https://gitlab.com")

GITLAB_PRIVATE_TOKEN = _config("CICI_GITLAB_PRIVATE_TOKEN", default="")
