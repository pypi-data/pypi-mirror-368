
from avrs.requests.request import AvrsApiRequest

class MoveToLandmarkRequest(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'MoveToLandmark', 'Ego')
        psr = parser.add_parser('move-to-landmark', help='command an object to move to a landmark')
        psr.add_argument('--object-name', default='Ego', help='the name of the object to move')
        psr.add_argument('landmark', help='the name of the landmark to move the object to')
        psr.set_defaults(func=self.send_request)

    def get_request_body(self, args):
        self.target_object_id = args.object_name
        return {
            'LandmarkName': args.landmark
        }