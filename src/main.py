#!/bin/python
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

import dose_rates


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            results = dose_rates.get_data()
            body = '\n'.join(results)

            self.send_response(200)
            self.send_header(
                "Content-type", "text/plain; charset=utf-8; version=0.0.4")
            self.end_headers()
            self.wfile.write(body.encode())

        else:
            body = "404 Not Found"
            self.send_response(404)
            self.end_headers()
            self.wfile.write(body.encode())


httpd = HTTPServer(('0.0.0.0', 8080), SimpleHTTPRequestHandler)
httpd.serve_forever()
