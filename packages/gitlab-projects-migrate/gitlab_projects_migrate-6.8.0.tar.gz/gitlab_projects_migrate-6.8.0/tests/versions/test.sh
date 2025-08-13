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
  gitlab-projects-migrate --version
  gitlab-projects-migrate --update-check
  DEBUG_UPDATES_DISABLE=true gitlab-projects-migrate --update-check
  FORCE_COLOR=1 gitlab-projects-migrate --update-check
  NO_COLOR=1 gitlab-projects-migrate --update-check
  FORCE_COLOR=1 PYTHONIOENCODING=ascii gitlab-projects-migrate --update-check
  FORCE_COLOR=1 COLUMNS=40 gitlab-projects-migrate --update-check
  FORCE_COLOR=1 DEBUG_UPDATES_OFFLINE='' gitlab-projects-migrate --update-check
  FORCE_COLOR=1 DEBUG_UPDATES_OFFLINE=true gitlab-projects-migrate --update-check
  FORCE_COLOR=1 DEBUG_UPDATES_OFFLINE=true DEBUG_VERSION_FAKE=0.0.2 DEBUG_UPDATES_FAKE=0.0.1 gitlab-projects-migrate --update-check
  FORCE_COLOR=1 DEBUG_UPDATES_OFFLINE=true DEBUG_VERSION_FAKE=0.0.2 DEBUG_UPDATES_FAKE=0.0.2 gitlab-projects-migrate --update-check
  FORCE_COLOR=1 DEBUG_UPDATES_OFFLINE=true DEBUG_VERSION_FAKE=0.0.2 DEBUG_UPDATES_FAKE=0.0.3 gitlab-projects-migrate --update-check
  FORCE_COLOR=1 DEBUG_UPDATES_DAILY=true DEBUG_VERSION_FAKE=0.0.2 DEBUG_UPDATES_FAKE=0.0.3 gitlab-projects-migrate || true
  FORCE_COLOR=1 gitlab-projects-migrate || true
  FORCE_COLOR=1 gitlab-projects-migrate --help
)
