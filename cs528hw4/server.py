import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from google.cloud import storage, logging as cloud_logging, pubsub_v1
import json

PROJECT_ID = "cs528-project-0"
BUCKET_NAME = "umihw2bucket"
TOPIC_ID = "forbiddenRequests"  
BANNED_COUNTRIES = ["North Korea", "Iran", "Cuba", "Myanmar", "Iraq", "Libya", "Sudan", "Zimbabwe", "Syria"]

log_client = cloud_logging.Client()
logger = log_client.logger("hw4-web-server")

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        filename = self.path.lstrip("/")
        country = self.headers.get("X-country")

        if country in BANNED_COUNTRIES:
            logger.log_text(f"CRITICAL: Forbidden access from {country}", severity="CRITICAL")

            try:
                publisher.publish(topic_path, country.encode("utf-8"))
            except Exception:
                pass

            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Permission Denied")
            return

        try:
            client = storage.Client()
            bucket = client.bucket(BUCKET_NAME)
            blob = bucket.blob(filename)

            if not blob.exists():
                logger.log_text(f"WARNING: File {filename} not found", severity="WARNING")
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"404 Not Found")
                return

            content = blob.download_as_bytes()

            self.send_response(200)
            self.end_headers()
            self.wfile.write(content)

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

    def do_POST(self):
        logger.log_text("WARNING: POST not implemented", severity="WARNING")
        self.send_response(501)
        self.end_headers()
        self.wfile.write(b"501 Not Implemented")

    def do_PUT(self):
        self.do_POST()

    def do_DELETE(self):
        self.do_POST()

    def do_PATCH(self):
        self.do_POST()


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 80), MyHandler)
    print("Server running on port 80...")
    server.serve_forever()