from avrs.requests.request import AvrsApiRequest
from argparse import RawTextHelpFormatter

SPAWN_OBJECT_HELP = '''
spawn an object with the specified configuration, optionally overriding its name
'''

class AvrsSpawnObjectRequest(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'SpawnObject', 0)
        psr = parser.add_parser('spawn-object', help=SPAWN_OBJECT_HELP, formatter_class=RawTextHelpFormatter)

        psr.add_argument(
            '--object-type',
            default='Eav24',
            help='the type of object to spawn')

        psr.add_argument(
            'spec',
            help='the specialization of the object (eg eav24_mv0)')

        psr.add_argument(
            '--name-override',
            default='',
            help='if not empty, will override the name given to the spawned object')

        psr.add_argument(
            'spawn_landmark',
            help='what landmark to spawn at (eg MvStart0, MvStart1, MvStart2, or MvStart3)')

        psr.set_defaults(func=self.send_request)
    
    def get_request_body(self, args):

        return {
            'name': args.name_override,
            'type': args.object_type,
            'spec': args.spec,
            'bUseStoredInitializer': True,
            'location': {},
            'rotation': {},
            'landmark': args.spawn_landmark,
            'payloads': []
        }