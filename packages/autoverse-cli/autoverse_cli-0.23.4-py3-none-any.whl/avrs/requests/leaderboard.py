from avrs.requests.request import AvrsApiRequest

class AvrsLeaderboardRequest():
    def __init__(self, parser, cfg):
        psr = parser.add_parser('leaderboard', help='utilities for leaderboard management')
        sps = psr.add_subparsers(required= True, help='sub-command of leaderboard')
        ToggleLeaderboard(sps, cfg)
        ChronoLeaderboard(sps, cfg)
        LapsLeaderboard(sps, cfg)
        ResetLeaderboard(sps, cfg)

class ToggleLeaderboard(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'ToggleLeaderboard', '')
        psr = parser.add_parser('toggle', help='Toggles the leaderboard on or off')

        psr.set_defaults(func=self.send_request)
    
    def get_request_body(self, args):
        self.target_object_id = ''
        return {
        }
    
class ChronoLeaderboard(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'ChronoLeaderboard', '')
        psr = parser.add_parser('chrono', help='Displays some options for the chrono in free practice and qualifying')
        
        group = psr.add_mutually_exclusive_group()
        group.add_argument('--start', action='store_true', help="Start the timer")
        group.add_argument('--stop', action='store_true', help="Stop the timer")
        group.add_argument('--reset', action='store_true', help="Reset the timer to its initial value")

        psr.add_argument('--set', type=int, help="Set a new initial value for the timer")

        psr.set_defaults(func=self.send_request)
    
    def get_request_body(self, args):
        self.target_object_id = ''
        return {
            'Start': args.start,
            'Stop': args.stop,
            'Reset': args.reset,
            'Set': args.set
        }
    
class LapsLeaderboard(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'LapsLeaderboard', '')
        psr = parser.add_parser('set-laps', help='Set the number of laps to complete the race')

        psr.add_argument('laps', type=int, help='Number of laps')

        psr.set_defaults(func=self.send_request)
    
    def get_request_body(self, args):
        self.target_object_id = ''
        return {
            'Laps': args.laps
        }
    
class ResetLeaderboard(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'ResetLeaderboard', '')
        psr = parser.add_parser('reset', help='Reset all the leaderboard data')

        psr.set_defaults(func=self.send_request)
    
    def get_request_body(self, args):
        self.target_object_id = ''
        return {
        }
    
    