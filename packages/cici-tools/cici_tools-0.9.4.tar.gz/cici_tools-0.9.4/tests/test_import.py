# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import importlib

import pytest


@pytest.mark.parametrize(
    "module_name",
    [
        "cici.providers.gitlab.serializers",
        "cici.providers.gitlab.converter",
        "cici.providers.gitlab.constants",
        "cici.providers.gitlab.utils",
        "cici.providers.gitlab.models",
        "cici.providers.gitlab",
        "cici.providers",
        "cici.constants",
        "cici.utils",
        "cici",
        "cici.main",
        "cici._version",
        "cici.cli._build",
        "cici.cli.update",
        "cici.cli",
        "cici.cli.bundle",
        "cici.cli.fmt",
        "cici.__main__",
        "cici.config",
        "cici.schema",
    ],
)
def test_import_module(module_name):
    importlib.import_module(module_name)
