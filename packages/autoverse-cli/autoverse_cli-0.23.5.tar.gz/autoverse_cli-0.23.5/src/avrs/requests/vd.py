from avrs.requests.request import AvrsApiRequest

class Vd():
    def __init__(self, parser, cfg):
        psr = parser.add_parser('vd', help='Vehicle dynamic options')
        sps = psr.add_subparsers(required= True, help='sub-command of vd')
        SetFrictionModifier(sps, cfg)
        GetFrictionModifier(sps, cfg)
        #SlipModel(sps, cfg)

class SetFrictionModifier(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'SetFrictionModifiers', 'Ego')
        psr = parser.add_parser('set-friction-modifier', help='Change the amount of grip the car has.' 
            + '0 is no grip and higher values will prevent spinning')
        psr.add_argument('modifier', type = float, help = "Modified grip value")
        psr.add_argument('tires', help = "Tires to apply the modifier to", 
            choices=("FL", "FR", "RL", "RR", "F", "R", "All"))

        psr.add_argument(
            '--object-name',
            default='ego',
            help='the simulated object to modify the friction for')
        
        psr.set_defaults(func=self.send_request)
    
    def get_request_body(self, args):
        self.target_object_id = args.object_name
        return {
            'NewModifier': args.modifier,
            'Tires': args.tires
        }
    
class GetFrictionModifier(AvrsApiRequest):
    def __init__(self, parser, cfg):
        AvrsApiRequest.__init__(self, parser, cfg, 'GetFrictionModifiers', 'Ego')
        psr = parser.add_parser('get-friction-modifier', help='Get the amount of grip the car has.')
        psr.add_argument('tires', help = "Tires to get the grip value from", 
            choices=("FL", "FR", "RL", "RR", "F", "R", "All"))

        psr.add_argument(
            '--object-name',
            default='ego',
            help='the simulated object to get the friction from')

        psr.set_defaults(func=self.send_request)
    
    def get_request_body(self, args):
        self.target_object_id = args.object_name
        return {
            'Tires': args.tires
        }
    
# class SlipModel(AvrsApiRequest):
#     def __init__(self, parser, cfg):
#         AvrsApiRequest.__init__(self, parser, cfg, 'SlipModel', 'Ego')
#         psr = parser.add_parser('slip-model', help='Change the tire slip model to be pure slip only or combined slip')
#         psr.add_argument('slip', choices = ['pure-slip, combined-slip'], help = 'type of slip')
#         psr.set_defaults(func=self.send_request)
    
#     def get_request_body(self, args):
#         return {
#             'Modifier Value': args.slip
#         }