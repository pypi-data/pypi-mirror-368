#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Detect Windows host
if [ "${OSTYPE}" = 'msys' ] || [ "${OSTYPE}" = 'win32' ]; then
  echo 'INFO: Test "windows" running on a Windows host'

# Detect Wine support
elif type wine >/dev/null 2>&1 && wine python --version >/dev/null 2>&1; then
  echo 'INFO: Test "windows" running in a Wine Python environment'
  if wine gcil --version >/dev/null 2>&1; then
    alias gcil='wine gcil'
  fi

# Unsupported host
else
  echo 'INFO: Test "windows" was ignored as it is not supported on this host'
  exit 0
fi

# Configure tests
set -ex

# Run tests
gcil --settings
gcil -c ../simple/ </dev/null && exit 1 || true
WINPTY_BINARY_PATH='winpty.exe.missing' gcil -c ../simple/ </dev/null && exit 1 || true
WINPTY_BINARY_PATH='where.exe' gcil -c ../simple/ </dev/null || true
