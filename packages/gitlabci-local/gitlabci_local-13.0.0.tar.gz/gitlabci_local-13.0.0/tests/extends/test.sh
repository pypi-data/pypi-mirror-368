#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Prepare aliases
alias pexpect-executor='pexpect-executor --delay-init 0.2 --delay-press 0.2 --delay-prompt 0.2'

# Configure tests
set -ex

# Run tests
gcil -H -p
gcil -c ./.gitlab-ci.incomplete.yml -H 'Job 1'
gcil -c ./.gitlab-ci.incomplete.yml -H 'Job 2'
gcil -c ./.gitlab-ci.incomplete.yml -H 'Job 3' && exit 1 || true
gcil -c ./.gitlab-ci.incomplete.yml -e CI_LOCAL_EXTENDS_INCOMPLETE='1' -H 'Job 3'
gcil -c ./.gitlab-ci.incomplete.yml -e CI_LOCAL_EXTENDS_INCOMPLETE='true' -H 'Job 3'
gcil -c ./.gitlab-ci.incomplete.yml -e CI_LOCAL_EXTENDS_INCOMPLETE='True' -H 'Job 3'
gcil -c ./.gitlab-ci.incomplete.yml -e CI_LOCAL_EXTENDS_INCOMPLETE='0' -H 'Job 3' && exit 1 || true
gcil -c ./.gitlab-ci.incomplete.yml -e CI_LOCAL_EXTENDS_INCOMPLETE='false' -H 'Job 3' && exit 1 || true
gcil -c ./.gitlab-ci.incomplete.yml -H 'Job 4'
FORCE_COLOR=1 pexpect-executor --enter -- gcil -c ./.gitlab-ci.missing.yml -H
gcil -c ./.gitlab-ci.partial.yml -H -p
gcil -c ./.gitlab-ci.partial.yml -H 'Job 3' && exit 1 || true
gcil -c ./.gitlab-ci.partial.yml -H 'Job 4' && exit 1 || true
gcil -c ./.gitlab-ci.stages.yml -H -p
