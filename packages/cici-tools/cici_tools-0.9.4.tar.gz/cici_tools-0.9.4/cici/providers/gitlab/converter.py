# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import functools
from typing import Union

import cattrs
from cattrs.gen import make_dict_structure_fn, make_dict_unstructure_fn, override

from ...utils import (
    make_multiline_string,
    make_quoted_dict,
    make_quoted_list,
    make_quoted_list_or_string,
    make_quoted_string,
    make_scalar_list,
)
from . import models

CONVERTER = cattrs.Converter(omit_if_default=True, forbid_extra_keys=True)


make_dict_struct = functools.partial(
    make_dict_structure_fn,
    _cattrs_forbid_extra_keys=True,
)

make_dict_unstruct = functools.partial(
    make_dict_unstructure_fn,
    _cattrs_omit_if_default=True,
)


def quoted_list_struct_hook(object, __):
    return make_quoted_list(object)


def quoted_string_struct_hook(object, __):
    return make_quoted_string(object)


def multiline_string_struct_hook(object, __):
    return make_multiline_string(object)


def quoted_list_or_string_struct_hook(object, __):
    return make_quoted_list_or_string(object)


def quoted_dict_struct_hook(object, __):
    return make_quoted_dict(object)


def structure_image(object, __):
    if object is None:
        return None
    elif isinstance(object, str):
        return make_quoted_string(CONVERTER.structure(object, str))
    return CONVERTER.structure(object, models.Image)


def structure_include(object, __):
    if isinstance(object, str):
        return CONVERTER.structure(object, str)
    items = []
    for item in object:
        if "local" in item:
            items.append(CONVERTER.structure(item, models.IncludeLocal))
        elif "project" in item:
            items.append(CONVERTER.structure(item, models.IncludeProject))
        elif "remote" in item:
            items.append(CONVERTER.structure(item, models.IncludeRemote))
        elif "template" in item:
            items.append(CONVERTER.structure(item, models.IncludeTemplate))
    return items


def structure_script(object, __):
    if isinstance(object, str):
        return CONVERTER.structure(object, str)
    items = []
    for item in object:
        if isinstance(item, str):
            items.append(CONVERTER.structure(item, str))
        else:
            for entry in item:
                items.append(CONVERTER.structure(entry, str))
    return make_scalar_list(items)


def structure_service(object, __):
    if isinstance(object, str):
        return make_quoted_string(CONVERTER.structure(object, str))
    return CONVERTER.structure(object, models.Service)


def structure_variables(object, __):
    variables = {}
    for key, value in object.items():
        if isinstance(value, str):
            variables[key] = make_quoted_string(value)
        else:
            variables[key] = CONVERTER.structure(value, models.Variable)
    return variables


CONVERTER.register_structure_hook(
    Union[
        str,
        list[
            Union[
                models.IncludeLocal,
                models.IncludeProject,
                models.IncludeRemote,
                models.IncludeTemplate,
            ]
        ],
    ],
    structure_include,
)


CONVERTER.register_structure_hook(
    Union[str, list[str]], quoted_list_or_string_struct_hook
)

CONVERTER.register_structure_hook(
    Union[str, models.Service],
    lambda object, _: CONVERTER.structure(
        object, str if isinstance(object, str) else models.Service
    ),
)

CONVERTER.register_structure_hook(
    Union[str, models.CacheKey],
    lambda object, _: CONVERTER.structure(
        object, str if isinstance(object, str) else models.CacheKey
    ),
)

CONVERTER.register_structure_hook(
    Union[str, models.Environment],
    lambda object, _: CONVERTER.structure(
        object, str if isinstance(object, str) else models.Environment
    ),
)

CONVERTER.register_structure_hook(
    Union[int, models.Retry],
    lambda object, _: CONVERTER.structure(
        object, int if isinstance(object, int) else models.Retry
    ),
)

CONVERTER.register_structure_hook(
    Union[str, list[Union[str, list[str]]]],
    structure_script,
)

CONVERTER.register_structure_hook(
    models.Image,
    make_dict_struct(
        models.Image,
        CONVERTER,
        name=override(struct_hook=quoted_string_struct_hook),
        entrypoint=override(struct_hook=quoted_list_or_string_struct_hook),
    ),
)

CONVERTER.register_structure_hook(
    models.Service,
    make_dict_struct(
        models.Service,
        CONVERTER,
        name=override(struct_hook=quoted_string_struct_hook),
        command=override(struct_hook=quoted_list_or_string_struct_hook),
        entrypoint=override(struct_hook=quoted_list_or_string_struct_hook),
    ),
)

CONVERTER.register_structure_hook(
    models.Variable,
    make_dict_struct(
        models.Variable,
        CONVERTER,
        description=override(struct_hook=multiline_string_struct_hook),
        value=override(struct_hook=quoted_string_struct_hook),
        options=override(struct_hook=quoted_list_struct_hook),
    ),
)


def unstructure_script(cls):
    object = CONVERTER.unstructure(cls, str if isinstance(cls, str) else list[str])
    if isinstance(object, str):
        return object  # make_quoted_scalar_string(object)
    return make_scalar_list(object)


CONVERTER.register_unstructure_hook(
    Union[str, list[str]],
    unstructure_script,
)

CONVERTER.register_structure_hook(
    Union[str, models.Image, None],
    structure_image,
)

CONVERTER.register_structure_hook(
    models.Rule,
    make_dict_struct(
        models.Rule,
        CONVERTER,
        if_=override(rename="if"),
    ),
)
CONVERTER.register_unstructure_hook(
    models.Rule,
    make_dict_unstruct(
        models.Rule,
        CONVERTER,
        if_=override(rename="if"),
    ),
)


CONVERTER.register_structure_hook(
    models.Job,
    make_dict_struct(
        models.Job,
        CONVERTER,
        variables=override(struct_hook=structure_variables),
    ),
)

CONVERTER.register_structure_hook(
    models.File,
    make_dict_struct(
        models.File,
        CONVERTER,
        variables=override(struct_hook=structure_variables),
    ),
)
