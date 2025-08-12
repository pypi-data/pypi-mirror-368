#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil -p
gcil -e USER -e VALUE_1=set1 -e VALUE_2=set2 -e VALUE_3=set3 -p
gcil -e FOLDER="$(readlink -f "${PWD}")" -v ./ 'Job 2'
gcil -e environment.env -p
VALUE_5=value_5 gcil -e environment.env -p
gcil -v ./:/opt 'Job 2'
gcil -v ./:/opt -w /opt/ 'Job 2'
gcil --dump | grep -A1 'services' | grep '\$'
gcil --dump -e environment.env | grep -A1 'services' | grep 'docker:dind'
IMAGE_REFERENCE_SERVICE=registry.gitlab.com/radiandevcore/tools/gcil/docker:dind gcil --dump -e environment.env | grep -A1 'services' | grep 'docker:dind'
