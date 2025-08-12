#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil -p
gcil -H -p
gcil 'Job 2' && exit 1 || true
gcil -e CI_VARIABLE_DIR=. 'Job 2'
CI_VARIABLE_DIR=. gcil 'Job 2' && exit 1 || true
CI_VARIABLE_DIR=. gcil -e CI_VARIABLE_DIR 'Job 2'
gcil 'Job 3'
gcil 'Job 4'
gcil -e CI_CONSTANT_PRE_DIR=. -e CI_CONSTANT_POST_DIR=. 'Job 3'
gcil -c ./.gitlab-ci.overrides.yml -e GREP='test\.sh' -p
gcil -c ./.gitlab-ci.overrides.yml -e GREP='test\.sh' -e CI_PROJECT_DIR='/unknown' -p && exit 1 || true
gcil -c ./.gitlab-ci.overrides.yml -e GREP='test\.sh' -e CI_PROJECT_DIR='${CI_PROJECT_DIR}/first' -p && exit 1 || true
gcil -c ./.gitlab-ci.overrides.yml -e GREP='data\.raw' -e CI_PROJECT_DIR='${CI_PROJECT_DIR}/first' -p
gcil -c ./.gitlab-ci.overrides.yml -e GREP='data\.raw' -e CI_PROJECT_DIR='${CI_PROJECT_DIR}/second' -p
