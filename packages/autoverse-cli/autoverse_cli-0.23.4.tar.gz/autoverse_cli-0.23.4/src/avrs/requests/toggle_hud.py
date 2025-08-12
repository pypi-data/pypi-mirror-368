from avrs.requests.request import AvrsApiRequest

class AvrsToggleHudRequest(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'ToggleHud', 'Ego')
        psr = parser.add_parser('toggle-hud', help='toggles the HUD on or off')
        psr.set_defaults(func=self.send_request)

    def get_request_body(self, args):
        return {
        }
