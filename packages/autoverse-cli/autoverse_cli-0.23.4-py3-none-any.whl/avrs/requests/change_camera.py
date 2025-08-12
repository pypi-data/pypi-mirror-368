from avrs.requests.request import AvrsApiRequest

class AvrsChangeCameraRequest(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'ChangeCamera', '')
        psr = parser.add_parser('change-camera', help='changes the active camera on an object')

        psr.add_argument(
            'object_name',
            metavar='object-name',
            help='the specific object to change cameras on')

        psr.add_argument(
            '--activate-pixel-stream',
            action="store_true",
            help='if true, a pixel stream will be created for the object')

        psr.set_defaults(func=self.send_request)

    def get_request_body(self, args):
        return {
            "pixelStreamObjectId": args.object_name,
            "bActivatePixelStream": args.activate_pixel_stream
        }
