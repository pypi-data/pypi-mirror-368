#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
git-dct --settings
! type sudo >/dev/null 2>&1 || sudo -E env PYTHONPATH="${PYTHONPATH}" git-dct --settings
git-dct --set && exit 1 || true
git-dct --set GROUP && exit 1 || true
git-dct --set GROUP KEY && exit 1 || true
git-dct --set package test 1
git-dct --set package test 0
git-dct --set package test UNSET
git-dct --set updates enabled NaN
git-dct --version
git-dct --set updates enabled UNSET
