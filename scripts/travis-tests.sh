#!/usr/bin/env bash

set -ev

# Return status is that of the last command to fail in a
# piped command, or a zero if they all succeed.
set -o pipefail

# There is no need to install the prereqs, as this was already
# just done via the dependencies override section of .travis.yml.
export NO_PREREQ_INSTALL='true'

EXIT=0

echo "Running tests for common/lib/ and pavelib/"
paver test_lib --with-flaky --cov-args="-p" --with-xunitmp || EXIT=1
echo "Running python tests for $TEST_SUITE"
paver test_system -s $TEST_SUITE --with-flaky --cov-args="-p" --with-xunitmp || EXIT=1

exit EXIT;
