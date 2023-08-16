#!/bin/bash
set -ex # -e: exit immediately if there are errors. -x: print out every line that runs

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
systemctl stop viam-server-canary

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
systemctl start viam-server-canary
echo "viam-server up"
sleep 60 # The server takes some time to set up its connections; don't talk to it too soon.

# TODO: consider updating the repo to the latest version here. Is that something that you can do in
# a cron job, where you don't have user credentials?

echo "running tests..."
./test_gpios.py
echo "done running tests!"

pushd > /dev/null
exit 0