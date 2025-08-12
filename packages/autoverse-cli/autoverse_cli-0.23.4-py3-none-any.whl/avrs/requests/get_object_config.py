from avrs.requests.request import AvrsApiRequest

class AvrsGetObjectConfigRequest(AvrsApiRequest):
    def __init__(self, parser, cfg):
            AvrsApiRequest.__init__(self, parser, cfg, 'GetObjectConfig', '')
            psr = parser.add_parser('get-object-config', help='returns the JSON structure of an objects configuration')

            psr.add_argument(
                '--target',
                default='ego',
                help='the simulated object to return config for')

            psr.set_defaults(func=self.send_request)

    def get_request_body(self, args):
        self.target_object_id = args.target
        return {
        }