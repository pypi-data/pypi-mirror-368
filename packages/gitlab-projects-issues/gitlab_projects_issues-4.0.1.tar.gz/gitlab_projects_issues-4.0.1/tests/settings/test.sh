#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gitlab-projects-issues --settings
! type sudo >/dev/null 2>&1 || sudo -E env PYTHONPATH="${PYTHONPATH}" gitlab-projects-issues --settings
gitlab-projects-issues --set && exit 1 || true
gitlab-projects-issues --set GROUP && exit 1 || true
gitlab-projects-issues --set GROUP KEY && exit 1 || true
gitlab-projects-issues --set package test 1
gitlab-projects-issues --set package test 0
gitlab-projects-issues --set package test UNSET
gitlab-projects-issues --set updates enabled NaN
gitlab-projects-issues --version
gitlab-projects-issues --set updates enabled UNSET
