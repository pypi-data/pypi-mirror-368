from avrs.requests.request import AvrsApiRequest

class AvrsConfigureVehicleInputRequest(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'ConfigureVehicleInput', 'Ego')
        psr = parser.add_parser(
            'configure-vehicle-input', 
            help='Allows different input modes to be set for a vehicle')

        psr.add_argument(
            'input_mode', 
            default='None', 
            choices=['None', 'Keyboard', 'WheelAndPedals', 'CAN'], 
            help='the type of input mode to set')

        psr.set_defaults(func=self.send_request)

    def get_request_body(self, args):
        return {
            "InputMode": args.input_mode
        }