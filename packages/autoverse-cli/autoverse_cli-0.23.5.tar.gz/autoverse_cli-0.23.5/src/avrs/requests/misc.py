from avrs.requests.request import AvrsApiRequest
from avrs.requests.rest_request import AvrsRestApiRequest

class AvrsGetSimVersionRequest(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'GetVersion', 0)
        psr = parser.add_parser('get-sim-version', help='get the version of the currently running simulator')
        psr.set_defaults(func=self.send_request)
    
    def get_request_body(self, args):
        return {
        }
    
class AvrsGetSessionIdRequest(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'GetSessionId', 0)
        psr = parser.add_parser('get-session-id', help='get the session ID of the currently running simulator session')
        psr.set_defaults(func=self.send_request)
    
    def get_request_body(self, args):
        return {
        }

class AvrsDescribeSimRestRequest(AvrsRestApiRequest):
    def __init__(self, parser, cfg):
        AvrsRestApiRequest.__init__(self, parser, cfg, '/api/v1.0/describe-app', 'GET')
        psr = parser.add_parser('describe-app', help='get the version of the currently running simulator')
        psr.set_defaults(func=self.send_request)

    def get_request_params(self, args):
        return {}

class AvrsGetExitSimRequest(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'ExitSim', 0)
        psr = parser.add_parser('exit-sim', help='exit the currently running simulator')
        psr.set_defaults(func=self.send_request)
    
    def get_request_body(self, args):
        return {
        }

class AvrsPingRequest(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'GetVersion', 0)
        psr = parser.add_parser('ping', help='ping the simulator to see if it is running and responsive')
        psr.set_defaults(func=self.send_ping)

    def send_ping(self, args):
        try:
            self.send_http_request(args)
        except:
            print('no')

class AvrsConfigureSimLodRequest(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'ConfigureSimLod', 'lodctrl')
        psr = parser.add_parser('set-lod', help='set the LOD of the sim, possibly reducing GPU overhead')

        psr.add_argument(
            'lod', 
            type=int, 
            help='the new lod level to set. 0 is max lod, 1 is min lod')

        psr.set_defaults(func=self.send_request)
    
    def get_request_body(self, args):
        return {
            'newLod': args.lod
        }