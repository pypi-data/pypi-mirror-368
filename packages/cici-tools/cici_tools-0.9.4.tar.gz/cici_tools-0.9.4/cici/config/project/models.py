# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from typing import Optional

from attrs import define, field


@define(frozen=True, kw_only=True, slots=True)
class PreCommitHookTarget:
    name: str


@define(frozen=True, kw_only=True, slots=True)
class GitLabIncludeTarget:
    name: str


@define(frozen=True, kw_only=True, slots=True)
class Group:
    name: str
    brief: str = ""
    description: str = ""


@define(frozen=True, kw_only=True, slots=True)
class Target:
    name: str
    brief: str = ""
    description: str = ""

    groups: list[str] = field(factory=list)

    precommit_hook: Optional[PreCommitHookTarget] = None
    gitlab_include: Optional[GitLabIncludeTarget] = None


@define(frozen=True, kw_only=True, slots=True)
class VariableExample:
    value: str
    brief: str = ""


@define(frozen=True, kw_only=True, slots=True)
class Variable:
    name: str
    brief: str = ""
    default: str = ""
    description: str = ""
    required: bool = False

    examples: list[VariableExample] = field(factory=list)


@define(kw_only=True, slots=True)
class File:
    name: str

    repo_url: str = ""

    gitlab_project_path: str = ""

    brief: str = ""
    description: str = ""

    groups: list[Group] = field(factory=list)
    targets: list[Target] = field(factory=list)
    variables: dict[str, Variable] = field(factory=dict)
