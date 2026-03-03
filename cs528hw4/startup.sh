#!/bin/bash
if [ -f /var/log/startup_already_done ]; then
    echo "Startup script already ran once. Skipping."
    exit 0
fi

apt-get update
apt-get install -y python3-pip
pip3 install --break-system-packages flask google-cloud-storage google-cloud-logging google-cloud-pubsub requests

touch /var/log/startup_already_done