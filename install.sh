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

# This next line basically means "it's okay for the root user to update the repo from within a cron
# job, even if the repo is owned by a normal non-root user."
git config --global --add safe.directory "$this_dir"

pip install -r requirements.txt

# Install the RDK server
curl "https://storage.googleapis.com/packages.viam.com/apps/viam-server/viam-server-latest-$(uname -m).AppImage" -o viam-server
chmod 755 viam-server
./viam-server --aix-install

# Install a systemctl file for the canary server
cp viam-canary.service /etc/systemd/system
systemctl daemon-reload

# Create a crontab to run the script. Overwrite anything that had been there previously, in case
# we're installing updates to an old version. We use '%' as the regex delimiter for sed instead of
# the more traditional '/' because there are slashes within $this_dir and we don't want too many
# slashes to confuse the parser.
cat crontab_template.txt | sed "s%CANARY_DIR%$this_dir%g" > /etc/cron.d/viam-board-canary

# Remind the user of the steps they need to do manually
set +x # Stop printing every line: we're going to print them ourselves
echo ""
echo ""
echo "%%%%%%%%%%%%%"
echo "% REMINDER! %"
echo "%%%%%%%%%%%%%"
echo "There are four manual things to do:"
echo "- Set up a robot on app.viam.com, and download its config to"
echo "    /etc/viam-canary.json (not the default /etc/viam.json!)."
echo "- Copy canary_config.example.py into canary_config.py and edit it to be"
echo "    specific to your board."
echo "- Copy slack_reporter_config.example.py into slack_reporter_config.py"
echo "    and edit it to be specific to your board."
# This last one could be automated, but should not be done by the root user, and the rest of this
# script is run as root.
echo "- Run 'cat board_canary.pub >> ~/.ssh/authorized_keys'"
