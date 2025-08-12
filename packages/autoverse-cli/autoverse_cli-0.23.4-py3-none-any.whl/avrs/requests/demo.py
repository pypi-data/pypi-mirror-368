from avrs.requests.request import AvrsApiRequest

class AvrsDemoRequest(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'DemoSendConfig', '')
        psr = parser.add_parser('demo', help='Sends a request used for a demonstration')
        psr.add_argument('--ego-type-index', type=int, default=0, help='')
        psr.add_argument('--npc-density', type=int)
        psr.add_argument('--env-type-index', default=0, type=int)
        psr.add_argument('--weather-type-index', default=0, type=int)
        psr.set_defaults(func=self.send_request)

    def get_request_body(self, args):
        return {
            'IndexEgoType': args.ego_type_index,
            'NpcDensity': args.npc_density,
            'IndexEnvironmentType': args.env_type_index,
            'indexWeatherType': args.weather_type_index
        }
