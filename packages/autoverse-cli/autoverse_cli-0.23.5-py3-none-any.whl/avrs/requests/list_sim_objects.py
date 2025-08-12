from avrs.requests.request import AvrsApiRequest

class AvrsListSimObjectsRequest(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'ListSimObjects', 0)
        psr = parser.add_parser('list-sim-objects', help='list all the sim objects that currently exist in the simulator')
        psr.add_argument(
            '-v',
            action='store_true',
            help='request verbose output')
        psr.add_argument(
            '--components',
            action='store_true',
            help='also print information about the object components')
        psr.add_argument(
            '--isolate',
            default='',
            help='indicate a specific object of interest')
        psr.set_defaults(func=self.send_request)
    
    def get_request_body(self, args):
        return {
            "bVerbose": args.v,
            'bListComponents': args.components,
            'isolate': args.isolate
        }