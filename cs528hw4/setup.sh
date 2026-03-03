#!/bin/bash
PROJECT_ID=$(gcloud config get-value project)
SA_NAME="hw4vmserviceaccount"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
BUCKET="umihw2bucket" 

gcloud iam service-accounts create $SA_NAME --display-name="HW4 Service Account" || true

for ROLE in roles/storage.objectViewer roles/logging.logWriter roles/pubsub.publisher roles/pubsub.subscriber; do
    gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="$ROLE"
done

gsutil cp server.py gs://$BUCKET/
gsutil cp reporter.py gs://$BUCKET/

gcloud compute addresses create server-static-ip --region=us-central1 || true

gcloud compute instances create web-server-vm \
    --zone=us-central1-a \
    --machine-type=e2-micro \
    --address=server-static-ip \
    --service-account=$SA_EMAIL \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --tags=http-server \
    --metadata-from-file startup-script=startup.sh \
    --metadata=run-cmd="python3 /home/server.py"

gcloud compute instances create reporter-vm \
    --zone=us-central1-a \
    --machine-type=e2-micro \
    --service-account=$SA_EMAIL \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --metadata-from-file startup-script=startup.sh \
    --metadata=run-cmd="python3 /home/reporter.py"

gcloud compute firewall-rules create allow-http-80 --allow tcp:80 --target-tags=http-server || true

gcloud compute ssh web-server-vm --zone=us-central1-a --command="gsutil cp gs://$BUCKET/server.py /home/server.py && sudo python3 /home/server.py &" --quiet
gcloud compute ssh reporter-vm --zone=us-central1-a --command="gsutil cp gs://$BUCKET/reporter.py /home/reporter.py && python3 /home/reporter.py &" --quiet