#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Configure environment
(
  # Configure versions
  export DEBUG_UPDATES_DISABLE=''
  export DEBUG_VERSION_FAKE='2.0.0'

  # Run tests
  gcil --version
  gcil --update-check
  DEBUG_UPDATES_DISABLE=true gcil --update-check
  FORCE_COLOR=1 gcil --update-check
  NO_COLOR=1 gcil --update-check
  FORCE_COLOR=1 PYTHONIOENCODING=ascii gcil --update-check
  FORCE_COLOR=1 COLUMNS=40 gcil --update-check
  FORCE_COLOR=1 DEBUG_UPDATES_OFFLINE='' gcil --update-check
  FORCE_COLOR=1 DEBUG_UPDATES_OFFLINE=true gcil --update-check
  FORCE_COLOR=1 DEBUG_UPDATES_OFFLINE=true DEBUG_VERSION_FAKE=0.0.2 DEBUG_UPDATES_FAKE=0.0.1 gcil --update-check
  FORCE_COLOR=1 DEBUG_UPDATES_OFFLINE=true DEBUG_VERSION_FAKE=0.0.2 DEBUG_UPDATES_FAKE=0.0.2 gcil --update-check
  FORCE_COLOR=1 DEBUG_UPDATES_OFFLINE=true DEBUG_VERSION_FAKE=0.0.2 DEBUG_UPDATES_FAKE=0.0.3 gcil --update-check
  if [ "${OSTYPE}" = 'msys' ] || [ "${OSTYPE}" = 'win32' ]; then
    echo 'INFO: Test "versions" has some ignored tests as it is not supported on this host'
  elif type wine >/dev/null 2>&1 && wine python --version >/dev/null 2>&1; then
    echo 'INFO: Test "versions" has some ignored tests as it is not supported in this Wine Python environment'
  else
    FORCE_COLOR=1 DEBUG_UPDATES_DAILY=true DEBUG_VERSION_FAKE=0.0.2 DEBUG_UPDATES_FAKE=0.0.3 gcil -H -p
    FORCE_COLOR=1 gcil -H -p
    FORCE_COLOR=1 gcil -c ./.gitlab-ci.local.older.yml -H -p
    FORCE_COLOR=1 gcil -c ./.gitlab-ci.local.newer.yml -H -p
    FORCE_COLOR=1 gcil -c ./.gitlab-ci.local.int.yml -H -p
    FORCE_COLOR=1 gcil -c ./.gitlab-ci.local.float.yml -H -p
    FORCE_COLOR=1 gcil -c ./.gitlab-ci.local.str.yml -H -p
  fi
)
