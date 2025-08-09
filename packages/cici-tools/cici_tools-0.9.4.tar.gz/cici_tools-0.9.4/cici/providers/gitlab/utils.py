# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import functools
import json
import typing

import jsonschema

from ...constants import SCHEMA_DIR


@functools.cache
def load_schema() -> typing.Any:
    schema_file = SCHEMA_DIR / "gitlab-ci.json"
    return json.load(open(schema_file))


def validate(data: typing.Any):
    schema = load_schema()
    jsonschema.validate(data, schema=schema)


def get_reserved_words():
    return {key for key in load_schema()["properties"].keys() if key not in ("pages",)}


def get_job_names(data):
    return {key for key in data.keys() if key not in get_reserved_words()}
