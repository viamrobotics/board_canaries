#!/bin/sh
set -ex # -e: exit immediately if there are errors. -x: print out every line that runs

# This is adapted from https://viam.atlassian.net/wiki/spaces/ENG/pages/155451406/Data+ML+Canary+Testing+Bot

now=$(date +"%T")
echo "Current time : $now"
# stop the viam-server first
echo "stopping viam-server"
systemctl stop viam-server-canary

# UPDATE RDK
viam-server-canary --aix-update
if [ $? -eq 0 ]
then
  echo "rdk successfully updated"
else 
  echo "rdk failed to update"
fi

# Start the Viam Server after updating
echo "restarting the viam-server"
systemctl start viam-server-canary
echo "viam-server up"

exit 0
