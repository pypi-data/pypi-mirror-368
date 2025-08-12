#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil -p && exit 1 || true
gcil 'Job 1' 'Job 2'
gcil -H -p && exit 1 || true
gcil -H 'Job 1' 'Job 2'
PYTHONIOENCODING=ascii gcil -H -p && exit 1 || true
PYTHONIOENCODING=ascii gcil -H 'Job 1' 'Job 2'
