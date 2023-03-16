#!/bin/python
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

from prometheus_client import make_wsgi_app, start_http_server
from prometheus_client.exposition import ThreadingWSGIServer
from wsgiref.simple_server import make_server, WSGIRequestHandler

import dose_rates


class SilentHandler(WSGIRequestHandler):
    def log_message(self, format, *args):
        return


def update_data_loop():
    while True:
        dose_rates.update_data()
        time.sleep(300)  # Update data every 5 minutes


if __name__ == "__main__":
    # Start the HTTP server for Prometheus metrics
    prometheus_app = make_wsgi_app()
    httpd = make_server("0.0.0.0", 8080, prometheus_app, handler_class=SilentHandler)

    # Start the data update loop in a separate thread
    data_update_thread = threading.Thread(target=update_data_loop)
    data_update_thread.daemon = True
    data_update_thread.start()

    # Serve requests in the main thread
    httpd.serve_forever()
