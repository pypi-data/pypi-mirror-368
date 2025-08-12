#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil -p
gcil 'C'
gcil 'C++'
gcil 'Test'
gcil 'C*'
gcil 'C.*'
gcil 'est .*'
gcil 'test *' && exit 1 || true
gcil -i 'test *'
