# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import functools

import cattrs
from cattrs.gen import make_dict_structure_fn, override

from . import models

CONVERTER = cattrs.Converter(omit_if_default=True, forbid_extra_keys=True)


make_dict_struct = functools.partial(
    make_dict_structure_fn,
    _cattrs_forbid_extra_keys=True,
)


def structure_variables(object, __):
    variables = {}
    for key, value in object.items():
        value["name"] = key
        variables[key] = CONVERTER.structure(value, models.Variable)
    return variables


CONVERTER.register_structure_hook(
    models.File,
    make_dict_struct(
        models.File,
        CONVERTER,
        variables=override(struct_hook=structure_variables),
    ),
)
