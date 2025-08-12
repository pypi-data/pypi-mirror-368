#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil -h
gcil -c unknown/.gitlab-ci.yml && exit 1 || true
gcil -c ../../examples/ -d
gcil -c ../../examples/.gitlab-ci.yml -d
gcil -c ../../examples/.gitlab-ci.yml -d 'Job 1 - 1'
gcil -c ../../examples/.gitlab-ci.yml -d -i 'job 1 - 1'
gcil -c ../../examples/.gitlab-ci.yml --no-verbose 'Job 1 - 1'
gcil -c ../../examples/.gitlab-ci.yml -e CI_LOCAL_NO_VERBOSE=true 'Job 1 - 1'
gcil -c ../../examples/.gitlab-ci.yml --quiet 'Job 1 - 1'
gcil -c ../../examples/.gitlab-ci.yml -e CI_LOCAL_QUIET=true 'Job 1 - 1'
gcil -c ../../examples/.gitlab-ci.yml --no-verbose --quiet 'Job 1 - 1'
gcil -c ../../examples/.gitlab-ci.yml -e CI_LOCAL_NO_VERBOSE=true -e CI_LOCAL_QUIET=true 'Job 1 - 1'
