#!/bin/bash

set -e
set -x

NO_COVERAGE_TOXENVS=(docs)
if ! [[ "${NO_COVERAGE_TOXENVS[*]}" =~ "${TOXENV}" ]]; then
    codecov --env TRAVIS_OS_NAME TOXENV
fi
