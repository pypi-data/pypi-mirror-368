#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Unsupported host
USER_ID=$(id -u)
if [ ! "${USER_ID}" = '0' ]; then
  echo 'INFO: Test "permissions" ignored as it needs to run in a root container'
  exit 0
fi

# Prepare temporary holder
temp_dir=$(mktemp -d)
trap "{ rm -rf \"${temp_dir}\"; }" EXIT
mkdir -p "${temp_dir}/holder"

# Prepare temporary clones
mkdir -p "${temp_dir}/holder/parent/"
cp -rf "${test_path}" "${temp_dir}/holder/parent/test"
cp -rf "${test_path}" "${temp_dir}/holder/root"
cp -rf "${test_path}" "${temp_dir}/holder/test"

# Prepare temporary user
id -u test >/dev/null 2>&1 || useradd --create-home test

# Prepare temporary permissions
chmod 755 "${temp_dir}"
chmod 755 "${temp_dir}/holder"
chmod 755 "${temp_dir}/holder/parent"
chown -R test:test "${temp_dir}/holder/parent"
chown -R test:test "${temp_dir}/holder/test"

# Configure tests
set -ex

# Run tests
gcil -H -p
gcil --rmi
timeout -sINT 1 gcil -p && exit 1 || true
sudo -H -u test -E env PYTHONPATH="${PYTHONPATH}" gcil -c "${temp_dir}/holder/root/" -H -p && exit 1 || true
sudo -H -u test -E env PYTHONPATH="${PYTHONPATH}" gcil -c "${temp_dir}/holder/parent/test/" -H -p
sudo -H -u test -E env PYTHONPATH="${PYTHONPATH}" gcil -c "${temp_dir}/holder/test/" -H -p
# TODO: Fix Podman leftovers and remove ' || true'
find ../ -name '.tmp.entrypoint.*' -print -exec false {} + || true
find "${temp_dir}/holder/parent/test/" -name '.tmp.entrypoint.*' -print -exec false {} + || true
find "${temp_dir}/holder/test/" -name '.tmp.entrypoint.*' -print -exec false {} + || true
