#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil --notify 'Job 1'
gcil --notify 'Job 2' && exit 1 || true
gcil --notify -p && exit 1 || true
NOTIFY_BINARY_PATH='echo' gcil --notify -p && exit 1 || true
NOTIFY_BINARY_PATH='notify-missing' gcil --notify -p && exit 1 || true
gcil -c ./.gitlab-ci.local.yml 'Job 1'
gcil -c ./.gitlab-ci.local.yml 'Job 2' && exit 1 || true
gcil -c ./.gitlab-ci.local.yml -p && exit 1 || true
gcil -c ./.gitlab-ci.image.yml --pull
timeout 10 timeout -k 8 5 gcil -c ./.gitlab-ci.image.yml --bash --notify 'Job 1' && exit 1 || true
timeout 10 timeout -k 8 5 gcil -c ./.gitlab-ci.image.yml --debug --notify 'Job 1' && exit 1 || true
timeout 5 gcil -c ./.gitlab-ci.image.yml --notify 'Job 2' && exit 1 || true
