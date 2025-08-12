#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil -p && exit 1 || true
gcil -e IMAGE_REFERENCE_1='local' -p && exit 1 || true
gcil -e IMAGE_REFERENCE_1='local' -e IMAGE_REFERENCE_5='local' -p
IMAGE_REFERENCE_1='local' IMAGE_REFERENCE_5='local' gcil -p
gcil -c ./.gitlab-ci.nested.yml -p
gcil -c ./.gitlab-ci.image.yml -p
gcil -c ./.gitlab-ci.images.yml -p
gcil -c ./.gitlab-ci.tags.yml --dump | grep -A1 'tags' | grep '\$' && exit 1 || true
gcil -c ./.gitlab-ci.tags.yml --dump | grep -A1 'tags' | grep 'docker'
