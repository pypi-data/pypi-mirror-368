#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Prepare environment
export CI_LOCAL_ENGINE=''

# Run tests
gcil -p
gcil -n none -p
DOCKER_HOST=tcp://0.0.0.0:9999 gcil -E d -p && exit 1 || true
gcil -E auto -p
gcil -e CI_LOCAL_ENGINE='auto' -p
CI_LOCAL_ENGINE=docker,podman,auto gcil -p
gcil -e CI_LOCAL_ENGINE=docker,podman,auto -p
gcil -E '' -p
gcil -e CI_LOCAL_ENGINE='' -p
gcil --set engines engine 'docker,podman,auto' && gcil -p
gcil --set engines engine 'UNSET' && gcil -p
PODMAN_BINARY_PATH=podman-missing gcil -E podman -p && exit 1 || true
PODMAN_BINARY_PATH=ls gcil -E podman -p && exit 1 || true
gcil -c .gitlab-ci.hybrid.yml -p
