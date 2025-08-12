import random
from avrs.requests.request import AvrsApiRequest
from argparse import RawDescriptionHelpFormatter
from argparse import RawTextHelpFormatter

class AvrsVehicleReplayRequests():
    def __init__(self, parser, cfg):
        psr = parser.add_parser('vehicle-replay', help='utilty for recording and replaying vehicle motion')
        sps = psr.add_subparsers(required= True, help='sub-command vehicle-replay')
        SpawnReplayVehicle(sps, cfg)
        StartVehicleReplayRecording(sps, cfg)
        StopVehicleReplayRecording(sps, cfg)
        DespawnReplayVehicle(sps, cfg)
        SpawnVehicleReplayGroup(sps, cfg)

class SpawnReplayVehicle(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'SpawnObject', '')
        psr = parser.add_parser(
            'spawn', help='spawn a vehicle intended to replay motion', formatter_class=RawTextHelpFormatter)

        psr.add_argument(
            'replay_file', 
            default='', 
            help='the replay file to use ("random" for a random profile)')

        psr.add_argument(
            '--name', 
            default='', 
            help='name of the replay vehicle to spawn')

        psr.add_argument(
            '--vehicle-type', 
            default='EAV24', 
            help='what type of vehicle to spawn for replay')

        # psr.add_argument(
        #     '--position', 
        #     choices=('relative', 'absolute'), 
        #     default='absolute', 
        #     help=NPC_SPAWN_POSITION_HELP)


        # psr.add_argument(
        #     '--velocity-type', 
        #     default='constant', 
        #     help='the path the NPC follows is a constant velocity or speed')

        # psr.add_argument(
        #     '--speed', 
        #     type=float, 
        #     default=20, 
        #     help='the speed of the npc is m/s')

        psr.add_argument(
            '--rate', 
            type=float, 
            default=1.0, 
            help='the playback rate, 1.0 is normal')

        psr.add_argument(
            '--random-start',
            action='store_true',
            help='if set, will start at a random point in the replay')

        psr.add_argument(
            '--relative-dist', 
            type=float, 
            default=40.0, 
            help='the distance relative to ego to start the playback (-1 to start at playback start)')

        psr.add_argument(
            '--auto-start',
            action='store_true',
            help='if set, the npc will begin moving immediately')

        psr.add_argument(
            '--count',
            type=int,
            default=1,
            help='the number of npcs to spawn (only works with automatic name)')

        psr.add_argument(
            '--group-name',
            default="",
            help="if specified, all vehicles will begin recording with the given group name")

        psr.add_argument(
            '--enable-front-lidar',
            action='store_true',
            help='if set, will enable the front lidar on the replay vehicle')

        psr.add_argument(
            '--enable-left-lidar',
            action='store_true',
            help='if set, will enable the left lidar on the replay vehicle')

        psr.add_argument(
            '--enable-right-lidar',
            action='store_true',
            help='if set, will enable the right lidar on the replay vehicle')

        # psr.add_argument(
        #     '--enable-sensors', 
        #     type=bool, 
        #     default=False, 
        #     help='whether to enable sensors on the replay vehicle')

        psr.add_argument(
            '--with-view-cameras',
            action='store_true',
            help='if set, will attach viewing cameras to the replay vehicle')
        
        psr.set_defaults(func=self.send_request)
    
    def send_request(self, args):
        for i in range(args.count):
            self.send_http_request(args)

    def get_request_body(self, args):

        replay_ipd = {
            'bEnableRecording': False,
            'bRecordOnPhysicsTick': False,
            'recordMotionMinSpeedThreshold': 0.01,
            'bEnableReplay': True,
            'bApplyInitialConfig': True,
            'initialConfig': {
                'playRate': args.rate,
                'profile': args.replay_file,
                'bUseRandomProfile': args.replay_file == 'random',
                'replayAction': 'start' if args.auto_start else '',
                'bStartReplayAtRandomTime': args.random_start,
                'relativeDistance': args.relative_dist,
                'bRecordAllVehiclesAsGroup': args.group_name != "",
                'RecordingGroupName': args.group_name
            }
        }

        eav_init_pld = {
            "bEnablePrimaryCan": False,
            "bEnableSecondaryCan": False,
            "bEnableBadeniaCan": False,
            "bHudEnabled": False,
            "bLidarEnabled": True,
            "bCameraEnabled": False,
            "bPublishInputs": False,
            "bPublishGroundTruth": False
        }

        lidar_front_pld = {
            'componentConfig': {
                'instanceName': 'lidar_front'
            },
            'sensorDesc': {
                'frame': 'lidar_front',
                'leverarm': {
                    'translation': {
                        'x': 85,
                        'y': 0,
                        'z': 73
                    },
                    'translationUnits': 'centimeters',
                    'rotation': {
                        'pitch': 0,
                        'yaw': 0,
                        'roll': 0
                    },
                    'rotationUnits': 'degrees'
                },
                'dataStream': {
                    'streamName': 'lidar_front/points',
                    'rateHz': 15
                }
            }
        }

        lidar_left_pld = {
            'componentConfig': {
                'instanceName': 'lidar_left'
            },
            'sensorDesc': {
                'frame': 'lidar_left',
                'leverarm': {
                    'translation': {
                        'x': 15,
                        'y': -20,
                        'z': 82
                    },
                    'translationUnits': 'centimeters',
                    'rotation': {
                        'pitch': 0,
                        'yaw': 240,
                        'roll': 0
                    },
                    'rotationUnits': 'degrees'
                },
                'dataStream': {
                    'streamName': 'lidar_left/points',
                    'rateHz': 15
                }
            }
        }

        lidar_right_pld = {
            'componentConfig': {
                'instanceName': 'lidar_right'
            },
            'sensorDesc': {
                'frame': 'lidar_right',
                'leverarm': {
                    'translation': {
                        'x': 15,
                        'y': 20,
                        'z': 82
                    },
                    'translationUnits': 'centimeters',
                    'rotation': {
                        'pitch': 0,
                        'yaw': 120,
                        'roll': 0
                    },
                    'rotationUnits': 'degrees'
                },
                'dataStream': {
                    'streamName': 'lidar_right/points',
                    'rateHz': 15
                }
            }
        }

        world_label_pld = {
            "typeName": "WorldTextComponent",
            "bEnabled": True,
            "body": {
                "bUseObjectName": False,
                "defaultString": "",
                "fontSize": 34,
                "offsetCm": {
                    "x": 0,
                    "y": 0,
                    "z": 150
                }
            }
        }

        plds = [
            {
                'typeName': 'WheeledVehicleReplayIpd',
                'body': replay_ipd
            },
            {
                'typeName': 'Eav24Initializer',
                'body': eav_init_pld
            },
            {
                'typeName': 'GenericLidarIpd',
                'bEnabled': args.enable_front_lidar,
                'body': lidar_front_pld
            },
            {
                'typeName': 'GenericLidarIpd',
                'bEnabled': args.enable_left_lidar,
                'body': lidar_left_pld
            },
            {
                'typeName': 'GenericLidarIpd',
                'bEnabled': args.enable_right_lidar,
                'body': lidar_right_pld
            },
            world_label_pld
        ]

        if args.with_view_cameras:
            plds.append(
                {
                    'typeName': 'InitializerTemplates',
                    'body': {
                        'templates': [
                            {
                                'payloadType': 'SimViewTargetIpd',
                                'payloadSpec': 'DefaultCarCams'
                            }
                        ]
                    }
                })

        # Create time based name if not specified
        name = args.name
        if name == '':
            name = 'npc_{}'.format(random.randint(0, 100000))

        return {
            'Name': name,
            'Type': args.vehicle_type,
            'Location': {},
            'Rotation': {},
            'Payloads': plds
        }

