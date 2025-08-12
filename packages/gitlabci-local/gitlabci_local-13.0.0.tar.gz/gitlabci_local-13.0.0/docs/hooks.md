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

[TOC]

<span class="page-break"></span>

## Using gcil hooks

```yaml title="Sources / .pre-commit-config.yaml"
# pre-commit configurations
default_install_hook_types:
  - pre-commit
  - pre-push
default_stages:
  - pre-commit
  - pre-push
minimum_pre_commit_version: 3.8.0

# gcil repositories
repos:

  # Repository: gcil
  - repo: https://gitlab.com/RadianDevCore/tools/gcil
    rev: X.Y.Z # Adapt to latest release tag
    hooks:
      - id: ...
```

---

## `run-gcil-commit`

**Run GitLab CI job with gcil upon commit and push :**

- <!-- -->
  ```yaml title="Sources / .pre-commit-config.yaml"
    # Repository: gcil
    - repo: ...
      ...
      hooks:
        - id: run-gcil-commit
          name: Run GitLab CI job with gcil (adapt:job:name:1)
          description: Automatically run GitLab CI job with gcil (adapt:job:name:1)
          args:
            - 'adapt:job:name:1'
        - id: run-gcil-commit
          name: Run GitLab CI job with gcil (adapt:job:name:2)
          description: Automatically run GitLab CI job with gcil (adapt:job:name:2)
          args:
            - 'adapt:job:name:2'
  ```

---

<span class="page-break"></span>

## `run-gcil-push`

**Run GitLab CI job with gcil upon push only :**

- <!-- -->
  ```yaml title="Sources / .pre-commit-config.yaml"
    # Repository: gcil
    - repo: ...
      ...
      hooks:
        - id: run-gcil-push
          name: Run GitLab CI job with gcil (adapt:job:name:1)
          description: Automatically run GitLab CI job with gcil (adapt:job:name:1)
          args:
            - 'adapt:job:name:1'
        - id: run-gcil-push
          name: Run GitLab CI job with gcil (adapt:job:name:2)
          description: Automatically run GitLab CI job with gcil (adapt:job:name:2)
          args:
            - 'adapt:job:name:2'
  ```
