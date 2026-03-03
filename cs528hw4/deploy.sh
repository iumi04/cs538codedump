#!/bin/bash
PROJECT_ID="cs528-project-0"
SERVICE_ACCOUNT="hw4vmserviceaccount@${PROJECT_ID}.iam.gserviceaccount.com"
ZONE="us-central1-a"
BUCKET="umihw2bucket"

gcloud compute addresses create server-static-ip --region=us-central1 --project=$PROJECT_ID

gcloud compute instances create reporter-vm \
    --zone=$ZONE \
    --machine-type=e2-micro \
    --service-account=$SERVICE_ACCOUNT \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --metadata=startup-script="#!/bin/bash
        apt-get update
        apt-get install -y python3-pip
        pip3 install --break-system-packages google-cloud-pubsub google-cloud-storage
        gsutil cp gs://$BUCKET/reporter.py /home/reporter.py
        python3 /home/reporter.py > /home/reporter_log.out 2>&1 &"

gcloud compute instances create web-server-vm \
    --zone=$ZONE \
    --machine-type=e2-micro \
    --address=server-static-ip \
    --service-account=$SERVICE_ACCOUNT \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --tags=http-server \
    --metadata=startup-script="#!/bin/bash
    apt-get update
    apt-get install -y python3-pip
    pip3 install --break-system-packages google-cloud-storage google-cloud-logging google-cloud-pubsub
    gsutil cp gs://$BUCKET/server.py /home/server.py
    nohup sudo python3 /home/server.py > /home/server.log 2>&1 &"

gcloud compute firewall-rules create allow-http-80 --allow tcp:80 --target-tags=http-server
