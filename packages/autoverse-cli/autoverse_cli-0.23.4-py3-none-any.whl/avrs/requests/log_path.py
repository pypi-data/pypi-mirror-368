from avrs.requests.request import AvrsApiRequest

class LogPath(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'LogPath', 'Ego')
        psr = parser.add_parser('log-path', help='logs the path of the current vehicle so it can be used as' +
            ' an NPC profile')
        
        psr.add_argument('filename', help = 'the name of the file you want')
        psr.add_argument('time', type = float, help = 'the time in seconds you want to log the vehicle path. If you want to keep continously logging until'
            + ' end of simulation, enter -1')
        psr.add_argument('--filepath', nargs='?', help = 'By default the csv saves in your saved folder located in the simulator.' + 
            ' However if you would like to save to a new location, please provide an ABSOLUTE file path', default = None)
        psr.set_defaults(func=self.send_request)
    
    def get_request_body(self, args):
        if args.filepath == None:
            return {
                'Filename' : args.filename,
                'Time' : args.time,
                'AbsolutePath' : ""
            }
        else:
            return {
                'Filename' : args.filename,
                'Time' : args.time,
                'Path' : args.filepath
            }