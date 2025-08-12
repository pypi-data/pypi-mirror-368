#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil -c ./.gitlab-ci.empty.yml --dump && exit 1 || true
gcil -c ./.gitlab-ci.documents.3.yml --dump && exit 1 || true
