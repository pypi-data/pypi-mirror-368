# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from typing import Any, Optional, Union

import ruamel.yaml

from . import models as cici_config
from .converter import CONVERTER


def loads(
    text: str,
    gitlab_ci_jobs: Optional[dict[str, Any]] = None,
    precommit_hooks: Optional[dict[str, Any]] = None,
) -> cici_config.File:
    if gitlab_ci_jobs is None:
        gitlab_ci_jobs = {}
    if precommit_hooks is None:
        precommit_hooks = {}
    yaml = ruamel.yaml.YAML(typ="safe")
    data = yaml.load(text)
    data.setdefault("targets", [])
    for target in data["targets"]:
        if target["name"] in precommit_hooks:
            target["precommit_hook"] = {"name": target["name"]}
        if target["name"] in gitlab_ci_jobs:
            target["gitlab_include"] = {"name": target["name"]}
    return CONVERTER.structure(data, cici_config.File)


def load(
    file: Union[str, Path],
    gitlab_ci_jobs: Optional[dict[str, Any]] = None,
    precommit_hooks: Optional[dict[str, Any]] = None,
) -> cici_config.File:
    return loads(
        open(file).read(),
        gitlab_ci_jobs=gitlab_ci_jobs,
        precommit_hooks=precommit_hooks,
    )
