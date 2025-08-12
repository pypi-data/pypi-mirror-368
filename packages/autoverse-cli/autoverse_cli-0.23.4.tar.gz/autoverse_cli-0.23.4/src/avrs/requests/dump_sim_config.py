from avrs.requests.request import AvrsApiRequest

class AvrsDumpSimConfigRequest(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'DumpSimConfig', '')
        psr = parser.add_parser(
            'dump-sim-config', 
            help='dump all currently loaded configuration from the simulation')
        
        psr.set_defaults(func=self.send_request)
    
    def get_request_body(self, args):
        return {
        }