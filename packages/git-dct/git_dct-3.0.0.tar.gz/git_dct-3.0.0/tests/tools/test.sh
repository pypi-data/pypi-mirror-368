#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
git-dct-tools-git-cauthor --help
git-dct-tools-git-fcp --help
git-dct-tools-git-fe --help
git-dct-tools-git-pu --help
git-dct-tools-git-rb --help
git-dct-tools-git-stat --help
