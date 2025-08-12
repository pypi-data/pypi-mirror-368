from avrs.requests.request import AvrsApiRequest
import can
import cantools
import time
import os
import datetime

from avrs.cfg import *
from avrs.can_tool_util import *

class AvrsCanTool():
    def __init__(self, parent_parser, cfg):
        self.cfg = cfg
        can_tool_parser = parent_parser.add_parser(
            'can-tool', 
            help='provides CAN utilities (echo certain signals, etc)\n\n')
        sps = can_tool_parser.add_subparsers(required=True, help='can-tool options')

        add_dbc_parser = sps.add_parser(
            'add-dbc', 
            help='save a dbc file to be used with other commands')
        add_dbc_parser.add_argument(
            'dbc_file_path', 
            help='the path to the dbc file to add')
        add_dbc_parser.add_argument(
            '--overwrite-ok',
            action='store_true',
            help='is it ok to overwrite an existing file')
        add_dbc_parser.set_defaults(func=self.add_dbc)

        list_dbc_parser = sps.add_parser(
            'list-dbc', 
            help='list the dbc files that are known to avrs')
        list_dbc_parser.set_defaults(func=self.list_dbc)

        echo_parser = sps.add_parser(
            'echo', 
            help='echos CAN messages')
        echo_parser.add_argument(
            'can_names',
            nargs='+',
            help='the names of the CAN interfaces, eg "vcan0 vcan1" etc')
        echo_parser.add_argument(
            '--dbc_names',
            nargs='+',
            default='',
            help='the names or indeces of a cached dbc files or path to existing dbc files to use')
        echo_parser.add_argument(
            '--isolate',
            nargs='+',
            default='',
            help='a list of specific signal to echo, ignoring other signals')
        echo_parser.add_argument(
            '--duration',
            type=float,
            default=1.0,
            help='the duration to echo can')
        echo_parser.add_argument(
            '--rates',
            action='store_true',
            help='echo the rates for messages instead of their values')
        echo_parser.add_argument(
            '--save-report-as',
            default='',
            help='if set along with the "--rates" flag, will save results to a json file')
        echo_parser.set_defaults(func=self.echo)

        eav_input_parser = sps.add_parser(
            'send-eav24-input',
            help='send some simple input (throttle, brake, steer etc) to an eav24 over CAN')
        eav_input_parser.add_argument(
            'can_name',
            help='the name of the CAN interface, eg "vcan0"')
        eav_input_parser.add_argument(
            'dbc_name',
            help='the name or index of a cached dbc file or path to existing dbc file to use')
        eav_input_parser.add_argument(
            '--throttle',
            type=float,
            default=0.0,
            help='throttle to send 0 -> 1.0')
        eav_input_parser.add_argument(
            '--gear',
            type=int,
            default=0,
            help='gear to send')
        eav_input_parser.add_argument(
            '--brake',
            type=float,
            default=0.0,
            help='brake to send 0 -> 1.0')
        eav_input_parser.add_argument(
            '--steer',
            type=float,
            default=0.0,
            help='steer to send -24 -> 24')
        eav_input_parser.add_argument(
            '--duration',
            type=float,
            default=1.0,
            help='the duration to send the command can')
        eav_input_parser.set_defaults(func=self.eav_input)

        test_latency_parser = sps.add_parser(
            'test-eav24-bsu-latency', 
            help='test the latency in the EAV24 BSU CAN interface by waiting for command ACK')
        test_latency_parser.add_argument(
            'can_name',
            help='the name of the CAN interface, eg "vcan0"')
        test_latency_parser.add_argument(
            'dbc_name',
            help='the name or index of a cached dbc file or path to existing dbc file to use')
        test_latency_parser.add_argument(
            '--nsamples',
            type=int,
            default=5,
            help='the number of samples to test')
        test_latency_parser.add_argument(
            '--duration',
            type=float,
            default=1.0,
            help='the duration to send each command can to wait for a given ack')
        test_latency_parser.add_argument(
            '--send-rate-hz',
            type=float,
            default=50,
            help='the rate in hz to send messages to wait for a given ack')
        test_latency_parser.add_argument(
            '--save-report-as',
            default='',
            help='if set will save results to a json file with this name')

        test_latency_parser.set_defaults(func=self.test_eav24_latency)


    def add_dbc(self, args):
        ok, status = add_cached_file(
            'avrs', 'dbc', args.dbc_file_path, args.overwrite_ok)
        print(status)

    def list_dbc(self, args):
        files = get_cached_file_list('avrs', 'dbc')
        s = ''
        for i in range(len(files)):
            s += '({}) {} \n'.format(i, files[i])
        print(s) if len(files) > 0 else print('(empty)')

    def echo(self, args):
        dbcs = self.get_dbcs(args.dbc_names)
        print('echoing {} using {} dbcs'.format(args.can_names, len(dbcs)))
        if len(dbcs) > 0:
            echo_can(args.can_names, dbcs, args.duration, args.isolate, args.rates, args.save_report_as)
        else:
            print('unable to echo can (dbc or can name error)')

    def eav_input(self, args):
        dbcs = self.get_dbcs([args.dbc_name])
        if len(dbcs) > 0:
            send_eav24_can_values(
                args.can_name, dbcs[0], args.throttle, args.gear, args.brake, args.steer, args.duration)
        else:
            print('unable to echo can (dbc or can name error)')

    def test_eav24_latency(self, args):
        dbcs = self.get_dbcs([args.dbc_name])
        if len(dbcs) > 0:
            test_eav24_can_latency(
                args.can_name, dbcs[0], args.nsamples, args.send_rate_hz, args.duration, args.save_report_as)
        else:
            print('unable to echo can (dbc or can name error)')

    def get_dbcs(self, dbc_names):
        dbcs = []
        # If default, find all dbcs and return them
        if dbc_names == '':
            for d in get_cached_file_list('avrs', 'dbc'):
                ok, cache_path = get_cached_file('avrs', 'dbc', d)
                if ok:
                    dbcs.append(cantools.database.load_file(cache_path))
                else:
                    print(cache_path)
        else:
            for d in dbc_names:
                if os.path.isfile(d):
                    dbc = cantools.database.load_file(d)
                else:
                    ok, cache_path = get_cached_file('avrs', 'dbc', d)
                    if ok:
                        dbcs.append(cantools.database.load_file(cache_path))
                    else:
                        print(cache_path)
        return dbcs
