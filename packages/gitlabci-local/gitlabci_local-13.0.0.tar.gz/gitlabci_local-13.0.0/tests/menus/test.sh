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
pexpect-executor --space --enter gcil
pexpect-executor --press a --enter gcil
pexpect-executor --press a --enter -- gcil -s 'Job 1'
pexpect-executor --down --down --space --enter -- gcil -m
pexpect-executor --space --enter -- gcil -p -s
pexpect-executor --space --enter -- gcil -p -s menus-1
pexpect-executor -- gcil -p -s menus-0
pexpect-executor --up --up --space --enter -- gcil -p -m -l
pexpect-executor --ctrl c -- gcil -p -m -l || true
pexpect-executor --space --enter -- gcil -c ./.gitlab-ci.select.yml -s
FORCE_COLOR=1 pexpect-executor --enter -- gcil -c ./.gitlab-ci.select.yml -l
FORCE_COLOR=0 pexpect-executor --enter -- gcil -c ./.gitlab-ci.select.yml -l
