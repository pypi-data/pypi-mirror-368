# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

ACCESS = "access"
ALWAYS = "always"
DEVELOPMENT = "development"
IF_NOT_PRESENT = "if-not-present"
NEVER = "never"
ON_SUCCESS = "on_success"
ON_FAILURE = "on_failure"
OTHER = "other"
PREPARE = "prepare"
PRODUCTION = "production"
PULL = "pull"
PULL_PUSH = "pull-push"
PUSH = "push"
STAGING = "staging"
START = "start"
STOP = "stop"
TESTING = "testing"
VERIFY = "verify"

CACHE_POLICIES = (PULL, PUSH, PULL_PUSH)

DEPLOYMENT_TIERS = (
    PRODUCTION,
    STAGING,
    TESTING,
    DEVELOPMENT,
    OTHER,
    None,
)

ENVIRONMENT_ACTIONS = (
    START,
    PREPARE,
    STOP,
    VERIFY,
    ACCESS,
)

PULL_POLICIES = (
    ALWAYS,
    IF_NOT_PRESENT,
    NEVER,
)

WHEN_CHOICES = (ON_SUCCESS, ON_FAILURE, ALWAYS)

RETRY_MAX_CHOICES = (0, 1, 2)

UNKNOWN_FAILURE = "unknown_failure"
SCRIPT_FAILURE = "script_failure"
API_FAILURE = "api_failure"
STUCK_OR_TIMEOUT_FAILURE = "stuck_or_timeout_failure"
RUNNER_SYSTEM_FAILURE = "runner_system_failure"
RUNNER_UNSUPPORTED = "runner_unsupported"
STALE_SCHEDULE = "stale_schedule"
JOB_EXECUTION_TIMEOUT = "job_execution_timeout"
ARCHIVED_FAILURE = "archived_failure"
UNMET_PREREQUISITES = "unmet_prerequisites"
SCHEDULER_FAILURE = "scheduler_failure"
DATA_INTEGRITY_FAILURE = "data_integrity_failure"

RETRY_WHEN_CHOICES = (
    ALWAYS,
    UNKNOWN_FAILURE,
    SCRIPT_FAILURE,
    API_FAILURE,
    STUCK_OR_TIMEOUT_FAILURE,
    RUNNER_SYSTEM_FAILURE,
    RUNNER_UNSUPPORTED,
    STALE_SCHEDULE,
    JOB_EXECUTION_TIMEOUT,
    ARCHIVED_FAILURE,
    UNMET_PREREQUISITES,
    SCHEDULER_FAILURE,
    DATA_INTEGRITY_FAILURE,
)

CI_FILE = ".gitlab-ci.yml"