class SpawnVehicleReplayGroup(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'ConfigureVehicleReplay', '')
        psr = parser.add_parser(
            'spawn-group', help='spawn each replay vehicle for a given group', formatter_class=RawTextHelpFormatter)

        psr.add_argument(
            'group_name',
            default="",
            help="if specified, all vehicles will begin recording with the given group name")

        psr.add_argument(
            '--start-time',
            type=float,
            default=-1.0,
            help="start the replay this many seconds in")

        psr.add_argument(
            '--rate',
            type=float,
            default=-1.0,
            help="")

        psr.set_defaults(func=self.send_request)

    def get_request_body(self, args):

        return {
            'PlayRate': args.rate,
            'startTime': args.start_time,
            'profile': '',
            'replayAction': 'start',
            #'teleportLocation': '',
            'recordAction': '',
            'bShouldOverrideRecordSingleLap': False,
            'bRecordSingleLapOverride': False,
            'bShouldOverrideRecordMinSpeedThresh': False,
            'RecordMinSpeedThreshOverride': -1.0,
            'recordFileName': '',
            'recordRateHz': 100,
            "RecordingGroupName": args.group_name
        }

class StartVehicleReplayRecording(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'ConfigureVehicleReplay', 'Ego')
        psr = parser.add_parser(
            'start-recording', help='begin recording vehicle motion', formatter_class=RawTextHelpFormatter)

        psr.add_argument(
            'out_file',
            help='the file name to use for the saved recording')

        psr.add_argument('--object-name', default='Ego', help='the name of the object to record')

        psr.add_argument(
            '--rate-hz',
            type=float,
            default=100.0, 
            help='the rate to record vehicle motion. high rates will produce large files')

        psr.add_argument(
            '--group-name',
            default="",
            help="if specified, all vehicles will begin recording with the given group name")

        psr.add_argument(
            '--not-single-lap',
            action='store_true', 
            help='if set, recording will not try to capture exactly one lap and must be stopped by the user')

        psr.set_defaults(func=self.send_request)
    

    def get_request_body(self, args):
        self.target_object_id = args.object_name

        # we do not want to default to ego for group recordings
        # because we want the replay manager to handle them
        if args.group_name != "":
            self.target_object_id = ""
            # it doesnt make sense to do group recordings as single laps
            args.not_single_lap = True

        return {
            'PlayRate': -1.0,
            'profile': '',
            'replayAction': '',
            #'teleportLocation': '',
            'recordAction': 'start',
            'bShouldOverrideRecordSingleLap': args.not_single_lap,
            'bRecordSingleLapOverride': not args.not_single_lap,
            'bShouldOverrideRecordMinSpeedThresh': args.group_name != "", # no min speed for groups
            'RecordMinSpeedThreshOverride': -1.0,
            'recordFileName': args.out_file,
            'recordRateHz': args.rate_hz,
            "RecordingGroupName": args.group_name
        }

