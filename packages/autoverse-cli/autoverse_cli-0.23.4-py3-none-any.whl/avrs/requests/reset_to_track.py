from avrs.requests.request import AvrsApiRequest

class ResetToTrack(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'ResetToTrack', 'Ego')
        psr = parser.add_parser(
            'reset-to-track', 
            help='moves the car to the closest point on track pointing down track')

        psr.add_argument(
            '--object-name',
            default='ego',
            help='the simulated object to reset to track')

        psr.set_defaults(func=self.send_request)
    
    def get_request_body(self, args):
        self.target_object_id = args.object_name
        return {
            
        }