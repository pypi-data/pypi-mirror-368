---
hide:
  - toc
---

# gcil

<!-- markdownlint-disable no-inline-html -->

[![Release](https://img.shields.io/pypi/v/gitlabci-local?color=blue)](https://pypi.org/project/gitlabci-local)
[![Python](https://img.shields.io/pypi/pyversions/gitlabci-local?color=blue)](https://pypi.org/project/gitlabci-local)
[![Downloads](https://img.shields.io/pypi/dm/gitlabci-local?color=blue)](https://pypi.org/project/gitlabci-local)
[![License](https://img.shields.io/gitlab/license/RadianDevCore/tools/gcil?color=blue)](https://gitlab.com/RadianDevCore/tools/gcil/-/blob/main/LICENSE)
<br />
[![Build](https://gitlab.com/RadianDevCore/tools/gcil/badges/main/pipeline.svg)](https://gitlab.com/RadianDevCore/tools/gcil/-/commits/main/)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=RadianDevCore_gcil&metric=bugs)](https://sonarcloud.io/dashboard?id=RadianDevCore_gcil)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=RadianDevCore_gcil&metric=code_smells)](https://sonarcloud.io/dashboard?id=RadianDevCore_gcil)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=RadianDevCore_gcil&metric=coverage)](https://sonarcloud.io/dashboard?id=RadianDevCore_gcil)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=RadianDevCore_gcil&metric=ncloc)](https://sonarcloud.io/dashboard?id=RadianDevCore_gcil)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=RadianDevCore_gcil&metric=alert_status)](https://sonarcloud.io/dashboard?id=RadianDevCore_gcil)
<br />
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Commitizen friendly](https://img.shields.io/badge/commitizen-friendly-brightgreen.svg)](https://commitizen-tools.github.io/commitizen/)
[![gcil](https://img.shields.io/badge/gcil-enabled-brightgreen?logo=gitlab)](https://radiandevcore.gitlab.io/tools/gcil)
[![pre-commit-crocodile](https://img.shields.io/badge/pre--commit--crocodile-enabled-brightgreen?logo=gitlab)](https://radiandevcore.gitlab.io/tools/pre-commit-crocodile)

Launch .gitlab-ci.yml jobs locally, wrapped inside the specific images,  
with inplace project volume mounts and adaptive user selections.

---

## Deprecated features

- Since version `13.0.0`, the following `.local:` configurations are removed:
    - `.local: after`: Deprecated and removed, [documented in issue #292](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/292)
    - `.local: bash`: Deprecated and removed, [documented in issue #292](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/292)
    - `.local: before`: Deprecated and removed, [documented in issue #292](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/292)
    - `.local: configurations`: Deprecated and removed, [documented in issue #292](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/292)
    - `.local: debug`: Deprecated and removed, [documented in issue #292](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/292)
    - `.local: default`: Deprecated and removed, [documented in issue #292](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/292)
    - `.local: display`: Deprecated and removed, [documented in issue #292](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/292)
    - `.local: engine`: Deprecated and removed, [documented in issue #292](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/292)
    - `.local: manual`: Deprecated and removed, [documented in issue #292](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/292)
    - `.local: network`: Deprecated and removed, [documented in issue #292](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/292)
    - `.local: no_console`: Deprecated and removed, [documented in issue #292](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/292)
    - `.local: no_verbose`: Deprecated and removed, [documented in issue #292](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/292)
    - `.local: notify`: Deprecated and removed, [documented in issue #292](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/292)
    - `.local: quiet`: Deprecated and removed, [documented in issue #292](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/292)
    - `.local: random_paths`: Deprecated and removed, [documented in issue #292](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/292)
    - `.local: real_paths`: Deprecated and removed, [documented in issue #292](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/292)
    - `.local: shell`: Deprecated and removed, [documented in issue #292](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/292)
    - `.local: sockets`: Deprecated and removed, [documented in issue #292](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/292)
    - `.local: ssh`: Deprecated and removed, [documented in issue #292](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/292)
    - `.local: workdir`: Deprecated and removed, [documented in issue #292](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/292)

- Since version `12.0.0`, the following `.local:` configurations are deprecated:
    - `.local: after`: Use `CI_LOCAL_AFTER` variable globally or per job, [documented in issue #295](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/295)
    - `.local: bash`: Use `CI_LOCAL_BASH` variable globally or per job, [documented in issue #295](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/295)
    - `.local: before`: Use `CI_LOCAL_BEFORE` variable globally or per job, [documented in issue #295](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/295)
    - `.local: configurations`: Deprecated and pending removal, [documented in issue #292](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/292)
    - `.local: debug`: Use `CI_LOCAL_DEBUG` variable globally or per job, [documented in issue #295](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/295)
    - `.local: default`: Deprecated and pending removal, [documented in issue #292](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/292)
    - `.local: display`: Use `CI_LOCAL_DISPLAY` variable globally or per job, [documented in issue #295](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/295)
    - `.local: engine`: Use `CI_LOCAL_ENGINE` variable globally or per job, [documented in issue #295](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/295)
    - `.local: manual`: Use `CI_LOCAL_MANUAL` variable globally or per job, [documented in issue #295](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/295)
    - `.local: no_console`: Use `CI_LOCAL_NO_CONSOLE` variable globally or per job, [documented in issue #295](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/295)
    - `.local: no_verbose`: Use `CI_LOCAL_NO_VERBOSE` variable globally or per job, [documented in issue #295](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/295)
    - `.local: notify`: Use `CI_LOCAL_NOTIFY` variable globally or per job, [documented in issue #295](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/295)
    - `.local: quiet`: Use `CI_LOCAL_QUIET` variable globally or per job, [documented in issue #295](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/295)
    - `.local: random_paths`: Use `CI_LOCAL_RANDOM_PATHS` variable globally or per job, [documented in issue #295](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/295)
    - `.local: real_paths`: Use `CI_LOCAL_REAL_PATHS` variable globally or per job, [documented in issue #295](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/295)
    - `.local: shell`: Use `CI_LOCAL_SHELL` variable globally or per job, [documented in issue #295](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/295)
    - `.local: sockets`: Use `CI_LOCAL_SOCKETS` variable globally or per job, [documented in issue #295](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/295)
    - `.local: ssh`: Use `CI_LOCAL_SSH` variable globally or per job, [documented in issue #295](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/295)
    - `.local: workdir`: Use `CI_LOCAL_WORKDIR` variable globally or per job, [documented in issue #295](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/295)

- Since version `11.0.0`, the following `.local:` configurations are deprecated:
    - `.local: network`: Use `CI_LOCAL_NETWORK` variable globally or per job, [documented in issue #286](https://gitlab.com/RadianDevCore/tools/gcil/-/issues/286)

- Versions before `10.0.0` were named `gitlabci-local` and not `gcil` yet,  
  the tool's backwards compatibility remains, however settings have changed too,  
  use the `--settings` parameter to see the file and redo your changes

- Versions before `4.6.0` used the now deprecated `PyInquirer` dependency,  
  and due to its own old dependency to the `prompt-toolkit` package,  
  you shoud uninstall both packages first before updating
