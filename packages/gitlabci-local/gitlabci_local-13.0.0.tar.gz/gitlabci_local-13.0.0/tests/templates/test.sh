#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil 'Job 1' 'Job 2' 'Job 3'
gcil -B -A 'Job 1' 'Job 2' 'Job 3'
gcil -c ./.gitlab-ci.partial.yml -p
gcil --settings | grep '^no_script_fail = '
gcil --no-script-fail -c ./.gitlab-ci.partial.yml -p && exit 1 || true
pexpect-executor --space --down --space --enter -- gcil -c ./.gitlab-ci.partial.yml
gcil -c ./.gitlab-ci.stages.yml -p template_stage_1
gcil -c ./.gitlab-ci.stages.yml -p template_stage_2
gcil -c ./.gitlab-ci.stages.yml -p template_stage_4
