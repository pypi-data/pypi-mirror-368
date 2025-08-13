#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gitlab-projects-migrate --help
gitlab-projects-migrate --help --no-color
gitlab-projects-migrate --set themes no_color 1
gitlab-projects-migrate --help
gitlab-projects-migrate --set themes no_color 0
gitlab-projects-migrate --help
gitlab-projects-migrate --set themes no_color UNSET
gitlab-projects-migrate --help
FORCE_COLOR=1 gitlab-projects-migrate --help
FORCE_COLOR=0 gitlab-projects-migrate --help
NO_COLOR=1 gitlab-projects-migrate --help
