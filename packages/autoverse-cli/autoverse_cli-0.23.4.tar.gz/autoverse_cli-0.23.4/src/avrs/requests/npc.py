from avrs.requests.request import AvrsApiRequest
from argparse import RawDescriptionHelpFormatter
from argparse import RawTextHelpFormatter

class Npc():
    def __init__(self, parser, cfg):
        psr = parser.add_parser('npc', help='Peforms a variety of NPC control commands')
        sps = psr.add_subparsers(required= True, help='sub-command of NPC')
        NpcSpawn(sps, cfg)
        NpcDespawn(sps, cfg)
        NpcChangeDifficulty(sps, cfg)
        NpcStart(sps, cfg)
        NpcStop(sps, cfg)
        NpcSetSpeed(sps, cfg)
        NpcChangeProfile(sps, cfg)
        NpcTeleport(sps, cfg)
       
NPC_SPAWN_POSITION_HELP = '''
spawn the NPC in a relative position or absoulte position
'''

NPC_SPAWN_PROFILE_HELP = '''
Sets the profile of which the npc follows. Note: the profiles provided are ones Provided by Autonoma. 
If you wish to use your own you have two options. If your custom profile
is located in the saved folder of the simulator you can just enter the filename. 
However if this is not the case you must enter the absolute path of the file
Provided Profiles:
    middleRouteYas
    leftRouteYas
    rightRouteYas
    backMiddleRouteYas
    backLeftRouteYas
'''

NPC_ROUTE_CHOICES = [
    'middleRouteYas', 
    'leftRouteYas', 
    'rightRouteYas', 
    'backMiddleRouteYas', 
    'backLeftRouteYas', 
    'atlNpc1', 
    'atlNpc2', 
    'atlNpc3', 
    'atlNpc4', 
    'atlNpc5'
]

class NpcSpawn(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'SpawnObject', '')
        psr = parser.add_parser(
            'spawn', help='spawn an NPC', formatter_class=RawTextHelpFormatter)

        psr.add_argument(
            '--name', 
            default='npc0', 
            help='name of the npc to spawn')

        psr.add_argument(
            '--vehicle-type', 
            default='HondaOdyssey', 
            help='what type of vehicle to spawn as an NPC')

        psr.add_argument(
            '--position', 
            choices=('relative', 'absolute'), 
            default='absolute', 
            help=NPC_SPAWN_POSITION_HELP)

        psr.add_argument(
            '--profile', 
            default='leftRouteYas', 
            help=NPC_SPAWN_PROFILE_HELP)

        psr.add_argument(
            '--velocity-type', 
            default='constant', 
            help='the path the NPC follows is a constant velocity or speed')

        psr.add_argument(
            '--speed', 
            type=float, 
            default=20, 
            help='the speed of the npc is m/s')

        psr.add_argument(
            '--difficulty', 
            type=float, 
            default=1.0, 
            help='the playback speed of the velocity profile, 1.0 is normal')

        psr.add_argument(
            '--enable-sensors', 
            type=bool, 
            default=False, 
            help='whether to enable sensors on the NPC')

        psr.add_argument(
            '--with-view-cameras',
            type=bool,
            default=False,
            help='whether to attach viewing cameras to the NPC')
        
        psr.set_defaults(func=self.send_request)
    

    def get_request_body(self, args):        
        if args.profile not in NPC_ROUTE_CHOICES:
            print(f"Warning: '{args.profile}' is not a default option, procceeding with custom file")
        
        npc_init_pld = {
            'Name': args.name,
            'Position': args.position,
            'Profile': args.profile,
            'Velocity' : args.velocity_type,
            'Speed' : args.speed,
            'Difficulty' : args.difficulty,
            'bEnableSensors': args.enable_sensors
        }

        eav_init_pld = {
            'VehicleCanName': 'can0'
        }

        plds = [
            {
                'TypeName': 'NpcInitializer',
                'Body': npc_init_pld
            }
        ]

        if args.with_view_cameras:
            plds.append(
                {
                    'TypeName': 'InitializerTemplates',
                    'Body': {
                        'Templates': [
                            {
                                'PayloadType': 'SimViewTargetIpd',
                                'PayloadSpec': 'DefaultCarCams'
                            }
                        ]
                    }
                })

        return {
            'Name': args.name,
            'Type': args.vehicle_type,
            'Location': {},
            'Rotation': {},
            'Payloads': plds
        }

