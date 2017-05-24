#!/usr/bin/env bash

set -ev

# Return status is that of the last command to fail in a
# piped command, or a zero if they all succeed.
set -o pipefail

# There is no need to install the prereqs, as this was already
# just done via the dependencies override section of .travis.yml.
export NO_PREREQ_INSTALL='true'

EXIT=0

PAVER_ARGS="--with-flaky --cov-args='-p' --with-xunitmp"
TEST_ARGS="-s $TEST_SUITE"

case "$TEST_SUITE" in

    "quality")
        echo "Finding fixme's and storing report..."
        paver find_fixme > fixme.log || { cat fixme.log; EXIT=1; }
        echo "Finding pep8 violations and storing report..."
        paver run_pep8 > pep8.log || { cat pep8.log; EXIT=1; }
        echo "Finding pylint violations and storing in report..."
        paver run_pylint -l $PYLINT_THRESHOLD > pylint.log || { cat pylint.log; EXIT=1; }

        mkdir -p reports

        echo "Finding ESLint violations and storing report..."
        paver run_eslint -l $ESLINT_THRESHOLD > eslint.log || { cat eslint.log; EXIT=1; }
        echo "Running code complexity report (python)."
        paver run_complexity || echo "Unable to calculate code complexity. Ignoring error."
        echo "Running safe template linter report."
        paver run_safelint -t $SAFELINT_THRESHOLDS > safelint.log || { cat safelint.log; EXIT=1; }
        echo "Running safe commit linter report."
        paver run_safecommit_report > safecommit.log || { cat safecommit.log; EXIT=1; }
        # Run quality task. Pass in the 'fail-under' percentage to diff-quality
        echo "Running diff quality."
        paver run_quality -p 100 || EXIT=1

        # # Need to create an empty test result so the post-build
        # # action doesn't fail the build.
        # emptyxunit "quality"
        ;;
    "lms")
        paver test_system -s $TEST_SUITE --with-flaky --cov-args="-p" --with-xunitmp || EXIT=1
        ;;
    "cms")
        paver test_system -s $TEST_SUITE --with-flaky --cov-args="-p" --with-xunitmp || EXIT=1
        ;;
    "lib")
        paver test_lib --with-flaky --cov-args="-p" -v --with-xunit
        ;;

exit $EXIT;