class StopVehicleReplayRecording(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'ConfigureVehicleReplay', 'Ego')
        psr = parser.add_parser(
            'stop-recording', help='begin recording vehicle motion', formatter_class=RawTextHelpFormatter)

        psr.add_argument('--object-name', default='Ego', help='the name of the object to record')

        psr.add_argument(
            '--group-name',
            default="",
            help="if specified, all vehicles will begin recording with the given group name")

        psr.set_defaults(func=self.send_request)
    

    def get_request_body(self, args):
        self.target_object_id = args.object_name

        # we do not want to default to ego for group recordings
        # because we want the replay manager to handle them
        if args.group_name != "":
            self.target_object_id = ""
        return {
            'recordAction': 'stop',
            "RecordingGroupName": args.group_name
        }

class DespawnReplayVehicle(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'DespawnObject', 'Ego')
        psr = parser.add_parser(
            'despawn', help='despawn a replay vehicle or all replay vehicles', formatter_class=RawTextHelpFormatter)

        psr.add_argument(
            '--name', 
            default='',
            help='name of the replay vehicle to despawn')

        psr.add_argument(
            '--all',
            action='store_true',
            help='if set, will despawn all replay vehicles')

        psr.set_defaults(func=self.send_request)
    

    def get_request_body(self, args):
        self.target_object_id = args.name
        tags = ["Npc"] if args.all else []

        return {
            'tags': tags,
            'bMatchAnyTag': True
        }