#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Prepare aliases
alias pexpect-executor='pexpect-executor --delay-init 0.2 --delay-press 0.2 --delay-prompt 0.2'

# Configure tests
set -ex

# Run tests
gcil -c ./.gitlab-ci.local.yml --dump
gcil -c ./.gitlab-ci.local.yml -H -p
gcil -c ./.gitlab-ci.project.yml --dump
gcil -c ./.gitlab-ci.component.yml --dump
gcil -c ./.gitlab-ci.component.missing.yml --dump && exit 1 || true
gcil -c ./.gitlab-ci.component.notfound.yml --dump && exit 1 || true
gcil -c ./.gitlab-ci.component.duplicates.yml --dump
gcil -c ./.gitlab-ci.component.empty.yml --dump && exit 1 || true
gcil -c ./.gitlab-ci.mandatory.yml --dump && exit 1 || true
gcil -c ./.gitlab-ci.nospec.yml --dump
gcil -c ./.gitlab-ci.include.0.yml --dump && exit 1 || true
gcil -c ./.gitlab-ci.include.3.yml --dump && exit 1 || true
gcil -c ./.gitlab-ci.types.yml --dump
gcil -c ./.gitlab-ci.types.unknown.broken.yml --dump && exit 1 || true
gcil -c ./.gitlab-ci.types.boolean.0.yml --dump
gcil -c ./.gitlab-ci.types.boolean.1.yml --dump
gcil -c ./.gitlab-ci.types.boolean.false.yml --dump
gcil -c ./.gitlab-ci.types.boolean.true.yml --dump
gcil -c ./.gitlab-ci.types.boolean.broken.yml --dump && exit 1 || true
gcil -c ./.gitlab-ci.types.number.boolean.yml --dump && exit 1 || true
gcil -c ./.gitlab-ci.types.number.broken.yml --dump && exit 1 || true
gcil -c ./.gitlab-ci.types.number.integer.yml --dump
gcil -c ./.gitlab-ci.types.number.floating.yml --dump
gcil -c ./.gitlab-ci.types.number.regex.yml --dump && exit 1 || true
gcil -c ./.gitlab-ci.types.options.boolean.yml --dump && exit 1 || true
gcil -c ./.gitlab-ci.types.options.empty.yml --dump && exit 1 || true
gcil -c ./.gitlab-ci.types.options.integer.yml --dump && exit 1 || true
gcil -c ./.gitlab-ci.types.options.floating.yml --dump && exit 1 || true
gcil -c ./.gitlab-ci.types.options.regex.yml --dump && exit 1 || true
gcil -c ./.gitlab-ci.types.options.strings.yml --dump && exit 1 || true
gcil -c ./.gitlab-ci.types.options.unknown.yml --dump && exit 1 || true
gcil -c ./.gitlab-ci.types.strings.regex.yml --dump && exit 1 || true
gcil -c ./.gitlab-ci.types.include.options.yml --dump && exit 1 || true
gcil -c ./.gitlab-ci.types.include.regex.yml --dump && exit 1 || true
gcil -c ./.gitlab-ci.types.array.unsupported.yml --dump && exit 1 || true
gcil -c ./.gitlab-ci.types.array.unsupported.yml --dump && exit 1 || true
gcil -c ./.gitlab-ci.types.boolean.true.yml --configure --input stage='components_input' --input name='job_input' --input flag='false' --dump </dev/null
gcil -c ./.gitlab-ci.types.boolean.true.yml --configure --input stage='components_input' --input name='job_input' --input flag='no' --dump </dev/null && exit 1 || true
gcil -c ./.gitlab-ci.types.strings.empty.yml --configure --input stage='components_input' --input name='job_input' --input comments='' --dump </dev/null
pexpect-executor \
    --press '\-stage' --enter \
    --down --enter \
    --down --enter \
    -- gcil -c ./.gitlab-ci.types.strings.empty.yml --configure --dump --pipeline </dev/null
gcil -c ./.gitlab-ci.types.strings.empty.yml --configure --dump </dev/null
pexpect-executor \
    --press '\-stage' --enter \
    --down --enter \
    --down --enter \
    --down --enter \
    --down --down --enter \
    --down --enter \
    --down --enter \
    --down --enter \
    --down --down --enter \
    -- gcil -c ./.gitlab-ci.types.yml --configure --dump </dev/null
