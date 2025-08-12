import subprocess
import base64
import logging
import time
from avrs.cfg import *
from avrs.race_cloud_util import *
from avrs.race_cloud_cfg_util import *
from avrs.race_cloud_fwd_api import *
from avrs.race_cloud_bridge_can import *
from avrs.util import *
from avrs.requests.request import AvrsApiRequest
from argparse import RawTextHelpFormatter

class AvrsRaceCloud(AvrsApiRequest):
    def __init__(self, parser, cfg):
        self.cfg = cfg
        race_cloud_parser = parser.add_parser(
            'race-cloud', 
            help='cloud racing\n\n')

        sps = race_cloud_parser.add_subparsers(required=True, help='race-cloud options')

        connect_parser = sps.add_parser(
            'connect',
            help='connect to an instance for cloud racing')
        connect_parser.add_argument(
            'sim_index',
            type = int,
            choices = [0, 1, 2, 3, 4, 5],
            help='the index of the simulator instance to connect to')
        connect_parser.add_argument(
            'team_name',
            help='the name of the team to race under')
        connect_parser.add_argument(
            'vehicle_config',
            help='the path the vehicle configuration file to use when racing')
        connect_parser.add_argument(
            '--instance-id',
            default = '',
            help='can be used directly instead of instance name if needed')
        connect_parser.add_argument(
            '--no-restart-sim',
            action='store_true',
            help='if set, the sim instance will not be restarted after connection')
        connect_parser.add_argument(
            '--no-check-cans',
            action='store_true',
            help='if set, vcan interfaces will not be checked for validity')
        connect_parser.add_argument(
            '--print-debug',
            action='store_true',
            help='if set, debug information will be printed')
        connect_parser.set_defaults(func=self.race_connect)

        rx_connect_parser = sps.add_parser(
            'rx-connection',
            help='execute steps to receive a connection (only relevant to sim-side)')
        rx_connect_parser.add_argument(
            'team_name',
            help='the name of the connecting team')
        rx_connect_parser.add_argument(
            'ip',
            help='the ip address of the incoming connection')
        rx_connect_parser.add_argument(
            '--restart',
            action='store_true',
            help='should the sim program be restarted after this connection')
        rx_connect_parser.add_argument(
            'cfg_data',
            help='the incoming vehicle configuration data')
        rx_connect_parser.set_defaults(func=self.rx_connect)

        sim_ctrl_parser = sps.add_parser(
            'sim-ctrl',
            help='control the sim program (start, stop, restart, reset)')
        sim_ctrl_parser.add_argument(
            'sim_index',
            type=int,
            choices=[0, 1, 2, 3, 4, 5],
            help='the index of the simulator instance to apply the action')
        sim_ctrl_parser.add_argument(
            'action',
            choices=['start', 'stop', 'restart', 'reset-connection', 'get-log'],
            help='what action to apply to the simulator program')
        sim_ctrl_parser.add_argument(
            '--local',
            action='store_true',
            help='if set, this command will run on this system locally (not for use from dev instances)')
        sim_ctrl_parser.add_argument(
            '--instance-id',
            default = '',
            help='can be used directly instead of sim index if needed')
        sim_ctrl_parser.add_argument(
            '--clear-autospawns',
            action='store_true',
            help='can be used with the reset-connection action to clear sim autospawn config')
        sim_ctrl_parser.set_defaults(func=self.sim_ctrl)

        reset_qos_parser = sps.add_parser(
            'reset-qos',
            help='reset the qos file on this system')
        reset_qos_parser.set_defaults(func=self.reset_qos)

        enable_peer_qos_parser = sps.add_parser(
            'enable-peer-qos',
            help='enable a peer in this systems qos file')
        enable_peer_qos_parser.add_argument(
            'peer_id',
            type=int,
            choices=[0, 1, 2, 3, 4, 5],
            help='the id of the peer to enable')
        enable_peer_qos_parser.add_argument(
            'ip',
            help='the ip address to add to the qos file')
        enable_peer_qos_parser.set_defaults(func=self.enable_peer_qos)

        disable_peer_qos_parser = sps.add_parser(
            'disable-peer-qos',
            help='disable a peer in this systems qos file')
        disable_peer_qos_parser.add_argument(
            'peer_id',
            type=int,
            choices=[0, 1, 2, 3, 4, 5],
            help='the id of the peer to enable')
        disable_peer_qos_parser.set_defaults(func=self.disable_peer_qos)

        fwd_server_parser = sps.add_parser(
            'fwd-api',
            help='forwards incoming external api requests to the simulator api')
        fwd_server_parser.add_argument(
            'mode',
            choices=['bg', 'fg'],
            help='whether to run in forground or background')
        fwd_server_parser.add_argument(
            'source_port',
            type=int,
            help='the external port to listen to external api requests on')
        fwd_server_parser.add_argument(
            'target_port',
            type=int,
            help='the local port to forward api requests too')
        fwd_server_parser.set_defaults(func=self.fwd_api)

        bridge_can_parser = sps.add_parser(
            'bridge-can',
            help='bridges a local vcan with a remote vcan over udp')

        bridge_can_parser.add_argument(
            'mode',
            choices=['bg', 'fg'],
            help='whether to run in forground or background')

        bridge_can_parser.add_argument(
            'vcan_name')

        bridge_can_parser.add_argument(
            'peer_ip')

        bridge_can_parser.add_argument(
            'peer_port',
            type=int)

        bridge_can_parser.add_argument(
            'local_port',
            type=int)

        bridge_can_parser.set_defaults(func=self.bridge_can)

    def race_connect(self, args):
        logger = logging.getLogger('avrs')

        # make api call to begin connection
        our_ip = get_local_instance_ip()

        if our_ip == '127.0.0.1':
            print('this machines IP was returned as localhost. was this run on the cloud instance?')
            return

        logger.info('starting race-cloud connect for team {} to instance {}'.format(
            args.team_name, args.sim_index))
        print('connecting to race with team name: {}'.format(args.team_name))

        if args.no_restart_sim:
            print('the simulator will NOT be restarted automatically after this connection')
        else:
            print('the simulator WILL be restarted automatically after this connection')

        # reset local connection first
        logger.info('resetting local connection state prior to connection')
        reset_race_cloud_connection()

        # validate / load vehicle config
        vcfg_ok, vcfg_data, bsu_vcan, kistler_vcan, badenia_vcan = prepare_vehicle_cfg(args.vehicle_config)

        if not vcfg_ok:
            print('error reading config file: {}'.format(vcfg_data))
            return

        print('creating vcan interfaces found in config locally: {}, {}, {} (if they do not exist)'.format(
            bsu_vcan, kistler_vcan, badenia_vcan))

        setup_vcans(bsu_vcan, kistler_vcan, badenia_vcan)

        vcan_ok = True
        if not check_vcan_exists(bsu_vcan) and not args.no_check_cans:
            print('bsu vcan {} does not appear to exist'.format(bsu_vcan))
            vcan_ok = False
        if not check_vcan_exists(kistler_vcan) and not args.no_check_cans:
            print('kistler vcan {} does not appear to exist'.format(kistler_vcan))
            vcan_ok = False
        if not check_vcan_exists(badenia_vcan) and not args.no_check_cans:
            print('badenia vcan {} does not appear to exist'.format(badenia_vcan))
            vcan_ok = False

        if not vcan_ok:
            return

        connection_request = {
            'action': 'connect',
            'sim_index': args.sim_index,
            'ip_to_reserve': our_ip,
            'team_name': args.team_name,
            'sim_id_override': args.instance_id,
            'ensure_instance_is_running': False,
            'should_restart_sim_program': not args.no_restart_sim,
            'config_data': vcfg_data
        }

        ok, response = call_race_cloud_api(connection_request)
        if not ok:
            print('connect api error: {}'.format(response))

        ok, rbody, sim_ip = get_api_script_response(response)
        if not ok:
            print(rbody)
            return

        if args.print_debug:
            print(rbody)
        #print(sim_ip)

        slot_info = {}
        for k, v in rbody.items():
            #print('out: {}'.format(v['stdout']))
            #print('err: {}'.format(v['stderr']))
            slot_info = json.loads(v['stdout'])

        if not slot_info['ok']:
            print('issue reserving slot: {}'.format(slot_info['msg']))
            return

        extra_msg = slot_info.get('extra_msg', '')
        print(extra_msg)

        sim_slot = slot_info['slot']

        # enable first peer since this is on a client (only will ever have 1, the sim)
        enable_peer_qos(sim_slot, sim_ip)

        # will need to get port from received slot id to connect peer vcans
        connect_peer_vcan(sim_slot, sim_ip, 0, bsu_vcan)
        connect_peer_vcan(sim_slot, sim_ip, 1, kistler_vcan)
        connect_peer_vcan(sim_slot, sim_ip, 2, badenia_vcan)

        # configure the CLI to communicate with the cloud sim instance
        self.cfg['sim_address'] = sim_ip
        self.cfg['sim_api_port'] = 30333 # set this to the forwarding server running on sim instance
        logger.info('setting sim addr to {} and port to {} for future api requests'.format(sim_ip, 30333))
        save_cfg('avrs', self.cfg)

        print('connection success with team name {} and slot id {}'.format(args.team_name, sim_slot))

        # if sim slot is not 0, which means domain id is not 0, notify user
        if sim_slot != 0:
            print('your ROS2 interfaces will be available on ROS_DOMAIN_ID {}'.format(sim_slot))
            print('you will need to set the ROS_DOMAIN_ID environment variable prior to echoing or running software')
            print('(eg \"export ROS_DOMAIN_ID={}\")'.format(sim_slot))

    # this should only run on sim instances (not dev instances)
    def rx_connect(self, args):
        logger = logging.getLogger('avrs')

        extra_msg = ''

        # check time-since last connection here. if > 10mins auto reset connection state
        time_since_last_connection = self.get_and_update_time_since_last_connection()
        reset_connection_timeout = 3600.0
        if time_since_last_connection > 3600.0:
            logger.info('time since last connection rx {} > {}. resetting connection'.format(
                time_since_last_connection, reset_connection_timeout))
            clear_autospawns()
            reset_race_cloud_connection()
            extra_msg += 'automatically resetting simulation instance connection state'
            extra_msg += ' (last connection was > {} seconds ago)'.format(reset_connection_timeout)
        else:
            extra_msg += 'NOT resetting connection state. last connection was only {} seconds ago'.format(
                time_since_last_connection)

        logger.info('rx race cloud connection for team {} with ip {}'.format(args.team_name, args.ip))
        ok, msg, slot = try_get_open_slot(args.team_name, args.ip)

        bsu_vcan = get_auto_vcan_name(slot, 0)
        kistler_vcan = get_auto_vcan_name(slot, 1)
        badenia_vcan = get_auto_vcan_name(slot, 2)

        # get CAN names from this
        register_received_vehicle(
            args.team_name, slot, args.cfg_data, bsu_vcan, kistler_vcan, badenia_vcan)

        vcan_ok = True
        vcan_msg = ''
        if not check_vcan_exists(bsu_vcan):
            vcan_msg = 'bsu vcan {} does not appear to exist'.format(bsu_vcan)
            vcan_ok = False
        if not check_vcan_exists(kistler_vcan):
            vcan_msg = 'kistler vcan {} does not appear to exist'.format(kistler_vcan)
            vcan_ok = False
        if not check_vcan_exists(badenia_vcan):
            vcan_msg = 'badenia vcan {} does not appear to exist'.format(badenia_vcan)
            vcan_ok = False

        if not vcan_ok:
            print(json.dumps({
                'ok': vcan_ok,
                'msg': vcan_msg,
                'slot': -1
                }))
            return

        if ok:
            logger.info('enabling qos for slot {} with ip {}'.format(slot, args.ip))
            enable_peer_qos(slot, args.ip)
            logger.info('connecting vcans for incoming connection')
            out = connect_peer_vcan(slot, args.ip, 0)
            logger.info('connected first vcan result: {} {}'.format(out.out, out.err))
            out = connect_peer_vcan(slot, args.ip, 1)
            logger.info('connected second vcan result: {} {}'.format(out.out, out.err))
            out = connect_peer_vcan(slot, args.ip, 2)
            logger.info('connected third vcan result: {} {}'.format(out.out, out.err))

        # go ahead and restart forwarding script here
        # stop it if its already running
        stop_result = stop_fwd_api()
        logger.info('stopped fwd-api: {}'.format(stop_result))
        start_result = start_fwd_api(30333, 30313)
        logger.info('started fwd-api: {}'.format(start_result))

        if args.restart:
            logger.info('restarting sim program for new connection')
            logger.info('stopping sim program on sim instance')
            bash_kill_process('Autoverse')
            logger.info('starting sim program on sim instance')
            exe_path = os.path.join(get_sim_exe_path())
            start_exe(exe_path)
            extra_msg += '\n' if len(extra_msg) > 0 else ''
            extra_msg += 'automatically restarting sim program on sim instance'
        else:
            logger.info('--restart not specified, not restarting sim program for this connection')

        response = {
            'ok': ok,
            'msg': msg,
            'slot': slot,
            'extra_msg': extra_msg
        }

        print(json.dumps(response)) # print this so that when called from the ssh lambda we can get the result

    def sim_ctrl(self, args):
        if args.local:
            self.local_sim_ctrl(args)
        else:
            self.remote_sim_ctrl(args)

    def local_sim_ctrl(self, args):
        logger = logging.getLogger('avrs')
        if args.action == 'reset-connection':
            logger.info('resetting local race-cloud connection states')
            print('resetting race cloud connection')
            print('resetting qos file, removing CAN lock files, stopping all cannelloni instances')
            reset_race_cloud_connection()
            if args.clear_autospawns:
                clear_autospawns()
        if args.action == 'stop' or args.action == 'restart':
            logger.info('stopping race-cloud simulator program')
            print('stopping sim program on sim instance')
            bash_kill_process('Autoverse')
        if args.action == 'start' or args.action == 'restart':
            logger.info('starting race-cloud simulator program')
            #print('starting sim program on sim instance')
            exe_path = os.path.join(get_sim_exe_path())
            start_exe(exe_path)
        if args.action == 'get-log':
            logger.info('getting connection log')
            log_path = os.path.join(get_cfg_dir('avrs'), 'avrs.log')
            if os.path.isfile(log_path):
                print('the get-log command has been deprecated')
                #with open(log_path, 'r', encoding='utf-8') as f:
                    #print('the get-log command has been deprecated')
                    #print(f.read())
            else:
                print('no log file found')


    def remote_sim_ctrl(self, args):
        logger = logging.getLogger('avrs')

        # go ahead and reset local connection as well
        if args.action == 'reset-connection':
            reset_race_cloud_connection()

        our_ip = get_local_instance_ip()

        reset_request = {
            'action': args.action,
            'sim_index': args.sim_index,
            'ip_to_reserve': our_ip,
            'sim_id_override': args.instance_id,
            'ensure_instance_is_running': False
        }

        logger.info('sending race-clolud sim-ctrl request: {}'.format(reset_request))

        ok, response = call_race_cloud_api(reset_request)
        #print(response)
        if not ok:
            print(response)
            return

        ok, rbody, sim_ip = get_api_script_response(response)
        if not ok:
            print(rbody)
            return

        for k, v in rbody.items():
            print(v['stdout'])

    def reset_qos(self, args):
        print('resetting qos file')
        reset_rmw_qos()

    def enable_peer_qos(self, args):
        print('enabling peer qos for id {} using ip address {}'.format(
            args.peer_id, args.ip))
        out = enable_peer_qos(args.peer_id, args.ip)
        print('{} {}'.format(out.out, out.err))

    def disable_peer_qos(self, args):
        print('disabling peer qos for id {}'.format(args.peer_id))
        out = disable_peer_qos(args.peer_id)
        print('{} {}'.format(out.out, out.err))

    def fwd_api(self, args):
        # start a server that listens for http on some port and forwards
        # to the simulator on 30313
        logger = logging.getLogger('avrs')

        if args.mode == 'bg':
            # call the cli so that it starts the forwarding server in the background
            # stop it if its already running
            try:
                stop_result = stop_fwd_api()
                logger.info('stopped fwd-api: {}'.format(stop_result))
                start_result = start_fwd_api(args.source_port, args.target_port)
                logger.info('started fwd-api: {}'.format(start_result))
            except Exception as e:
                logger.error('failed to restart fwd-api: {}'.format(e))

        else:
            logger.info('starting fwd-api in forground')
            handler = ApiForwardHandler(args.target_port)
            server = HTTPServer(('0.0.0.0', args.source_port), handler)
            server.serve_forever()

    def test_reset_timeout(self, args):
        print('testing reset timeout')

        elapsed = self.get_and_update_time_since_last_connection()
        print('elasped: {}'.format(elapsed))

    def get_and_update_time_since_last_connection(self):
        t = time.time()
        # default to zero if not exist to force timeout
        last_time = self.cfg.get('race-cloud-last-connect-time', 0)
        elapsed = t - last_time
        self.cfg['race-cloud-last-connect-time'] = t
        save_cfg('avrs', self.cfg)
        return elapsed

    def bridge_can(self, args):
        logger = logging.getLogger('avrs')

        if args.mode == 'bg':
            # call the cli so that it starts the forwarding server in the background
            # stop it if its already running
            try:
                stop_result = stop_can_brdige()
                logger.info('stopped can bridge: {}'.format(stop_result))
                start_result = start_can_bridge(args)
                logger.info('started can bridge: {}'.format(start_result))
            except Exception as e:
                logger.error('failed to restart can bridge: {}'.format(e))

        else:
            logger.info('starting can bridge in forground')
            can_bridge_loop(args)