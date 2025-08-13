#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
git-dct --help
git-dct --help --no-color
git-dct --set themes no_color 1
git-dct --help
git-dct --set themes no_color 0
git-dct --help
git-dct --set themes no_color UNSET
git-dct --help
FORCE_COLOR=1 git-dct --help
FORCE_COLOR=0 git-dct --help
NO_COLOR=1 git-dct --help
