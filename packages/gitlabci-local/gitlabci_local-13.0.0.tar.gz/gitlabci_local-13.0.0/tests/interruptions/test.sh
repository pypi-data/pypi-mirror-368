#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
timeout 10 timeout -k 8 -s SIGINT 5 gcil 'Job 2' && exit 1 || true
timeout 10 timeout -k 8 -s SIGINT 5 gcil -H 'Job 2' && exit 1 || true
timeout 12 timeout -k 10 -s SIGINT 6 gcil -p && exit 1 || true
