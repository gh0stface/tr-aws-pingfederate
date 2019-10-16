#!/bin/bash

if [ $NODE_ROLE = "CLUSTERED_CONSOLE" ] ; then
    aws s3 cp $DATA_HOME/data.zip $PF_HOME/server/default/data/drop-in-deployer/data.zip
fi

# Restarts nodes to correct Oauth client JDBC issue.
$PF_HOME/sbin/pingfederate-run.sh &&
sleep 75 &&
$PF_HOME/sbin/pingfederate-shutdown.sh &&
sleep 15 &&
$PF_HOME/bin/run.sh &
sleep 120

if [ $NODE_ROLE = "CLUSTERED_CONSOLE" ] ; then
    $PF_HOME/bin/replicate.sh
else
    sleep 30
fi

# The engine tasks are stubborn, so they need another restart.
if [ $PROVISIONER = "OFF" ] && [ $NODE_ROLE = "CLUSTERED_ENGINE" ] ; then
    sleep 240
    $PF_HOME/sbin/pingfederate-shutdown.sh &&
    sleep 15 &&
    $PF_HOME/bin/run.sh &
    sleep 120
else
    sleep 210
fi

sudo service cron start && sudo rm -f /etc/sudoers.d/a${AAID}-PowerUser2

if [ $NODE_ROLE = "CLUSTERED_CONSOLE" ] ; then
    (crontab -l 2>/dev/null; echo "*/5 * * * * . /tmp/export_envvars.sh && $PF_HOME/bin/replicate.sh") | crontab -
    (crontab -l 2>/dev/null; echo "*/5 * * * * . /tmp/export_envvars.sh && $PF_HOME/bin/export.sh") | crontab -
fi

sleep infinity
