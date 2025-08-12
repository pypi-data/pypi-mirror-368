#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
timeout 10 timeout -k 5 2 gcil --bash 'Job 1' </dev/null && exit 1 || true
timeout 10 timeout -k 5 2 gcil --bash 'Job 1' </dev/null && exit 1 || true
timeout 10 timeout -k 5 2 gcil --bash --no-console 'Job 1' && exit 1 || true
timeout 25 timeout -k 20 18 pexpect-executor --wait 2 --press exit --enter -- gcil --bash 'Job 1' && exit 1 || true
timeout 25 timeout -k 20 18 pexpect-executor -- timeout 3 gcil --bash --no-console 'Job 1' && exit 1 || true
timeout 10 timeout -k 5 2 gcil --bash 'Job 2' </dev/null && exit 1 || true
timeout --preserve-status 10 timeout --preserve-status -k 5 2 gcil --debug 'Job 1' </dev/null || {
  result=${?}
  test "${result}" -eq 143
}
timeout --preserve-status 10 timeout --preserve-status -k 5 2 gcil --debug 'Job 2' </dev/null && exit 1 || true
