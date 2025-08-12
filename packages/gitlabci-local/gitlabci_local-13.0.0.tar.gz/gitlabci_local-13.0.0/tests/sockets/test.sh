#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Detect engines
engine_docker=$(
  (type docker >/dev/null 2>&1 && timeout 5 docker --help | grep -iq 'Docker version' && echo 'true') \
    || (curl -s -o /dev/null "${DOCKER_HOST##*/}" && echo 'true') \
    || true
)

# Run tests (pull)
gcil -c ./.gitlab-ci.incomplete.yml --dump
gcil -c ./.gitlab-ci.incomplete.yml --pull
gcil -c ./.gitlab-ci.global.yml --dump
gcil -c ./.gitlab-ci.global.yml --pull
gcil -c ./.gitlab-ci.specific.yml --dump
gcil -c ./.gitlab-ci.specific.yml --pull
gcil -c ./.gitlab-ci.custom.yml --dump
gcil -c ./.gitlab-ci.custom.yml --pull

# Non-Docker hosts
if [ -z "${engine_docker}" ]; then
  echo 'WARNING: The sockets tests are ignored on non-Docker hosts'
  exit 0
fi

# Configure Docker
if [ ! -z "${DOCKER_HOST}" ] && echo "${DOCKER_HOST}" | grep -q '^tcp://'; then
  docker_hostname=$(echo "${DOCKER_HOST}" | sed 's#tcp://\(.*\):.*#\1#')
  docker_ip=$(getent ahostsv4 "${docker_hostname}" | head -n1 | cut -d' ' -f1)
  export DOCKER_HOST=$(echo "${DOCKER_HOST}" | sed "s#${docker_hostname}#${docker_ip}#g")
fi

# Run tests (incomplete)
timeout 5 gcil -c ./.gitlab-ci.incomplete.yml -p && exit 1 || true
timeout 5 gcil -c ./.gitlab-ci.incomplete.yml -p --sockets

# Run tests (global)
timeout 5 gcil -c ./.gitlab-ci.global.yml 'Job 1'
timeout 5 gcil -c ./.gitlab-ci.global.yml 'Job 2' && exit 1 || true

# Run tests (environment)
DOCKER_CERT_PATH="${DOCKER_CERT_PATH}" DOCKER_TLS_VERIFY="${DOCKER_TLS_VERIFY}" timeout 5 gcil -c ./.gitlab-ci.global.yml 'Job 1' || true
DOCKER_HOST='tcp://127.0.0.1:1234' timeout 5 gcil -c ./.gitlab-ci.global.yml 'Job 1' && exit 1 || true
DOCKER_HOST='unix:///var/run/docker.sock' timeout 5 gcil -c ./.gitlab-ci.global.yml 'Job 1' || true

# Run tests (specific)
timeout 5 gcil -c ./.gitlab-ci.specific.yml -p

# Run tests (custom)
timeout 5 gcil -c ./.gitlab-ci.custom.yml -p
timeout 5 gcil -c ./.gitlab-ci.custom.yml 'Job 2' && exit 1 || true
