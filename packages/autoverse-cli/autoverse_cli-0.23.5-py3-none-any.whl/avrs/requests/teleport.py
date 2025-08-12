from avrs.requests.request import AvrsApiRequest

class Teleport(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'Teleport', "Ego")
        
        psr = parser.add_parser('teleport', 
            help='Teleports the car to the given x,y,z in either NED or LLA.')

        psr.add_argument('x', type=float, 
            help='new x position (NED meters) or latitude (if frame is set to LLA)')

        psr.add_argument('y', type=float, 
            help='new y position (NED meters) or longitude (if frame is set to LLA)')

        psr.add_argument('z', type=float, 
            help='new z position (NED meters) or altitude (if frame is set to LLA)')

        psr.add_argument('--yaw', type=float, default=0.0, 
            help='the yaw in degrees (0 north, + CW) to apply post teleport')

        psr.add_argument('--frame', choices=['LLA', 'ned'], default='ned', help='LLA or NED coordinate system.')

        psr.add_argument(
            '--object-name',
            default='ego',
            help='the simulated object to teleport')

        psr.set_defaults(func=self.send_request)


    def get_request_body(self, args):
        self.target_object_id = args.object_name
        return { 
            "X": args.x,
            "Y": args.y,
            "Z": args.z,
            "yaw": args.yaw,
            "NavFrame": args.frame 
        }