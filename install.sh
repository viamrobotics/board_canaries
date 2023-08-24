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

# Install a systemctl file for the canary server
cp viam-server-canary.service /etc/systemd/system
systemctl daemon-reload

# Create a crontab to run the script
cat crontab_template.txt | sed "s/CANARY_DIR/$this_dir/g" > /etc/cron.d/viam-board-canary
