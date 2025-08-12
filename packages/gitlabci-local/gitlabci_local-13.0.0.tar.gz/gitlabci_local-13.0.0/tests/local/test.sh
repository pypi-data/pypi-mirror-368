#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Prepare paths
mkdir -p ~/.ssh

# Run tests
gcil
gcil -p
gcil '1' && exit 1 || true
gcil 'Job 1'
gcil --no-before 'Job 1'
gcil --no-after 'Job 1'
gcil -e CI_LOCAL_BEFORE=false 'Job 1'
gcil -e CI_LOCAL_BEFORE=true 'Job 1'
gcil -e CI_LOCAL_AFTER=false 'Job 1'
gcil -e CI_LOCAL_AFTER=true 'Job 1'
gcil 'Job 9'
gcil -p local_first
gcil 'Job 10'
gcil --host 'Job 10'
gcil -e CI_LOCAL_HOST=true 'Job 10'
gcil -c ./.gitlab-ci.unknown.yml -p </dev/null
pexpect-executor -- gcil -c ./.gitlab-ci.unknown.yml -p
gcil -c ./.gitlab-ci.paths.yml -p
gcil -c ./.gitlab-ci.paths.yml --real-paths -p
gcil -c ./.gitlab-ci.paths.yml -e CI_LOCAL_REAL_PATHS=true -p
gcil -c ./.gitlab-ci.paths.yml --random-paths -p
gcil -c ./.gitlab-ci.paths.yml -e CI_LOCAL_RANDOM_PATHS=true -p
gcil -c ./.gitlab-ci.paths.yml --real-paths --random-paths -p
gcil -c ./.gitlab-ci.paths.yml -e CI_LOCAL_REAL_PATHS=true -e CI_LOCAL_RANDOM_PATHS=true -p
