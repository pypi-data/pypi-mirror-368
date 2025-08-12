#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil -p && exit 1 || true
gcil --display -p || echo 'Display: Support for DISPLAY in CI tests is incomplete...'
gcil -c ./.gitlab-ci.local.yml -p || echo 'Display: Support for DISPLAY in CI tests is incomplete...'
