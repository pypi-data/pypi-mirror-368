#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil --dump
gcil -p
gcil -c ./.gitlab-ci.str.yml --dump
gcil -c ./.gitlab-ci.str.yml -p
gcil -c ./.gitlab-ci.nested.yml --dump
gcil -c ./.gitlab-ci.nested.yml -p
