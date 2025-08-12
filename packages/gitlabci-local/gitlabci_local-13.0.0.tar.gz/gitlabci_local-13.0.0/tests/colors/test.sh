#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil -H -p
gcil -H -p --no-color
gcil --set themes no_color 1
gcil -H -p
gcil --set themes no_color 0
gcil -H -p
gcil --set themes no_color UNSET
gcil -H -p
FORCE_COLOR=1 gcil -H -p
FORCE_COLOR=0 gcil -H -p
NO_COLOR=1 gcil -H -p
