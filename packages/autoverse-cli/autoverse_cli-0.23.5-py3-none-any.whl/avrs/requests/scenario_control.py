from avrs.requests.request import AvrsApiRequest
from argparse import RawDescriptionHelpFormatter
from argparse import RawTextHelpFormatter

class AvrsScenarioRequests():
    def __init__(self, parser, cfg):
        psr = parser.add_parser('scenario', help='commands related to scenarios in the simulator')
        sps = psr.add_subparsers(required= True, help='sub-command scenario')
        StartScenarioRequest(sps, cfg)
        StopScenarioRequest(sps, cfg)

class StartScenarioRequest(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'ScenarioControl', '')
        psr = parser.add_parser(
            'start', help='start a scenario', formatter_class=RawTextHelpFormatter)

        psr.add_argument(
            'scenario_name', 
            default='', 
            help='the name of the scenario to start')
        
        psr.set_defaults(func=self.send_request)
    

    def get_request_body(self, args):
        return {
            'scenarioName': args.scenario_name,
            'action': 'start'
        }

class StopScenarioRequest(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'ScenarioControl', '')
        psr = parser.add_parser(
            'stop', help='stop any active scenarios', formatter_class=RawTextHelpFormatter)

        psr.set_defaults(func=self.send_request)

    def get_request_body(self, args):
        return {
            'action': 'stop'
        }