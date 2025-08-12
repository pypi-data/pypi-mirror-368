import socket
import json
import os
import os.path
import multiprocessing
import time
import sys
import http.client

# the new API request

class AvrsRestApiRequest:
    def __init__(self, parser, cfg, endpoint, method):
        self.endpoint = endpoint
        self.method = method
        self.verbose = False
        self.cfg = cfg

    def get_request_body(self, args):
        return {}

    def get_request_params(self, args):
        return {}

    def send_request(self, args):

        sim_address = '0.0.0.0'
        # if 'sim_address' in self.cfg:
        #     sim_address = self.cfg['sim_address']
        # connection_addr = os.environ.get('AVRS_SIM_ADDRESS', sim_address)

        sim_port = 51111
        # if 'sim_api_port' in self.cfg:
        #     sim_port = self.cfg['sim_api_port']

        if args.verbose:
            print('sending request to: {}:{}'.format(sim_address, sim_port))
        connection = http.client.HTTPConnection(sim_address, sim_port, timeout=10)
        headers = {'Content-type': 'application/json'}
        body = json.dumps(self.get_request_body(args)).encode('utf-8')
        connection.request(self.method, self.endpoint, body, headers)
        response = connection.getresponse()
        if response.status != 200:
            print('response had status code {}'.format(response.status))
        print('{}'.format(response.read().decode('utf-8')))
