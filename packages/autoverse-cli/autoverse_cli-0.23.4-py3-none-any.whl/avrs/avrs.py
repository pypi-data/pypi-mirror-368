#!/usr/bin/env python3
import logging
import argparse
from argparse import RawDescriptionHelpFormatter
from argparse import RawTextHelpFormatter

from avrs.app_version import *
from avrs.cfg import *
from avrs.launcher import *
from avrs.can_tool import *
from avrs.race_cloud import *
from avrs.argparse_help import *

from avrs.requests.move_to_landmark import MoveToLandmarkRequest
from avrs.requests.restart import Restart
from avrs.requests.reset_to_track import ResetToTrack
from avrs.requests.teleport import Teleport
from avrs.requests.npc import Npc
from avrs.requests.vd import Vd
from avrs.requests.vehicle_input import AvrsConfigureVehicleInputRequest
from avrs.requests.log_path import LogPath
from avrs.requests.demo import AvrsDemoRequest
from avrs.requests.environment import *
from avrs.requests.code_booz import *
from avrs.requests.vehicle_replay import *
from avrs.requests.scenario_control import *
from avrs.requests.list_sim_objects import *
from avrs.requests.fault_injection import *
from avrs.requests.change_camera import *
from avrs.requests.toggle_hud import * 
from avrs.requests.race_control import *
from avrs.simconfig import *
from avrs.requests.get_object_config import *
from avrs.requests.misc import *
from avrs.requests.spawn_object import *
from avrs.requests.dump_sim_config import *
from avrs.requests.leaderboard import AvrsLeaderboardRequest

def get_version():
    return get_app_version()

def init_logging():
    max_log_size = 1024 * 512
    log_path = os.path.join(get_cfg_dir('avrs'), 'avrs.log')
    verbose_log_path = os.path.join(get_cfg_dir('avrs'), 'avrs_verbose.log')

    if os.path.exists(verbose_log_path) and os.path.getsize(verbose_log_path) > max_log_size:
            os.remove(verbose_log_path)
    if os.path.exists(log_path) and os.path.getsize(log_path) > max_log_size:
        os.remove(log_path)

    logging.basicConfig(filename=verbose_log_path,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

    # When testing, prevent multiple handler additions to global logging objects
    if 'avrs' in logging.Logger.manager.loggerDict:
        #self.logger = logging.getLogger('alvs')
        del logging.Logger.manager.loggerDict['avrs']
        #return
    logger = logging.getLogger('avrs')
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    file_handler.setFormatter(formatter)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    logger.addHandler(file_handler)
    #logger.addHandler(console)

def main():

    # logging will fail in pipeline
    try:
        init_logging()
    except Exception as e:
        pass

    parser = argparse.ArgumentParser(
            prog='avrs', 
            description='Autoverse CLI',
            epilog='',
            formatter_class=RawTextHelpFormatter)

    version_psr = parser.add_argument(
            '--version', 
            help='show the cli version', 
            action='version', 
            version=get_version())

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='request verbose output')

    sps = parser.add_subparsers(required=True, help='sub-command help')

    cfg = load_cfg('avrs')
    check_app_is_latest()

    AvrsLauncher(sps, cfg)


    MoveToLandmarkRequest(sps, cfg)
    Restart(sps, cfg)
    ResetToTrack(sps, cfg)
    Teleport(sps, cfg)
    #Npc(sps, cfg)
    AvrsRaceCloud(sps, cfg)
    Vd(sps, cfg)
    AvrsConfigureVehicleInputRequest(sps, cfg)
    LogPath(sps, cfg)
    AvrsEnvironmentRequests(sps, cfg)
    AvrsCodeBoozRequest(sps, cfg)
    AvrsVehicleReplayRequests(sps, cfg)
    AvrsCanTool(sps, cfg)
    AvrsSimConfig(sps, cfg)
    AvrsScenarioRequests(sps, cfg)
    AvrsListSimObjectsRequest(sps, cfg)
    AvrsLeaderboardRequest(sps, cfg)
    AvrsFaultInjectionRequests(sps, cfg)
    AvrsChangeCameraRequest(sps, cfg)
    AvrsToggleHudRequest(sps, cfg)
    AvrsGetObjectConfigRequest(sps, cfg)
    AvrsGetSimVersionRequest(sps, cfg)
    AvrsGetSessionIdRequest(sps, cfg)
    AvrsGetExitSimRequest(sps, cfg)
    AvrsPingRequest(sps, cfg)
    AvrsConfigureSimLodRequest(sps, cfg)
    AvrsSpawnObjectRequest(sps, cfg)
    AvrsDumpSimConfigRequest(sps, cfg)
    AvrsRaceControlRequest(sps, cfg)
    AvrsSetEnvironmentRequest(sps, cfg)

    # new api requests
    AvrsDescribeSimRestRequest(sps, cfg)

    if os.environ.get('AVRS_WITH_DEMO', '0') == '1':
        AvrsDemoRequest(sps, cfg)

    if os.environ.get('AVRS_GEN_DOCS', '0') == '1':
        generate_argparse_docs(parser)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()