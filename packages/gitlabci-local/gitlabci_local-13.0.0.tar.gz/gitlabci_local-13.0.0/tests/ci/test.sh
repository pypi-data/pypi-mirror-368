#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil -c ./.gitlab-ci.env.yml -p
gcil -c ./.gitlab-ci.git.yml -p
unset CI_COMMIT_REF_NAME CI_COMMIT_REF_SLUG CI_COMMIT_SHA CI_COMMIT_SHORT_SHA
gcil -c ./.gitlab-ci.env.yml -p
gcil -c ./.gitlab-ci.git.yml -p
gcil -c ./.gitlab-ci.git.yml -e CI_COMMIT_REF_NAME=develop -e CI_COMMIT_REF_SLUG=develop -e CI_DEFAULT_BRANCH='develop' -p
gcil -c ./.gitlab-ci.git.yml -e CI_COMMIT_SHA=abcd1234efgh5678 -e CI_COMMIT_SHORT_SHA=abcd1234 -p
gcil -c ./.gitlab-ci.git.yml -e CI_COMMIT_REF_NAME="$(tr -dc '[:graph:]' </dev/urandom 2>/dev/null | dd bs=1 count=128 2>/dev/null)" -p
GIT_BINARY_PATH=git-missing gcil -c ./.gitlab-ci.raw.yml -p
gcil -c ./.gitlab-ci.variables.yml -p
