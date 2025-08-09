# cici-tools

<!-- BADGIE TIME -->

[![pipeline status](https://img.shields.io/gitlab/pipeline-status/saferatday0/cici?branch=main)](https://gitlab.com/saferatday0/cici/-/commits/main)
[![coverage report](https://img.shields.io/gitlab/pipeline-coverage/saferatday0/cici?branch=main)](https://gitlab.com/saferatday0/cici/-/commits/main)
[![latest release](https://img.shields.io/gitlab/v/release/saferatday0/cici)](https://gitlab.com/saferatday0/cici/-/releases)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg)](https://github.com/prettier/prettier)

<!-- END BADGIE TIME -->

Power tools for CI/CD.

## Usage

### `bundle`

Flatten `extends` keywords to make zero-dependency GitLab CI/CD files.

```bash
cici bundle
```

```console
$ cici bundle
⚡ python-autoflake.yml
⚡ python-black.yml
⚡ python-build-sdist.yml
⚡ python-build-wheel.yml
⚡ python-import-linter.yml
⚡ python-isort.yml
⚡ python-mypy.yml
⚡ python-pyroma.yml
⚡ python-pytest.yml
⚡ python-setuptools-bdist-wheel.yml
⚡ python-setuptools-sdist.yml
⚡ python-twine-upload.yml
⚡ python-vulture.yml
```

### `readme`

Generate a README for your pipeline project:

```bash
cici readme
```

To customize the output, copy the default README template to `README.md.j2` in
your project root and modify:

```j2
# {{ name }} pipeline

{%- include "brief.md.j2" %}
{%- include "description.md.j2" %}

{%- include "groups.md.j2" %}

{%- include "targets.md.j2" %}

{%- include "variables.md.j2" %}
```

### `update`

Update to the latest GitLab CI/CD `include` versions available.

```bash
cici update
```

```console
$ cici update
updated saferatday0/library/python to 0.5.1
updated saferatday0/library/gitlab from 0.1.0 to 0.2.2
```
