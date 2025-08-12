#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil --privileged -- privileged
gcil --privileged 'true' privileged
gcil --privileged 'true' unprivileged && exit 1 || true
gcil --privileged 'false' privileged && exit 1 || true
gcil --privileged 'false' unprivileged
gcil --privileged '1' privileged
gcil --privileged '1' unprivileged && exit 1 || true
gcil --privileged 'faulty' privileged && exit 1 || true
gcil --privileged 'faulty' unprivileged
gcil -e CI_LOCAL_PRIVILEGED=true privileged
gcil -e CI_LOCAL_PRIVILEGED=true unprivileged && exit 1 || true
gcil -e CI_LOCAL_PRIVILEGED=false privileged && exit 1 || true
gcil -e CI_LOCAL_PRIVILEGED=false unprivileged
gcil -c ./.gitlab-ci.variables.yml --privileged 'true' privileged
gcil -c ./.gitlab-ci.variables.yml --privileged 'true' unprivileged && exit 1 || true
gcil -c ./.gitlab-ci.variables.yml --privileged 'false' privileged && exit 1 || true
gcil -c ./.gitlab-ci.variables.yml --privileged 'false' unprivileged
