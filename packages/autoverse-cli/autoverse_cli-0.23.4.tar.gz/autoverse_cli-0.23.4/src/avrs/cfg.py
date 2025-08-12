import json
import os
import shutil

def get_cfg_dir(cli_name):
    return os.path.join(os.environ['HOME'], '.config', cli_name)

def get_cfg_file(cli_name):
    return os.path.join(get_cfg_dir(cli_name), 'config.json')

def load_cfg(cli_name):
    cfg_dir = get_cfg_dir(cli_name)
    if not os.path.exists(cfg_dir):
        os.makedirs(cfg_dir)

    cfg_path = get_cfg_file(cli_name)
    cfg = {}

    if os.path.exists(cfg_path):
        with open(cfg_path, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
    return cfg

def save_cfg(cli_name, cfg):
    cfg_path = get_cfg_file(cli_name)
    with open(cfg_path, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, ensure_ascii=False, indent=4)

# Save a file to be re-used later to a cached location
def add_cached_file(cli_name, category, file_to_cache, overwrite_ok):
    if not os.path.exists(file_to_cache):
        return (False, '{} is not a valid file'.format(file_to_cache))
    cfg = load_cfg(cli_name)
    if '__cached_files__' not in cfg:
        cfg['__cached_files__'] = {}
    if category not in cfg['__cached_files__']:
        cfg['__cached_files__'][category] = []
    file_to_cache_name = os.path.basename(file_to_cache)
    cfg['__cached_files__'][category].append(file_to_cache_name)
    cat_path = os.path.join(get_cfg_dir(cli_name), category)
    if not os.path.exists(cat_path):
        os.makedirs(cat_path)
    cache_path = os.path.join(cat_path, file_to_cache_name)
    if os.path.isfile(cache_path) and not overwrite_ok:
        return (False, '{} already exists and overwrite not specified as ok'.format(cache_path))
    shutil.copyfile(file_to_cache, cache_path)
    save_cfg(cli_name, cfg)
    return (True, '{} cached to {}'.format(file_to_cache, cache_path))

# Get a file previously cached
def get_cached_file(cli_name, category, file_to_get):
    cfg = load_cfg(cli_name)
    if '__cached_files__' not in cfg:
        return (False, 'no cached files')
    if category not in cfg['__cached_files__']:
        return (False, 'cached file {} not found'.format(file_to_get))
    cache_path = os.path.join(get_cfg_dir(cli_name), category, file_to_get)
    cf = cfg['__cached_files__'][category]
    # Check by index
    try:
        file_index = int(file_to_get)
        if file_index > -1 and file_index < len(cf):
            cache_path = os.path.join(get_cfg_dir(cli_name), category, cf[file_index])
        else:
            return (False, '{} is not a valid file index'.format(file_index))
    except Exception as e:
        pass
    if not os.path.exists(cache_path):
        return (False, 'failed to get cached file at {}'.format(cache_path))
    return (True, cache_path)

def get_cached_file_list(cli_name, category):
    cfg = load_cfg(cli_name)
    if '__cached_files__' not in cfg:
        return []
    if category not in cfg['__cached_files__']:
        return []
    return cfg['__cached_files__'][category]