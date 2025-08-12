#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Prepare cache
mkdir -p ./cache/
cp -f ./.gitlab-ci.yml ./cache/
cd ./cache/

# Configure tests
set -ex

# Run tests
gcil --no-git-safeties -p && exit 1 || true
gcil -p
