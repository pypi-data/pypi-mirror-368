#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil -p
gcil -m -p && exit 1 || true
gcil -t upload -p && exit 1 || true
gcil -t publish -p
gcil -t deploy,publish -p
gcil -t deploy,local,publish -p
gcil 'Job 3'
gcil -p three && exit 1 || true
gcil -m -p three
