#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil --settings
! type sudo >/dev/null 2>&1 || sudo -E env PYTHONPATH="${PYTHONPATH}" gcil --settings
gcil --set && exit 1 || true
gcil --set GROUP && exit 1 || true
gcil --set GROUP KEY && exit 1 || true
gcil --set package test 1
gcil --set package test 0
gcil --set package test UNSET
gcil --set updates enabled NaN
gcil --version
gcil --set updates enabled UNSET
settings_gcil=$(gcil --no-color --settings | grep -o 'Settings: [^ ]*' | cut -d' ' -f2)
settings_gcil=$(dirname "${settings_gcil}")
settings_gitlabci_local=$(echo "${settings_gcil}" | sed 's#gcil#gitlabci-local#g')
mkdir -p "${settings_gitlabci_local}/"
touch "${settings_gitlabci_local}/settings.ini"
gcil --settings && exit 1 || true
rm -rf "${settings_gitlabci_local}"
gcil --settings
