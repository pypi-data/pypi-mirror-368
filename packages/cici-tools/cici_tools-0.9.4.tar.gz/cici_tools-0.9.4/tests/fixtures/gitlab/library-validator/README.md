# library-validator component

<!-- BADGIE TIME -->

[![pipeline status](https://img.shields.io/gitlab/pipeline-status/saferatday0/cici?branch=main)](https://gitlab.com/saferatday0/cici/-/commits/main)
[![coverage report](https://img.shields.io/gitlab/pipeline-coverage/saferatday0/cici?branch=main)](https://gitlab.com/saferatday0/cici/-/commits/main)
[![latest release](https://img.shields.io/gitlab/v/release/saferatday0/cici)](https://gitlab.com/saferatday0/cici/-/releases)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg)](https://github.com/prettier/prettier)

<!-- END BADGIE TIME -->

Validate saferatday0 library components.

> Do not use this software unless you are an active collaborator on the
> associated research project.
>
> This project is an output of an ongoing, active research project. It is
> published without warranty, is subject to change at any time, and has not been
> certified, tested, assessed, or otherwise assured of safety by any person or
> organization. Use at your own risk.

## Usage

Use of this component required a token with `read_api` scope on the containing
project. A CI token is not sufficient as the tests include project settings.

```yaml
# .gitlab-ci.yml
include:
  - project: saferatday0/infra/library-validator
    file: library-validator.yml
```

## Targets

| Name                                    | [GitLab include](https://docs.gitlab.com/ee/ci/yaml/includes.html) | [pre-commit hook](https://pre-commit.com/) | Description                              |
| --------------------------------------- | ------------------------------------------------------------------ | ------------------------------------------ | ---------------------------------------- |
| [library-validator](#library-validator) | ✓                                                                  |                                            | Validate saferatday0 library components. |

### `library-validator`

Validate saferatday0 library components.

As a GitLab include:

```yaml
# .gitlab-ci.yml
include:
  - project: saferatday0/infra/library-validator
    file:
      - library-validator.yml
```

## Variables

### `LIBRARY_VALIDATOR_JOB_TOKEN`

_Default:_ `${CI_JOB_TOKEN}`

### `LIBRARY_VALIDATOR_PRIVATE_TOKEN`

## License

Copyright UL Research Institutes.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

<http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
