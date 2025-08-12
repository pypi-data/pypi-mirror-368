#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil unknown_job && exit 1 || true
gcil -p unknown_stage && exit 1 || true
gcil -p && exit 1 || true
gcil -p one two
gcil -s -p one two </dev/null
gcil -c ./.gitlab-ci.defaults.yml --dump
gcil -c ./.gitlab-ci.defaults.yml -p
gcil -c ./.gitlab-ci.test.yml -p
gcil -c ./.gitlab-ci.unknown.yml -p && exit 1 || true
gcil -c ./.gitlab-ci.disabled.yml -p
gcil -c ./.gitlab-ci.pre.post.explicit.yml -p
gcil -c ./.gitlab-ci.pre.post.implicit.yml -p
