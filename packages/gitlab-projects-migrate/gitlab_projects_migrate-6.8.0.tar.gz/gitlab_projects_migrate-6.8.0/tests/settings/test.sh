#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gitlab-projects-migrate --settings
! type sudo >/dev/null 2>&1 || sudo -E env PYTHONPATH="${PYTHONPATH}" gitlab-projects-migrate --settings
gitlab-projects-migrate --set && exit 1 || true
gitlab-projects-migrate --set GROUP && exit 1 || true
gitlab-projects-migrate --set GROUP KEY && exit 1 || true
gitlab-projects-migrate --set package test 1
gitlab-projects-migrate --set package test 0
gitlab-projects-migrate --set package test UNSET
gitlab-projects-migrate --set updates enabled NaN
gitlab-projects-migrate --version
gitlab-projects-migrate --set updates enabled UNSET
