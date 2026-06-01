"""Minimal HTTP receiver for cicflowmeter -u URL mode.

Usage:
    python examples/flow_receiver.py
    cicflowmeter -f capture.pcap -u http://127.0.0.1:8080/flows

See docs/BACKEND_INTEGRATION.md for production integration patterns.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class FlowHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        flow = json.loads(body)
        print(
            f"flow {flow.get('src_ip')}:{flow.get('src_port')} -> "
            f"{flow.get('dst_ip')}:{flow.get('dst_port')} "
            f"duration={flow.get('flow_duration')}"
        )
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    print("Listening on http://127.0.0.1:8080/flows")
    HTTPServer(("127.0.0.1", 8080), FlowHandler).serve_forever()
