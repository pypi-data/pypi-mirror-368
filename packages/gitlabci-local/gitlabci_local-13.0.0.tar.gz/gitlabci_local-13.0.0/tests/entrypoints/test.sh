#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil --pull
gcil -d
gcil -p
gcil -c ./.gitlab-ci.local.yml -p
gcil -c ./.gitlab-ci.name.yml -p
gcil -c ./.gitlab-ci.simple.yml -p
gcil -c ./.gitlab-ci.local.entrypoint.yml -p
