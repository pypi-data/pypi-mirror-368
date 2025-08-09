#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gitlab-projects-issues --help
gitlab-projects-issues --help --no-color
gitlab-projects-issues --set themes no_color 1
gitlab-projects-issues --help
gitlab-projects-issues --set themes no_color 0
gitlab-projects-issues --help
gitlab-projects-issues --set themes no_color UNSET
gitlab-projects-issues --help
FORCE_COLOR=1 gitlab-projects-issues --help
FORCE_COLOR=0 gitlab-projects-issues --help
NO_COLOR=1 gitlab-projects-issues --help
