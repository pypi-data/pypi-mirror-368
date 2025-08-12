#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Drop validation environment
unset PYTHON_VERSION

# Run tests
gcil 'Job 1'
gcil -e PYTHON_VERSION=3.8 'Job 1'
gcil -e PYTHON_VERSION=0.0 'Job 1' && exit 1 || true
PYTHON_VERSION=3.8 gcil 'Job 1'
PYTHON_VERSION=0.0 gcil 'Job 1' && exit 1 || true
gcil -H 'Job 2'
gcil -H -e VALUE1= 'Job 2' && exit 1 || true
gcil -H -e VALUE1=3 'Job 2'
gcil -H -e VALUE1=4 'Job 2' && exit 1 || true
gcil -H -e VALUE2= 'Job 2' && exit 1 || true
gcil -H -e VALUE2=2 'Job 2'
gcil -H -e VALUE2=3 'Job 2' && exit 1 || true
gcil -H 'Job 2: [3.8, 1, 1]'
gcil -H -e VALUE2=2 'Job 2: [3.8, 1, 1]' && exit 1 || true
gcil -H 'Job 2: [3.8, 1, 2]'
gcil -H 'Job 2: [3.8, 1, 3]' && exit 1 || true
gcil 'Job 3'
gcil -H 'Job 4'
gcil -H 'Job 4 0/10' && exit 1 || true
gcil -H 'Job 4 10/10'
