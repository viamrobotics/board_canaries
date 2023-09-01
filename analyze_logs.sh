#!/bin/bash

# See https://stackoverflow.com/a/1482133 for an explanation of this next line.
# It gets the directory in which this script resides.
this_dir="$(dirname -- "$( readlink -f -- "$0"; )")";
echo "this_dir is $this_dir"
pushd "$this_dir" > /dev/null

# The sed line keeps only the file contents that match the current date and
# later. This solution was taken from https://stackoverflow.com/a/7104422
cat /tmp/canary_tests.log |\
	sed -n "/$(date '+%Y-%m-%d')/,$p" |\
	./analyze_logs.py

popd > /dev/null # pushd "$this_dir"
