import socket
import json
import os
import os.path
import multiprocessing
import time
import sys
import http.client

class AvrsApiRequest:
    def __init__(self, parser, cfg, request_type, target_id):
        self.target_object_id = target_id
        self.request_type = request_type
        self.verbose = False
        self.cfg = cfg

    def get_request(self, args):
        body = self.get_request_body(args)
        return {
            'TargetObjectId': self.target_object_id,
            'RequestType': self.request_type,
            'bVerboseResponse': args.verbose or self.verbose,
            'RequestBody': body
        }

    def get_request_body(self, args):
        return '{}'

    def send_request(self, args):
        #self.send_tcp_request(args)
        self.send_http_request(args)

    def send_tcp_request(self, args):
        pass
        # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # s.connect((self.ip, self.port))
        # s.send(json.dumps(self.get_request(args)).encode('utf-8'))
        # response = s.recv(self.buffer_size).decode('utf-8')
        # print('{}'.format(response))

    def send_http_request(self, args):

        sim_address = 'localhost'
        if 'sim_address' in self.cfg:
            sim_address = self.cfg['sim_address']
        connection_addr = os.environ.get('AVRS_SIM_ADDRESS', sim_address)

        sim_port = 30313
        if 'sim_api_port' in self.cfg:
            sim_port = self.cfg['sim_api_port']

        if args.verbose:
            print('sending request to: {}:{}'.format(connection_addr, sim_port))
        connection = http.client.HTTPConnection(connection_addr, sim_port, timeout=10)
        headers = {'Content-type': 'application/json'}
        body = json.dumps(self.get_request(args)).encode('utf-8')
        connection.request('POST', '/post', body, headers)
        response = connection.getresponse()
        if response.status != 200:
            print('response had status code {}'.format(response))
        print('{}'.format(response.read().decode('utf-8')))
