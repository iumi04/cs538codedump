import time
import datetime
from google.cloud import pubsub_v1
from google.cloud import storage

PROJECT_ID = "cs528-project-0"
SUBSCRIPTION_ID = "forbiddenRequestsSub"
BUCKET_NAME = "umihw2bucket"

subscriber = pubsub_v1.SubscriberClient()
storage_client = storage.Client()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

def callback(message):
    text = message.data.decode("utf-8")
    print(f"FORBIDDEN REQUEST RECEIVED: {text}")

    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob("forbidden_logs/log.txt")

    timestamp = datetime.datetime.now().isoformat()
    new_entry = f"{timestamp} - {text}\n"

    try:
        existing = blob.download_as_text()
    except Exception:
        existing = ""

    blob.upload_from_string(existing + new_entry)
    message.ack()

print(f"Listening for messages on {subscription_path}...")
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)

try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    streaming_pull_future.cancel()