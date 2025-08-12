import os
import json
import http.client
import boto3
import sys
import shutil

def validate_license_file(file_path):
    """ 
    Given file path, load and validate license info. Returns tuple of bool
    indicating success, string for status, and dict of license info from file
    """
    status = ''
    license = {}

    # Ensure it's a file
    if not os.path.isfile(file_path):
        status = 'no license file at {}'.format(file_path)
        return (False, status, license)

    # Parse it and check format
    with open(file_path, 'r', encoding='utf-8') as f:
        license = json.load(f)

    if 'id' not in license:
        status = 'malformed license file. missing id field'
        return (False, status, license)
    if 'public_key' not in license:
        status = 'malformed license file. missing public key field'
        return (False, status, license)
    if 'shipping_signature' not in license:
        status = 'malformed license file. missing shipping signature'
        return (False, status, license)
    return (True, status, license)


def try_get_launcher_download_keys(cfg):
    """
    Uses license info stored in config to requrest download keys from API.
    These keys can be used to authenticate downloads from bucket
    """
    status = ''
    out_cfg = cfg

    api_url = 'uu6fmbvrhk.execute-api.us-east-1.amazonaws.com'
    connection = http.client.HTTPSConnection(api_url)
    headers = {'Content-type': 'application/json'}
    body = json.dumps({
        'id': cfg['license']['data']['id'],
        'licenseSignature': cfg['license']['data']['shipping_signature']
    }).encode('utf-8')
    connection.request('POST', '/test', body, headers)
    response = connection.getresponse()

    api_ok = False
    api_status = ""

    if response.status == 200:
        res_full = json.loads(response.read().decode('utf-8'))
        status += "primary api response: {}".format(res_full)
        dlinfo = json.loads(res_full['body'])
        code = res_full['statusCode']
        if code == 200:
            api_ok = True
            for k, v in dlinfo.items():
                    out_cfg[k] = v

    if not api_ok:
        #try other api
        alt_api_url = 'uu6fmbvrhk.execute-api.us-east-1.amazonaws.com'
        connection = http.client.HTTPSConnection(alt_api_url)
        connection.request('POST', '/test/alt', body, headers)
        response = connection.getresponse()
        if response.status == 200:
            res_full = json.loads(response.read().decode('utf-8'))
            status += "alt api response: {}".format(res_full)
            dlinfo = json.loads(res_full.get('body', "{}"))
            code = res_full['statusCode']
            if code == 200:
                api_ok = True
                for k, v in dlinfo.items():
                    out_cfg[k] = v
            else:
                status += "primary and alt returned non 200"
        else:
            status += "primary and alt returned non 200"

    return (api_ok, status, out_cfg)

def has_launcher_download_keys(cfg):
    """
    Checks for required config values for download keys
    """
    status = ''
    if 'dlkey_id' not in cfg or 'dlkey' not in cfg:
        status += 'Config has no Download Keys'
        return (False, status)
    return (True, status)

def get_launcher_license_status_string(cfg):
    """
    Builds a string representation of where the CLI stands
    as far as being configured as a launcher able to download simulator builds
    """
    status = ''
    if 'license' not in cfg:
        status += 'no license has been registered\n'
    else:
        status += 'license registered as {}\n'.format(cfg['license']['filename'])

    if 'dlkey_id' not in cfg:
        status += 'no download key ID found\n'
    else:
        status += 'download key id obtained\n'

    if 'dlkey' not in cfg:
        status += 'no download key found\n'
    else:
        status += 'download key obtained\n'
    return status

def get_launcher_build_info(cfg, variant):
    """
    Contacts API to discover the current latest build version
    """

    api_url = 'zn5boqqk60.execute-api.us-east-1.amazonaws.com'
    connection = http.client.HTTPSConnection(api_url)
    headers = {'Content-type': 'application/json'}
    body = {
        "packageName": variant
    }
    connection.request('POST', '/test', json.dumps(body).encode("utf-8"), headers)
    response = connection.getresponse()

    if response.status != 200:
        return (False, "get build info api returned {}".format(response.status), "", "")

    res_full = json.loads(response.read().decode('utf-8'))
    info = json.loads(res_full['body'])
    code = res_full['statusCode']
    if code != 200:
        return (False, "get build info api returned {}".format(code), "", "")

    latest_version = info['prod']
    staged_version = info.get('staging', latest_version)
    return (True, "ok", latest_version, staged_version)

def download_simulator_archive(cfg, source_path, target_path):
    """
    Downloads the latest version of the simulator from the builds bucket
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=cfg['dlkey_id'],
        aws_secret_access_key=cfg['dlkey'])
    s3_download_with_progress(s3_client, 'autoverse-builds', source_path, target_path)

def get_sim_saved_dir(sim_install_path):
    return os.path.join(sim_install_path, 'Linux', 'Autoverse', 'Saved')

def is_installed_sim(file_path):
    """
    Check if the given path appears to be the root of
    a simulator installation
    """
    if not os.path.exists(file_path):
        return False

    if not os.path.isdir(os.path.join(file_path, 'Linux', 'Autoverse')):
        return False

    if not os.path.isfile(os.path.join(file_path, 'Linux', 'Autoverse', 'Saved', 'simconfig.json')):
        return False

    return True

def s3_download_with_progress(s3_client, s3_bucket, s3_object_key, local_file_path):

    meta_data = s3_client.head_object(Bucket=s3_bucket, Key=s3_object_key)
    total_length = int(meta_data.get('ContentLength', 0))
    downloaded = 0

    def progress(chunk):
        nonlocal downloaded
        downloaded += chunk
        done = int(50 * downloaded / total_length)
        sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
        sys.stdout.flush()

    with open(local_file_path, 'wb') as f:
        s3_client.download_fileobj(s3_bucket, s3_object_key, f, Callback=progress)
    print('\n')
