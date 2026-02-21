from google.cloud import pubsub_v1
from google.cloud import storage
import datetime
import time

PROJECT_ID = "cs528-project-0"
SUBSCRIPTION_ID = "forbiddenRequestsSub"
BUCKET_NAME = "umihw2bucket"

subscriber = pubsub_v1.SubscriberClient()
storageClient = storage.Client()

subscriptionPath = subscriber.subscription_path(
    PROJECT_ID, SUBSCRIPTION_ID
)

def callback(message):
    text = message.data.decode()
    print("Forbidden request received:", text)

    bucket = storageClient.bucket(BUCKET_NAME)
    blob = bucket.blob("forbidden_logs/log.txt")

    timestamp = datetime.datetime.now().isoformat()
    newEntry = f"{timestamp} - {text}\n"

    try:
        existing = blob.download_as_text()
    except:
        existing = ""

    blob.upload_from_string(existing + newEntry)

    message.ack()

print("Listening for forbidden requests...")

subscriber.subscribe(subscriptionPath, callback=callback)

while True:
    time.sleep(60)
