#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
CI_LOCAL_HISTORIES_DURATION_FAKE=0 gcil -p
CI_LOCAL_HISTORIES_DURATION_FAKE=10 gcil -p
CI_LOCAL_HISTORIES_DURATION_FAKE=62 gcil -p
