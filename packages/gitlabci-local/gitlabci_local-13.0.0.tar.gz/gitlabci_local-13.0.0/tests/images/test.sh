#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil --pull
gcil --pull
gcil --pull 'Job 4'
gcil --pull 'Job 3' && exit 1 || true
gcil --pull -p containers
gcil --pull -p native  && exit 1 || true
gcil --pull --force
pexpect-executor -- gcil --pull --force
gcil --rmi
gcil --rmi
gcil -p
gcil -c ./.gitlab-ci.default.yml --dump
CI_LOCAL_IMAGE_DEFAULT=registry.gitlab.com/radiandevcore/tools/gcil/ruby:3.1 gcil -c ./.gitlab-ci.default.yml --pull
CI_LOCAL_IMAGE_DEFAULT=registry.gitlab.com/radiandevcore/tools/gcil/ruby:3.1 gcil -c ./.gitlab-ci.default.yml -p
CI_LOCAL_IMAGE_DEFAULT=registry.gitlab.com/radiandevcore/tools/gcil/ruby:3.1 gcil -c ./.gitlab-ci.extends.yml -p
