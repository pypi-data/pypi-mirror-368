#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil -p && exit 1 || true
gcil 'Job 1'
gcil 'Job 2' && exit 1 || true
gcil 'Job 3' && exit 1 || true
gcil 'Job 4'
gcil 'Job 5' && exit 1 || true
gcil 'Job 6' && exit 1 || true
gcil 'Job 7'
gcil 'Job 8'
gcil 'Job 9'
gcil -c ./.gitlab-ci.incomplete.yml -p && exit 1 || true
gcil -c ./.gitlab-ci.shebang.yml 'Job 1'
gcil -c ./.gitlab-ci.shebang.yml -e __GITLAB_CI_LOCAL_SHEBANG_MARKER_BASH__=true 'Job 1' && exit 1 || true
gcil -c ./.gitlab-ci.shebang.yml 'Job 2'
gcil -c ./.gitlab-ci.nested.yml 'Job 1'
gcil -p --scripts
