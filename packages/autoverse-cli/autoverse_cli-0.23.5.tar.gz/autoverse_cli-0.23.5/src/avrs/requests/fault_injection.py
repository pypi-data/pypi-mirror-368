from avrs.requests.request import AvrsApiRequest
from argparse import RawDescriptionHelpFormatter
from argparse import RawTextHelpFormatter

class AvrsFaultInjectionRequests():
    def __init__(self, parser, cfg):
        psr = parser.add_parser('inject-fault', help='utilty to inject faults into components (sensors, actuators, etc)')
        sps = psr.add_subparsers(required= True, help='sub-command inject-fault')
        AvrsGnssFaultRequest(sps, cfg)
        AvrsLidarFaultRequest(sps, cfg)
        AvrsImuFaultRequest(sps, cfg)
        AvrsCanFaultRequest(sps, cfg)
    
def add_base_injection_args(psr):

    psr.add_argument(
        '--target',
        default='ego',
        help='the simulated object to apply the command to')

    psr.add_argument(
        '--duration',
        type=float,
        default=1.0,
        help='how long to apply the fault (0.0 is infinite)')

    psr.add_argument(
            '--dropout',
            action='store_true',
            help='if specified, will apply a complete dropout fault')

    psr.add_argument(
            '--freeze',
            action='store_true',
            help='if specified, will freeze the data (values will not change)')

class AvrsGnssFaultRequest(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'FaultInjection', '')

        psr = parser.add_parser(
            'gnss', 
            help='inject a gnss fault', 
            formatter_class=RawTextHelpFormatter)

        psr.add_argument(
            '--horizontal-bias',
            type=float,
            default=0.0,
            help='horizontal bias to apply to the sensor as a fault')

        psr.add_argument(
            '--vertical-bias',
            type=float,
            default=0.0,
            help='vertical bias to apply to the sensor as a fault')

        psr.add_argument(
            '--horizontal-stdev',
            type=float,
            default=0.0,
            help='horizontal standard deviation to apply to the sensor')

        psr.add_argument(
            '--vertical-stdev',
            type=float,
            default=0.0,
            help='vertical standard deviation to apply to the sensor')

        add_base_injection_args(psr)
        psr.set_defaults(func=self.send_request)

    def get_request_body(self, args):
        self.target_object_id = args.target
        self.verbose = args.verbose
        return {
            'faultType': 'GnssFault',
            'duration': args.duration,
            'bIsDropout': args.dropout,
            'bIsFreeze': args.freeze,
            'JsonBody': {
                'verticalBias': args.vertical_bias,
                'verticalStdev': args.vertical_stdev,
                'horizontalBias': args.horizontal_bias,
                'horizontalStdev': args.horizontal_stdev
            }
        }

class AvrsImuFaultRequest(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'FaultInjection', '')

        psr = parser.add_parser(
            'imu', 
            help='inject an imu fault', 
            formatter_class=RawTextHelpFormatter)

        psr.add_argument(
            '--bias',
            type=float,
            default=0.0,
            help='horizontal bias to apply to the sensor as a fault')

        psr.add_argument(
            '--stdev',
            type=float,
            default=0.0,
            help='horizontal standard deviation to apply to the sensor')

        add_base_injection_args(psr)
        psr.set_defaults(func=self.send_request)

    def get_request_body(self, args):
        self.target_object_id = args.target
        self.verbose = args.verbose
        return {
            'faultType': 'ImuFault',
            'duration': args.duration,
            'bIsDropout': args.dropout,
            'bIsFreeze': args.freeze,
            'JsonBody': {
                'bias': args.bias,
                'stdev': args.stdev
            }
        }

class AvrsLidarFaultRequest(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'FaultInjection', '')

        psr = parser.add_parser(
            'lidar', 
            help='inject a lidar fault', 
            formatter_class=RawTextHelpFormatter)

        psr.add_argument(
            '--point-density-reduction',
            type=float,
            default=0.5,
            help='the percent of point density reduction, where 1.0 drops all points')

        add_base_injection_args(psr)
        psr.set_defaults(func=self.send_request)

    def get_request_body(self, args):
        self.target_object_id = args.target
        self.verbose = args.verbose
        return {
            'faultType': 'LidarFault',
            'duration': args.duration,
            'bIsDropout': args.dropout,
            'bIsFreeze': args.freeze,
            'JsonBody': {
                'pointDensityReduction': args.point_density_reduction
            }
        }

class AvrsCanFaultRequest(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'FaultInjection', '')

        psr = parser.add_parser(
            'can', 
            help='inject a can', 
            formatter_class=RawTextHelpFormatter)

        psr.add_argument(
            'can_type',
            choices = ['bsu', 'badenia', 'kistler', 'all'],
            help='what type of the can interface you wish to apply the fault to')

        add_base_injection_args(psr)
        psr.set_defaults(func=self.send_request)

    def get_request_body(self, args):
        self.target_object_id = args.target
        self.verbose = args.verbose
        return {
            'faultType': 'CanFault',
            'duration': args.duration,
            'bIsDropout': True,
            'bIsFreeze': args.freeze,
            'JsonBody': {
                'canType': args.can_type
            }
        }