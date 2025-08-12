import os
import stat
import json
import http.client
from avrs.cfg import *
from avrs.launcher_util import *
from avrs.simconfig_util import *

class AvrsSimConfig:
    def __init__(self, parent_parser, cfg):
        self.cfg = cfg
        sim_config_parser = parent_parser.add_parser(
            'sim-config', 
            help='utilities for easily configuring the simulator\n\n')

        sps = sim_config_parser.add_subparsers(required=True, help='sim-config options')

        compare_parser = sps.add_parser(
            'compare-configs',
            help='compare two sets of configuration files')
        compare_parser.add_argument(
            'a',
            help='the path to the first set of config files')
        compare_parser.add_argument(
            'b',
            help='the path to the second set of config files')
        compare_parser.set_defaults(func=self.compare_configs)

        apply_preset_parser = sps.add_parser(
            'apply-preset',
            help='apply a preset configuration for a certain use-case')
        apply_preset_parser.add_argument(
            'preset_name',
            choices=['default', 'lightweight', 'a2rl'],
            help='the name of the preset to apply')
        apply_preset_parser.add_argument(
            '--sim-path',
            default='',
            help='''
the path to the simulator installation having the intended config to modify, or the
index of a known installation. if there is only one known installation, it will be used as
the target
''')
        apply_preset_parser.set_defaults(func=self.apply_preset)


    def apply_preset(self, args):
        sim_path = args.sim_path
        if sim_path == '':
            if 'installs' in self.cfg and len(self.cfg['installs']) > 0:
                if len(self.cfg['installs']) > 1:
                    print('multiple known installs. specify path or index')
                    for i in range(len(self.cfg['installs'])):
                        print('({}) {}'.format(i, self.cfg['installs'][i]))
                    return
                else:
                    sim_path = self.cfg['installs'][0]
            else:
                print('sim_path not specified and no known existing installations')
                return
        try:
            sim_path_index = int(sim_path)
            if 'installs' in self.cfg and len(self.cfg['installs']) > sim_path_index:
                sim_path = self.cfg['installs'][sim_path_index]
        except Exception as e:
            pass
        if not is_installed_sim(sim_path):
            print('{} is not a valid sim installation'.format(sim_path))
            return

        print('applying preset {} to sim install at {}'.format(args.preset_name, sim_path))
        apply_simconfig_preset(get_sim_saved_dir(sim_path), args.preset_name)

    def compare_configs(self, args):
        compare_simconfig_defaults(args.a, args.b)