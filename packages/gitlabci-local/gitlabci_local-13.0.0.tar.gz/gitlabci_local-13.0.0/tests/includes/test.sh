#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil -c ./.gitlab-ci.default.yml -p
gcil -c ./.gitlab-ci.dict.yml -p
gcil -c ./.gitlab-ci.list.dict.yml -p
gcil -c ./.gitlab-ci.list.str.yml -p
gcil -c ./.gitlab-ci.local.yml -p
gcil -c ./.gitlab-ci.local.empty.yml -p && exit 1 || true
gcil -c ./.gitlab-ci.nested.valid.yml -p
gcil -c ./.gitlab-ci.nested.missing.yml -p && exit 1 || true
gcil -c ./.gitlab-ci.nested.loop.yml -p
gcil -c ./.gitlab-ci.project.yml -p
gcil -c ./.gitlab-ci.project.empty.yml -p && exit 1 || true
gcil -c ./.gitlab-ci.project.missing.yml -p && exit 1 || true
gcil -c ./.gitlab-ci.relative.faulty.yml -p && exit 1 || true
gcil -c ./.gitlab-ci.relative.folder.yml -p
gcil -c ./.gitlab-ci.relative.root.yml -p
gcil -c ./.gitlab-ci.str.yml -p
gcil -c ./.gitlab-ci.variables.yml -p
gcil -c ./.gitlab-ci.wildcards.valid.yml -p
gcil -c ./.gitlab-ci.wildcards.local.missing.yml -p && exit 1 || true
gcil -c ./.gitlab-ci.wildcards.project.missing.yml -p && exit 1 || true
gcil -c ./.gitlab-ci.wildcards.recursive.faulty.yml -p && exit 1 || true
gcil -c ./.gitlab-ci.wildcards.recursive.missing.yml -p && exit 1 || true
gcil -c ./src/ -H -p
