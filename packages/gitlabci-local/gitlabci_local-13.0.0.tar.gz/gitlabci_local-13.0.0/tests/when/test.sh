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
FORCE_COLOR=1 pexpect-executor --enter -- gcil -c ./.gitlab-ci.manual.yml -l
FORCE_COLOR=1 pexpect-executor --enter -- gcil -c ./.gitlab-ci.manual.yml -s
FORCE_COLOR=1 pexpect-executor --enter -- gcil -c ./.gitlab-ci.manual.yml
gcil -c .gitlab-ci.manual.yml -p && exit 1 || true
gcil -c .gitlab-ci.manual.yml -m -p
gcil -c .gitlab-ci.manual.yml -e CI_LOCAL_MANUAL=true -p
gcil -c .gitlab-ci.manual.yml 'Job 1'
