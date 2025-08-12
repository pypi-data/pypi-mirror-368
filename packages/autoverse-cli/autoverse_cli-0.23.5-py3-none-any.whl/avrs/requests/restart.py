from avrs.requests.request import AvrsApiRequest

class Restart(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'RestartSimulation', 0)
        psr = parser.add_parser('restart', help='command to restart the entire simulator')
        psr.set_defaults(func=self.send_request)
    
    def get_request_body(self, args):
        return {
            
        }