class NpcDespawn(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'NpcDespawn', 'Npc')
        psr = parser.add_parser('despawn', help='despawn an NPC')
        psr.add_argument('name', help = 'name of the npc to despawn')
        psr.set_defaults(func=self.send_request)
    
    def get_request_body(self, args):
        return {
            'Name': args.name
        }
    

class NpcTeleport(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'NpcTeleport', 'Npc')
        psr = parser.add_parser('teleport', help = 'telport an active NPC to new x,y,z location,' 
                                + 'a location on the path will be selected closeset to this value')
        psr.add_argument('name', help='name of npc to teleport')
        subparsers = psr.add_subparsers(dest = "action", help='sub-command of NPC teleport')

        # Define the parser for the 'vehicle' option
        vehicle_parser = subparsers.add_parser('vehicle', help='Teleport to the vehicle to an existing car')

        # Defines the parser for the 'custom' option
        custom_parser = subparsers.add_parser('custom', help='Teleport to custom coordinates')
        custom_parser.add_argument('x', type=float,  help='X coordinate.')
        custom_parser.add_argument('y', type=float,  help='Y coordinate.')
        custom_parser.add_argument('z', type=float,  help='Y coordinate.')
        
        psr.set_defaults(func = self.send_request)
    
    def get_request_body(self, args):
        if args.action == 'vehicle':
            print("Correct")
            return {
                'Name': args.name,
                'Type': args.action,
                'X': 0,
                'Y': 0,
                'Z': 0
            }
        else:
            return {
                'Name': args.name,
                'Type': args.action,
                'X': args.x,
                'Y': args.y,
                'Z ': args.z
            }
        
class NpcChangeProfile(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'NpcChangeProfile', 'Npc')
        psr = parser.add_parser('change-path', help = 'changes the raceline of an active NPC')
        psr.add_argument('name', help='name of npc to change the path for')
        psr.add_argument('profile', type=str, help = 'change the profile of the NPC, the same profile constraints apply as the spawn command')
        psr.set_defaults(func=self.send_request)
    
    def get_request_body(self, args):
        choices =  ['middleRouteYas', 'leftRouteYas', 'rightRouteYas', 'backMiddleRouteYas', 'backLeftRouteYas', 'atlNpc1', 'atlNpc2', 'atlNpc3', 'atlNpc4', 'atlNpc5']
        if args.profile not in choices:
            print(f"Warning: '{args.profile}' is not a default option, procceeding with custom file")
        return {
            'Name': args.name,
            'NewProfile': args.profile
        }
    
class NpcChangeDifficulty(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'NpcChangeDifficulty', 'Npc')
        psr = parser.add_parser('change-difficulty', help = 'changes the difficulty or the the playback speed '
                                + 'of an npc with a non-constant velocity')
        psr.add_argument('name', help='name of npc to change the path for')
        psr.add_argument('difficulty', type = float, help='name of npc to change the path for')
        psr.set_defaults(func=self.send_request)

    def get_request_body(self, args):
        return {
            'Name': args.name,
            'NewDifficulty': args.difficulty
        }


class NpcStart(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'NpcStart', 'Npc')
        psr = parser.add_parser('start', help = 'start an NPC')
        psr.add_argument('name', help='name of npc to start')
        psr.set_defaults(func=self.send_request)
    
    def get_request_body(self, args):
        return {
           'Name' : args.name
        }
    
class NpcStop(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'NpcStop', 'Npc')
        psr = parser.add_parser('stop', help = 'stop an NPC')
        psr.add_argument('name', help='name of npc to stop')
        psr.set_defaults(func=self.send_request)
    
    def get_request_body(self, args):
        return {
            'Name' : args.name
        }
    

class NpcSetSpeed(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'NpcSetSpeed', 'Npc')
        psr = parser.add_parser('set-speed', help = 'sets the speed of an Anctive NPC')
        psr.add_argument('name', help='name of npc to change the speed for')
        psr.add_argument('speed', type = float, help='speed of the NPC')
        psr.set_defaults(func=self.send_request)
    
    def get_request_body(self, args):
        return {
            'Name': args.name,
            'Speed': args.speed
        }
    

    


    



    




