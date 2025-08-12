#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil -c ./.gitlab-ci.yml --dump | grep 'image: local'
gcil -c ./.gitlab-ci.yml --dump | grep 'services:'
gcil -c ./.gitlab-ci.yml --dump 'Job 1' | grep 'image: local'
gcil -c ./.gitlab-ci.yml --dump -p default | grep 'image: local'
gcil -c ./.gitlab-ci.yml -p
gcil -c ./.gitlab-ci.conflict.after.yml -p && exit 1 || true
gcil -c ./.gitlab-ci.conflict.before.yml -p && exit 1 || true
gcil -c ./.gitlab-ci.conflict.image.yml -p && exit 1 || true
gcil -c ./.gitlab-ci.conflict.services.yml -p && exit 1 || true
