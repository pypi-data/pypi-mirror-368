#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil -p
if [ "${OSTYPE}" = 'msys' ] || [ "${OSTYPE}" = 'win32' ]; then
  gcil -v ../../tests/volumes://opt/src:ro -p
  gcil -v ../../tests/volumes://opt/src:ro -v ../../tests/volumes://opt/src:ro -p
  gcil -v ../../tests/local://opt/src:ro -p
  gcil -v ../../tests/volumes://opt/src3:ro -p
  gcil -v ../../tests/local://opt/src:ro -v ../../tests/volumes://opt/src:ro -p && exit 1 || true
  gcil -w //opt/src -p
  gcil -w //opt/unknown -p
else
  gcil -v ../../tests/volumes:/opt/src:ro -p
  gcil -v ../../tests/volumes:/opt/src:ro -v ../../tests/volumes:/opt/src:ro -p
  gcil -v ../../tests/local:/opt/src:ro -p
  gcil -v ../../tests/volumes:/opt/src3:ro -p
  gcil -v ../../tests/local:/opt/src:ro -v ../../tests/volumes:/opt/src:ro -p && exit 1 || true
  gcil -w /opt/src -p
  gcil -w /opt/unknown -p || (type podman >/dev/null 2>&1 && echo 'Podman engine: CLI workdir is not created automatically as expected')
fi
gcil -w . -p
gcil -r -w . -p
gcil -w ../../tests/volumes/ -p || (type podman >/dev/null 2>&1 && echo 'Podman engine: CLI workdir is not created automatically as expected')
gcil -r -w ../../tests/volumes/ -p
gcil -w . -p
gcil -r -w . -p
gcil 'Job 2'
gcil -w . 'Job 2'
gcil -r 'Job 2'
gcil -r -w . 'Job 2'
if [ "${OSTYPE}" = 'msys' ] || [ "${OSTYPE}" = 'win32' ]; then
  gcil -c ./.gitlab-ci.windows.yml -p || true
else
  gcil -c ./.gitlab-ci.relative.yml -p
  gcil -c ./.gitlab-ci.variables.yml -p
fi
gcil -c ./.gitlab-ci.empty.yml -p && exit 1 || true
