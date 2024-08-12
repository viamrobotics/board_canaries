#!/bin/bash
set -ex # -e: exit early on any error. -x: write all commands to stderr

date '+%Y-%m-%d'

# See https://stackoverflow.com/a/1482133 for an explanation of this next line.
# It gets the directory in which this script resides.
this_dir="$(dirname -- "$( readlink -f -- "$0"; )")";
pushd "$this_dir" > /dev/null

source venv/bin/activate

# The sed line keeps only the file contents that match the current date and
# later. This solution was taken from https://stackoverflow.com/a/7104422
cat /var/log/canary_tests.log |\
	sed -n "/$(date '+%Y-%m-%d')/,\$p" |\
	./analyze_logs.py

popd > /dev/null # pushd "$this_dir"
