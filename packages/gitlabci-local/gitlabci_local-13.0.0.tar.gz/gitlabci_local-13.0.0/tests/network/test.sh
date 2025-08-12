#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil -p
gcil -n bridge 'Job 2' || (type podman >/dev/null 2>&1 && echo 'Podman engine: Network bridge may fail in GitLab CI containers')
gcil -e CI_LOCAL_NETWORK='bridge' 'Job 2' || (type podman >/dev/null 2>&1 && echo 'Podman engine: Network bridge may fail in GitLab CI containers')
gcil -c ./.gitlab-ci.env.yml -e CI_LOCAL_NETWORK='bridge' 'Job 2' || (type podman >/dev/null 2>&1 && echo 'Podman engine: Network bridge may fail in GitLab CI containers')
gcil -n host 'Job 2'
gcil -c ./.gitlab-ci.env.yml -e CI_LOCAL_NETWORK='host' 'Job 2'
gcil -n none 'Job 2'
gcil -c ./.gitlab-ci.env.yml -e CI_LOCAL_NETWORK='none' 'Job 2'
