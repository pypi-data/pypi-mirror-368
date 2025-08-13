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
  if wine gitlab-projects-migrate --version >/dev/null 2>&1; then
    alias gitlab-projects-migrate='wine gitlab-projects-migrate'
  fi

# Unsupported host
else
  echo 'INFO: Test "windows" was ignored as it is not supported on this host'
  exit 0
fi

# Configure tests
set -ex

# Run tests
gitlab-projects-migrate --settings
gitlab-projects-migrate --help
