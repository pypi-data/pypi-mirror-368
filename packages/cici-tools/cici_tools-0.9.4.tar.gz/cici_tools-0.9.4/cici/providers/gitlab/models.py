# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Optional, Union

import attrs
from attrs import define, field

from .constants import (
    ALWAYS,
    CACHE_POLICIES,
    DEPLOYMENT_TIERS,
    ENVIRONMENT_ACTIONS,
    ON_SUCCESS,
    PULL_PUSH,
    RETRY_MAX_CHOICES,
    START,
    WHEN_CHOICES,
)


@define(frozen=True, kw_only=True, slots=True)
class AllowFailure:
    exit_codes: Union[int, list[int]] = field(factory=list)


@define(frozen=True, kw_only=True, slots=True)
class CoverageReport:
    coverage_format: str
    path: str


@define(frozen=True, kw_only=True, slots=True)
class ArtifactReports:
    coverage_report: Optional[CoverageReport] = None
    junit: Union[str, list[str]] = field(factory=list)
    terraform: str = ""
    container_scanning: str = ""


@define(frozen=True, kw_only=True, slots=True)
class Artifacts:
    name: str = ""
    exclude: list[str] = field(factory=list)
    expire_in: str = ""
    expose_as: str = ""
    public: bool = True
    paths: list[str] = field(factory=list)
    reports: Optional[ArtifactReports] = None
    untracked: bool = False
    when: str = field(validator=attrs.validators.in_(WHEN_CHOICES), default=ON_SUCCESS)


@define(frozen=True, kw_only=True, slots=True)
class CacheKey:
    files: list[str] = field(factory=list)
    prefix: str = ""


@define(frozen=True, kw_only=True, slots=True)
class Cache:
    key: Union[str, CacheKey] = ""
    paths: list[str] = field(factory=list)
    untracked: bool = False
    unprotect: bool = False
    when: str = field(validator=attrs.validators.in_(WHEN_CHOICES), default=ON_SUCCESS)
    policy: str = field(
        validator=attrs.validators.in_(CACHE_POLICIES), default=PULL_PUSH
    )
    fallback_keys: list[str] = field(factory=list)


@define(frozen=True, kw_only=True, slots=True)
class EnvironmentKubernetes:
    namespace: str = ""


@define(frozen=True, kw_only=True, slots=True)
class Environment:
    name: str
    url: str = ""
    on_stop: str = ""
    action: str = field(
        validator=attrs.validators.in_(ENVIRONMENT_ACTIONS), default=START
    )
    auto_stop_in: str = ""
    kubernetes: Optional[EnvironmentKubernetes] = None
    deployment_tier: Optional[str] = field(
        validator=attrs.validators.in_(DEPLOYMENT_TIERS), default=None
    )


@define(frozen=True, kw_only=True, slots=True)
class Hooks:
    pre_get_sources_script: Union[str, list[Union[str, list[str]]]] = field(
        factory=list
    )


@define(frozen=True, kw_only=True, slots=True)
class IDToken:
    aud: Union[str, list[str]] = field(factory=list)


@define(frozen=True, kw_only=True, slots=True)
class Image:
    name: str
    entrypoint: Union[str, list[str]] = field(factory=list)
    pull_policy: Union[str, list[str]] = field(factory=list)


@define(frozen=True, kw_only=True, slots=True)
class IncludeLocal:
    local: str


@define(frozen=True, kw_only=True, slots=True)
class IncludeProject:
    project: str
    ref: Optional[str] = None
    file: Union[str, list[str]] = field(factory=list)


@define(frozen=True, kw_only=True, slots=True)
class IncludeRemote:
    remote: str


@define(frozen=True, kw_only=True, slots=True)
class IncludeTemplate:
    template: str


@define(frozen=True, kw_only=True, slots=True)
class RuleChanges:
    compare_to: str
    paths = list[str]


@define(frozen=True, kw_only=True, slots=True)
class Rule:
    if_: str = ""
    when: str = ""
    changes: Union[list[str], RuleChanges] = field(factory=list)
    exists: list[str] = field(factory=list)
    allow_failure: bool = False
    needs: Optional[Union[list[str], dict[str, str]]] = None
    variables: dict[str, str] = field(factory=dict)


@define(frozen=True, kw_only=True, slots=True)
class Retry:
    max: int = field(validator=attrs.validators.in_(RETRY_MAX_CHOICES), default=0)
    when: Union[str, list[str]] = ALWAYS


@define(frozen=True, kw_only=True, slots=True)
class Variable:
    description: Optional[str] = None
    value: Optional[str] = None
    options: Optional[list[str]] = None
    expand: bool = True


@define(frozen=True, kw_only=True, slots=True)
class Service:
    name: str
    entrypoint: Optional[Union[str, list[str]]] = None
    command: Optional[Union[str, list[str]]] = None
    variables: dict[str, Union[str, Variable]] = field(factory=dict)
    alias: Optional[str] = None
    pull_policy: Union[str, list[str]] = field(factory=list)


@define(frozen=True, kw_only=True, slots=True)
class Job:
    extends: Union[str, list[str]] = []
    stage: Optional[str] = None
    image: Optional[Union[str, Image]] = None
    services: list[Union[str, Service]] = field(factory=list)
    variables: dict[str, Union[str, Variable]] = field(factory=dict)
    before_script: Union[str, list[Union[str, list[str]]]] = field(factory=list)
    script: Union[str, list[Union[str, list[str]]]] = field(factory=list)
    after_script: Union[str, list[Union[str, list[str]]]] = field(factory=list)
    allow_failure: Union[bool, AllowFailure] = False
    artifacts: Optional[Artifacts] = None
    coverage: str = ""
    cache: Optional[Cache] = None
    dependencies: list[str] = field(factory=list)
    environment: Union[str, Environment] = ""
    hooks: Optional[Hooks] = None
    id_tokens: dict[str, IDToken] = field(factory=list)
    interruptible: bool = False
    needs: Optional[list[str]] = None
    retry: Union[int, Retry] = 0
    resource_group: str = ""
    rules: list[Rule] = field(factory=list)
    tags: list[str] = field(factory=list)


@define(frozen=True, kw_only=True, slots=True)
class Workflow:
    name: str = ""
    rules: list[Rule] = field(factory=list)


@define(frozen=True, kw_only=True, slots=True)
class Default:
    after_script: Union[str, list[Union[str, list[str]]]] = field(factory=list)
    artifacts: Optional[Artifacts] = None
    before_script: Union[str, list[Union[str, list[str]]]] = field(factory=list)
    cache: Optional[Cache] = None
    hooks: Optional[Hooks] = None
    image: Optional[Union[str, Image]] = None
    interruptible: bool = False
    retry: Union[int, Retry] = 0
    tags: list[str] = field(factory=list)


@define(kw_only=True, slots=True)
class File:
    jobs: dict[str, Job] = field(factory=dict)
    stages: list[str] = field(factory=list)
    include: Union[
        str, list[Union[IncludeLocal, IncludeProject, IncludeRemote, IncludeTemplate]]
    ] = field(factory=list)
    workflow: Optional[Workflow] = None
    variables: dict[str, Union[str, Variable]] = field(factory=dict)
    extras: dict[str, Any] = field(factory=dict)
