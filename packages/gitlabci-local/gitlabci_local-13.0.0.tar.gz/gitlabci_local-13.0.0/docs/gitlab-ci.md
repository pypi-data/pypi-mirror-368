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

## Supported .gitlab-ci.yml features

```yaml title="Syntax references / .gitlab-ci.yml"
# Global configurations

include: FILE_PATH
include:
  local: FILE_PATH
include:
  - local: FILE_PATH
include:
  - project: PROJECT_URL
    file: FILE_PATH
include:
  - project: PROJECT_URL
    file:
      - FILE_PATH_1
      - FILE_PATH_2

image: IMAGE_NAME
image:
  name: IMAGE_NAME
  entrypoint: ['COMMANDS']

services:
  - ...docker:dind
  - SERVICE_NAME
  - name: SERVICE_NAME
    alias: SERVICE_ALIAS

stages:
  - STAGE_NAMES

variables:
  - VARIABLES: VALUES
  - !reference [.path, to, YAML, node, variables]

# Global scripts

before_script:
  - COMMANDS
  - !reference [.path, to, YAML, node, before_script]

after_script:
  - COMMANDS
  - !reference [.path, to, YAML, node, after_script]

# Templates nodes

.TEMPLATES: &TEMPLATES
  KEYS: VALUES

# Job nodes

JOB_NAME:

  # Job configurations

  stage: STAGE_NAME

  image: IMAGE_NAME
  image:
    name: IMAGE_NAME
    entrypoint: ['COMMANDS']

  services:
    - ...docker:dind
    - SERVICE_NAME
    - name: SERVICE_NAME
      alias: SERVICE_ALIAS

  variables:
    VARIABLES: VALUES
    VARIABLE_PREFILLED:
      value: VALUE
      description: DESCRIPTION
    VARIABLE_REFERENCED: !reference [.path, to, YAML, node, variables, VARIABLE]
  variables: !reference [.path, to, YAML, node, variables]

  # Job templates

  <<: *TEMPLATES
  extends: TEMPLATE
  extends:
    - TEMPLATES

  # Job scripts

  before_script:
    - COMMANDS
    - !reference [.path, to, YAML, node, after_script]

  script:
    - COMMANDS
    - !reference [.path, to, YAML, node, script]

  after_script:
    - COMMANDS
    - !reference [.path, to, YAML, node, after_script]

  # Job executions

  parallel:
    matrix:
      - VARIABLE1: VALUES
        VARIABLE2: VALUES
      - VARIABLE1: VALUES
        VARIABLE3: VALUES

  retry: RETRY_COUNT
  retry:
    max: RETRY_COUNT

  tags:
    - MANUAL_TAGS

  trigger: SIMPLE_TRIGGER (ignored)
  trigger:
    COMPLEX_TRIGGER (ignored)

  when: on_success / manual / on_failure / always

  allow_failure: true / false
```
