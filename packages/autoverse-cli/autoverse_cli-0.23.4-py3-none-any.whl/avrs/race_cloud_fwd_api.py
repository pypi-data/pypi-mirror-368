import argparse
import json
import re
import threading
import http
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer

# https://gist.github.com/dfrankow/f91aefd683ece8e696c26e183d696c29

class ApiForwardHandler(BaseHTTPRequestHandler):
    def __init__(self, target_port):
        self.target_port = target_port

    # allows to be passed to the HTTPServer ctor
    def __call__(self, *args, **kwargs):
        """Handle a request."""
        super().__init__(*args, **kwargs)

    def do_POST(self):

        length = int(self.headers.get('content-length'))
        rfile_str = self.rfile.read(length).decode('utf8')
        sim_response = self.get_fwd_response(rfile_str)
        try:
            print("{} : {}".format(self.client_address, rfile_str))
        except:
            pass
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(sim_response.encode('utf-8'))
        self.end_headers()
        
    def get_fwd_response(self, body):
        connection = http.client.HTTPConnection('localhost', self.target_port, timeout=3)
        headers = {
            'Content-type': 'application/json',
        }
        #body = json.dumps(body).encode('utf-8') # already a string here
        connection.request('POST', '/post', body, headers)
        response = connection.getresponse()
        response_string = ''
        if response.status != 200:
            pass
        else:
            response_string = response.read().decode('utf-8')
        return response_string
    