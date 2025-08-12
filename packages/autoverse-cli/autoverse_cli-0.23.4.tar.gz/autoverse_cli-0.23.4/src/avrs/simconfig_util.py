import os
import json
import logging

class SimConfigFiles():
    def __init__(self, saved_dir):

        logger = logging.getLogger('avrs')

        self.required_files = {
            'main': os.path.join(saved_dir, 'simconfig.json'),
            'eav24': os.path.join(saved_dir, 'Objects', 'Eav24_default.json'),
            'yas': os.path.join(saved_dir, 'Environments', 'yasmarina_env.json'),
            'adrome': os.path.join(saved_dir, 'Environments', 'autonodrome.json'),
            'suzuka': os.path.join(saved_dir, "Environments", "Suzuka", "suzuka.json")
        }

        self.alt_paths = {
            "main": [],
            "eav24": [],
            "yas": [os.path.join(saved_dir, 'Environments', "YasMarina", 'yasmarina_env.json')],
            "adrome": [os.path.join(saved_dir, 'Environments', "Autonodrome", 'autonodrome.json')],
            "suzuka": [os.path.join(saved_dir, "Environments", "Suzuka", "suzuka.json")]
        }

        # support alternative paths for new directory structure, but retain backward compat
        for k, v in self.required_files.items():
            if not os.path.exists(v):
                for alt_path in self.alt_paths.get(k, []):
                    if os.path.exists(alt_path):
                        logger.info("could not find file under {} but found under alt path {}".format(
                            v, alt_path))
                        self.required_files[k] = alt_path

        self.files = {}

        ok, status = self.validate()
        if ok:
            for name, path in self.required_files.items():
                with open(path, 'r', encoding='utf-8') as f:
                    self.files[name] = json.load(f)

    def validate(self):
        for name, path in self.required_files.items():
            if not os.path.exists(path):
                return (False, '{} not found'.format(path))
        return (True, '')

    def save(self):
        for name, path in self.required_files.items():
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.files[name], f, ensure_ascii=False, indent=4)

def compare_simconfig_defaults(sim_saved_dir, new_defaults_dir):
    old_cfg_files = SimConfigFiles(sim_saved_dir)
    new_cfg_files = SimConfigFiles(new_defaults_dir)

    ok, status = old_cfg_files.validate()
    if not ok:
        print(status)
        return
    ok, status = new_cfg_files.validate()
    if not ok:
        print(status)
        return

    print('comparing config files at {} with those at {}'.format(
        sim_saved_dir, new_defaults_dir))

    out_cpr = {}
    compare_dicts(old_cfg_files.files['main'], new_cfg_files.files['main'], 'main', out_cpr)

    #print('{}'.format(out_cpr))
    print_simconfig_compare(out_cpr['main'])

def print_simconfig_compare(cpr):
        for i in cpr['only_a']:
            print('{} in a ({}) but not b'.format(i[0], i[1]))
        for i in cpr['only_b']:
            print('{} in b ({}) but not a'.format(i[0], i[1]))
        for i in cpr['type_mismatch']:
            print('{} ({}) does not match type {} ({})'.format(i[0], i[1], i[0], i[2]))
        for i in cpr['value_mismatch']:
            print('{} ({}) value does not match ({})'.format(i[0], i[1], i[2]))

        for key, value in cpr['sub'].items():
            print_simconfig_compare(value)

def compare_dicts(a, b, parent_key, out_checks):

    only_a = []
    only_b = []
    type_mismatch = []
    value_mismatch = []

    out_checks[parent_key] = {}
    out_checks[parent_key]['sub'] = {}


    for key, value in a.items():
        key_chain = '{}.{}'.format(parent_key, key)
        if key not in b:
            only_a.append((key_chain, value))
        else:
            if type(value) != type(b[key]):
                type_mismatch.append((key_chain, type(value), type(b[key])))
            elif isinstance(value, dict):
                compare_dicts(value, b[key], key_chain, out_checks[parent_key]['sub']) 
            elif value != b[key]:
                value_mismatch.append((key_chain, value, b[key]))

    for key, value in b.items():
        key_chain = '{}.{}'.format(parent_key, key)
        if key not in a:
            only_b.append((key_chain, value))

    out_checks[parent_key]['only_a'] = only_a
    out_checks[parent_key]['only_b'] = only_b
    out_checks[parent_key]['type_mismatch'] = type_mismatch
    out_checks[parent_key]['value_mismatch'] = value_mismatch

    #print('only a \n {} \n\n'.format(only_a))
    #print('only b \n {} \n\n'.format(only_b))
    #print('type mismatch \n {} \n\n'.format(type_mismatch))
    #print('value mismatch \n {} \n\n'.format(value_mismatch))
    #print('sub_checks')



def apply_simconfig_preset(sim_saved_dir, preset_name):
    cfg_files = SimConfigFiles(sim_saved_dir)
    ok, status = cfg_files.valdiate()
    if not ok:
        print(status)
        return

    presets = {
        'default': apply_default_simconfig_preset,
        'lightweight': apply_lightweight_simconfig_preset,
        'a2rl': apply_a2rl_simconfig_preset
    }
    presets[preset_name](cfg_files)    

def apply_default_simconfig_preset(cfg_files):
    files = cfg_files.files
    
    print('globally enabling ROS2 and CAN')
    files['main']['interfaces']['bEnableRos2'] = True
    files['main']['interfaces']['bEnableCan'] = True

    print('ensuring default eav24 and yasmarina are reference in main config')
    if not 'Environments/yasmarina_env.json' in files['main']['environmentPaths']:
        print('missing yas environment. adding')
        print('{}'.format(files['main']['environmentPaths']))
    if not 'Objects/Eav24_default.json' in files['main']['objectTemplatePaths']:
        print('missing eav24. adding')

    cfg_files.save()


def apply_lightweight_simconfig_preset(cfg_files):
    files = cfg_files.files
    
    cfg_files.save()

def apply_a2rl_simconfig_preset(cfg_files):
    files = cfg_files.files
    
    cfg_files.save()