#!/bin/bash
set -ex # -e: exit immediately if there are errors. -x: print out every line that runs

date # TODO: remove this when we have logging properly set up

if [[ "$(whoami)" != "root" ]] ; then
	echo "We must run as root, but currently we're $(whoami) instead."
	exit 1
fi

# See https://stackoverflow.com/a/1482133 for an explanation of this next line. It gets the
# directory in which this script resides.
this_dir="$(dirname -- "$( readlink -f -- "$0"; )")";
echo "this_dir is $this_dir"
pushd "$this_dir" > /dev/null

# This script is adapted from
# https://viam.atlassian.net/wiki/spaces/ENG/pages/155451406/Data+ML+Canary+Testing+Bot

now=$(date +"%T")
echo "Current time : $now"
# stop the viam-server first
echo "stopping viam-server"
systemctl stop viam-canary

# UPDATE RDK
viam-server --aix-update
if [ $? -eq 0 ]
then
  echo "rdk successfully updated RDK"
else 
  echo "rdk failed to update RDK"
fi

# Start the Viam Server after updating
echo "restarting the viam-server"
systemctl start viam-canary
echo "viam-server up"
sleep 60 # The server takes some time to set up its connections; don't talk to it too soon.

git pull --ff-only origin main # Update the test script if necessary

echo "running tests..."
# The cron job that runs our script writes stdout to file. If something goes wrong in the tests, it
# will be written to stderr. Redirect that to stdout so it gets written to file, too.
./test_gpios.py 2>&1
echo "done running tests!"

popd > /dev/null # pushd "$this_dir"
exit 0
