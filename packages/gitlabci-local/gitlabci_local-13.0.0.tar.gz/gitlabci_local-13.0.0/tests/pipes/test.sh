#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil -H -p | cat
gcil -p | cat
gcil -p | head -n1
gcil -p | head -n4
gcil --dump | cat
gcil --dump | head -n10
