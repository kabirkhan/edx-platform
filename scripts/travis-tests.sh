#!/usr/bin/env bash

set -e

# Return status is that of the last command to fail in a
# piped command, or a zero if they all succeed.
set -o pipefail

# There is no need to install the prereqs, as this was already
# just done via the dependencies override section of circle.yml.
export NO_PREREQ_INSTALL='true'

EXIT=0

echo "Only 1 container is being used to run the tests."
echo "To run in more containers, configure parallelism for this repo's settings "
echo "via the CircleCI UI and adjust scripts/circle-ci-tests.sh to match."

echo "Running tests for common/lib/ and pavelib/"
paver test_lib --with-flaky --cov-args="-p" --with-xunitmp || EXIT=1
echo "Running python tests for Studio"
paver test_system -s cms --with-flaky --cov-args="-p" --with-xunitmp || EXIT=1
echo "Running python tests for lms"
paver test_system -s lms --with-flaky --cov-args="-p" --with-xunitmp || EXIT=1
