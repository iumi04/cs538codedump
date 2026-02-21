import functions_framework
from google.cloud import storage
from google.cloud import pubsub_v1
import json

BUCKET_NAME = "umihw2bucket"
TOPIC_NAME = "forbiddenRequestsTopic"

FORBIDDEN_COUNTRIES = {
    "North Korea", "Iran", "Cuba", "Myanmar",
    "Iraq", "Libya", "Sudan", "Zimbabwe", "Syria"
}

storageClient = storage.Client()
publisher = pubsub_v1.PublisherClient()

topicPath = publisher.topic_path(
    storageClient.project, TOPIC_NAME
)

@functions_framework.http
def fileService(request):

    if request.method != "GET":
        log = {
            "error": "Unsupported HTTP method",
            "method": request.method
        }
        print(json.dumps(log))
        return ("Not Implemented", 501)

    country = request.headers.get("X-country", "UNKNOWN")

    if country in FORBIDDEN_COUNTRIES:

        message = f"Forbidden request from {country}"
        publisher.publish(topicPath, message.encode())

        log = {
            "error": "Forbidden country",
            "country": country
        }
        print(json.dumps(log))

        return ("Permission Denied", 400)

    filename = request.args.get("file")

    if not filename:
        return ("File parameter missing", 400)

    try:
        bucket = storageClient.bucket(BUCKET_NAME)
        blob = bucket.blob(f"generated_html/{filename}")

        if not blob.exists():
            raise Exception("File missing")

        content = blob.download_as_text()
        return (content, 200)

    except Exception:
        log = {
            "error": "File not found",
            "file": filename
        }
        print(json.dumps(log))
        return ("File not found", 404)
