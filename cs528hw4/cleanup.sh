#!/bin/bash
PROJECT_ID=$(gcloud config get-value project)
SA_EMAIL="hw4vmserviceaccount@${PROJECT_ID}.iam.gserviceaccount.com"

echo "Tearing down HW4 infrastructure..."

gcloud compute instances delete web-server-vm reporter-vm --zone=us-central1-a --quiet
gcloud compute addresses delete server-static-ip --region=us-central1 --quiet
gcloud compute firewall-rules delete allow-http-80 --quiet
gcloud projects remove-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/storage.objectViewer"
gcloud projects remove-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/logging.logWriter"
gcloud projects remove-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/pubsub.publisher"
gcloud projects remove-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/pubsub.subscriber"
gcloud iam service-accounts delete $SA_EMAIL --quiet

echo "Cleanup complete."