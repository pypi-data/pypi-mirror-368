from avrs.requests.request import AvrsApiRequest

class AvrsEnvironmentRequests():
    def __init__(self, parser, cfg):
            psr = parser.add_parser('environment', help='Edits the environment')
            sps = psr.add_subparsers(required= True, help='')
            AvrsSetTimeOfDayRequest(sps, cfg)
            AvrsGetEnvironmentMetaRequets(sps, cfg)


class AvrsSetTimeOfDayRequest(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'SetTimeOfDay', '')
        psr = parser.add_parser('set-time-of-day', help='sets the current time of day')
        psr.add_argument('tod', type=float, help='The time of day (0-24) to set')
        psr.set_defaults(func=self.send_request)

    def get_request_body(self, args):
        self.target_object_id = ''
        return {
            'TimeOfDay': args.tod
        }

class AvrsGetEnvironmentMetaRequets(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'GetEnvironmentMeta', '')
        psr = parser.add_parser('get-meta', help='get metadata about the currently loaded environment')
        psr.set_defaults(func=self.send_request)

    def get_request_body(self, args):
            self.target_object_id = ''
            return {
            }

class AvrsSetEnvironmentRequest(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'SetEnvironment', '')
        psr = parser.add_parser('set-environment', help='changes to a new environment')
        psr.add_argument('new_environment_name', help='name of desired environment')
        psr.set_defaults(func=self.send_request)

    def get_request_body(self, args):
        self.target_object_id = ''
        return {
            'newEnvironmentName': args.new_environment_name
        }