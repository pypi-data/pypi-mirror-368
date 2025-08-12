import os
import glob
import json
import base64
import logging
import datetime

from avrs.simconfig_util import *

# these corresond to what SimConfigFiles sets in its init
# and should autospawns configured
# todo: we could parse these from simconfig.json's environments
# inside SimConfigFiles instead of doing it manually
EXPECTED_ENV_NAMES = [
    "yas",
    "adrome",
    "suzuka"
]

def get_payload(cfg_object, payload_name):
    for p in cfg_object['payloads']:
        if p['typeName'].lower() == payload_name.lower():
            return p
    return None

def clear_autospawns():
    logger = logging.getLogger('avrs')
    sim_path = os.environ.get('AVRS_INSTALL_PATH', 
        os.path.join(os.environ['HOME'], 'autoverse-linux'))
    sim_saved = os.path.join(sim_path, 'Linux', 'Autoverse', 'Saved')
    logger.info('clearing autospawns from sim saved at {}'.format(sim_saved))

    cfg_files = SimConfigFiles(sim_saved)

    cfg_ok, msg = cfg_files.validate()
    if not cfg_ok:
        logger.error(msg)
        return

    # also remove all configs from Objects dir
    files = glob.glob(os.path.join(sim_saved, 'Objects/*'))
    for f in files:
        # do not remove default !!
        if 'Eav24_default' in f:
            logger.info('not removing {} because it is the default'.format(f))
        else:
            logger.info('removing object config: {}'.format(f))
            os.remove(f)


    for ee in EXPECTED_ENV_NAMES:
        cfg_files.files[ee]['autoSpawnObjects'] = []
    
    # keep the default!
    cfg_files.files['main']['objectTemplatePaths'] = ['Objects/Eav24_default.json']

    # we want splitscreen in cloud
    cfg_files.files['main']['bEnableSplitscreen'] = True

    cfg_files.save()

def register_received_vehicle(team_name, slot, cfg_data, bsu_vcan, kistler_vcan, badenia_vcan):
    logger = logging.getLogger('avrs')
    logger.info('registering received vehicle in slot {} for team {}'.format(slot, team_name))

    cfg_string = base64.b64decode(cfg_data)
    cfg_object = json.loads(cfg_string.decode('utf-8'))

    # ensure replay for recording is enabled
    logger.info('ensuring replay component is enabled')
    replay = get_payload(cfg_object, 'WheeledVehicleReplayIpd')
    replay['bEnabled'] = True
    replay['body']['bEnableRecording'] = True

    # ensure perception is disabled
    eav24 = get_payload(cfg_object, 'Eav24Initializer')
    if eav24 is None:
        return (False, 'no eav24 payload found')

    logger.info('disabling perception for received vehicle config')
    eav24['body']['bLidarEnabled'] = False
    eav24['body']['bCameraEnabled'] = False
    eav24['body']['bRadarEnabled'] = False
    eav24['body']['bPublishGroundTruth'] = False
    eav24['body']['bPublishInputs'] = False
    eav24['body']['bRenderHudInWorld'] = True

    # do not disable HUD
    #logger.info('disabling hud for received vehicle config')
    eav24['body']['bHudEnabled'] = True

    logger.info('setting primary vcan to: {}, secondary to: {}, and <unused> to: {}'.format(
        bsu_vcan, kistler_vcan, badenia_vcan))
    eav24['body']['primaryCanName'] = bsu_vcan
    eav24['body']['secondaryCanName'] = kistler_vcan

    eav24['body']['badeniaCanName'] = badenia_vcan

    # limit can rates to conserve resources

    if eav24["body"]["canReceiveRate"] > 10000:
        logger.info("can rx was > 10000. clamping")
        eav24["body"]["canReceiveRate"] = 10000

    if eav24["body"]["canLowSendRate"] > 10:
        logger.info("can tx low was > 10. clamping")
        eav24["body"]["canLowSendRate"] = 10

    if eav24["body"]["canMedSendRate"] > 100:
        logger.info("can tx med was > 100. clamping")
        eav24["body"]["canMedSendRate"] = 100

    if eav24["body"]["canHighSendRate"] > 500:
        logger.info("can tx high was > 500. clamping")
        eav24["body"]["canHighSendRate"] = 500

    # clamp vectornav rates

    vn = get_payload(cfg_object, "VectornavIpd")
    if vn.get("body", {}).get("sensorDesc", {}).get("namedDataStreams", {}).get("CommonGroup", {}).get("rateHz", 0) > 100:
        logger.info("vn CommonGroup rate was > 100. clamping")
        vn["body"]["sensorDesc"]["namedDataStreams"]["CommonGroup"]["rateHz"] = 100

    if vn.get("body", {}).get("sensorDesc", {}).get("namedDataStreams", {}).get("GpsGroup", {}).get("rateHz", 0) > 10:
        logger.info("vn GpsGroup rate was > 10. clamping")
        vn["body"]["sensorDesc"]["namedDataStreams"]["GpsGroup"]["rateHz"] = 10

    if vn.get("body", {}).get("sensorDesc", {}).get("namedDataStreams", {}).get("Gps2Group", {}).get("rateHz", 0) > 10:
        logger.info("vn Gps2Group rate was > 10. clamping")
        vn["body"]["sensorDesc"]["namedDataStreams"]["Gps2Group"]["rateHz"] = 10

    if vn.get("body", {}).get("sensorDesc", {}).get("namedDataStreams", {}).get("ImuGroup", {}).get("rateHz", 0) > 150:
        logger.info("vn ImuGroup rate was > 150. clamping")
        vn["body"]["sensorDesc"]["namedDataStreams"]["ImuGroup"]["rateHz"] = 150

    if vn.get("body", {}).get("sensorDesc", {}).get("namedDataStreams", {}).get("AttitudeGroup", {}).get("rateHz", 0) > 100:
        logger.info("vn AttitudeGroup rate was > 100. clamping")
        vn["body"]["sensorDesc"]["namedDataStreams"]["AttitudeGroup"]["rateHz"] = 100

    if vn.get("body", {}).get("sensorDesc", {}).get("namedDataStreams", {}).get("Tii", {}).get("rateHz", 0) > 100:
        logger.info("vn Tii rate was > 100. clamping")
        vn["body"]["sensorDesc"]["namedDataStreams"]["Tii"]["rateHz"] = 100

    if vn.get("body", {}).get("sensorDesc", {}).get("namedDataStreams", {}).get("NavSatFix", {}).get("rateHz", 0) > 10:
        logger.info("vn NavSatFix rate was > 10. clamping")
        vn["body"]["sensorDesc"]["namedDataStreams"]["NavSatFix"]["rateHz"] = 10

    ros2 = get_payload(cfg_object, 'Ros2')
    if ros2 is None:
        logger.info('no ros2 payload found. adding with domain id {}'.format(slot))
        # need to add a ros2 payload for domain id
        cfg_object['payloads'].append({
            'typeName': 'Ros2',
            'body': {
                'domainId': slot
            }
        })
    else:
        logger.info('found Ros2 payload OK'.format())
        logger.info('setting ros2 domain id to {}'.format(slot))
        ros2['body']['domainId'] = slot

    # auto add display widget
    wtc = get_payload(cfg_object, 'WorldTextComponent')
    if wtc is None:
        logger.info('no WorldTextComponent payload found. adding')
        cfg_object['payloads'].append({
            'typeName': 'WorldTextComponent',
            'body': {

            }
        })
    else:
        logger.info('found WorldTextComponent payload. ensuring it is enabled')
        wtc['bEnabled'] = True

    # auto add / enable ground truth payload
    gtc = get_payload(cfg_object, 'GroundTruthSensor')
    if gtc is None:
        logger.info('no GroundTruthSensor payload found. adding')
        cfg_object['payloads'].append({
            'typeName': 'GroundTruthSensor',
            'body': {
                'myGroundTruthDsd': {
                    'streamName': 'ground_truth',
                    'rateHz': 50.0
                },
                'opponentGroundTruthDsd': {
                    'streamName': 'v2v_ground_truth',
                    'rateHz': 50.0
                },
                'bUseOpponentRelativeRotation': False 
            }
        })
    else:
        logger.info('found GroundTruthSensor payload. ensuring it is enabled')
        gtc['bEnabled'] = True

    # limit gt rates

    gtc = get_payload(cfg_object, 'GroundTruthSensor')
    if gtc["body"]["myGroundTruthDsd"]["rateHz"] > 100:
        logger.info("myGroundTruthDsd rate was > 100. clamping")
        gtc["body"]["myGroundTruthDsd"]["rateHz"] = 100

    if gtc["body"]["opponentGroundTruthDsd"]["rateHz"] > 100:
        logger.info("opponentGroundTruthDsd rate was > 100. clamping")
        gtc["body"]["opponentGroundTruthDsd"]["rateHz"] = 100


    # do not allow default object name (collision)
    if cfg_object['name'] == 'eav24':
        logger.info('setting vehicle name from default to team name: {}'.format(team_name))
        cfg_object['name'] = team_name
    object_spec_name = 'eav24_{}'.format(team_name)
    cfg_object['specName'] = object_spec_name

    # also need to edit the yas_marina_env.json to have autospawn for this config
    sim_path = os.environ.get('AVRS_INSTALL_PATH', 
        os.path.join(os.environ['HOME'], 'autoverse-linux'))
    sim_saved = os.path.join(sim_path, 'Linux', 'Autoverse', 'Saved')
    cfg_files = SimConfigFiles(sim_saved)

    cfg_ok, msg = cfg_files.validate()
    if not cfg_ok:
        print(msg)
        return

    start_landmark = 'PitsSlot{}'.format(slot + 1)

    for ee in EXPECTED_ENV_NAMES:
        entry_exists = False

        # we want logging on for all environments
        cfg_files.files[ee]['bAutoRecordVehicles'] = True

        for i in cfg_files.files[ee]['autoSpawnObjects']:
            if 'objectSpec' in i and i['objectSpec'] == cfg_object['specName']:
                entry_exists = True
                logger.info('config is already in auto spawn list')

        if not entry_exists:
            logger.info('config is not in auto spawn list. adding')
            cfg_files.files[ee]['autoSpawnObjects'].append({
                    'bShouldSpawn': True,
                    'objectType': 'Eav24',
                    'objectSpec': cfg_object['specName'],
                    'bSpawnAtLandmark': True,
                    'spawnLandmarkName': start_landmark
                })

    # also need to add the object template to main sim config

    new_cfg_name = 'eav24_{}.json'.format(object_spec_name)
    cfg_files.files['main']['objectTemplatePaths'].append(os.path.join('Objects', new_cfg_name))
    logger.info('saving config file: {}'.format(new_cfg_name))
    cfg_files.save()

    target_path = os.path.join(sim_saved, 'Objects', new_cfg_name)
    with open(target_path, 'w', encoding='utf-8') as f:
        json.dump(cfg_object, f, ensure_ascii=False, indent=4)
    backup_path = os.path.join(os.environ['HOME'], 'team_configs')
    if not os.path.exists(backup_path):
        os.mkdir(backup_path)
    date_time = datetime.datetime.now(datetime.timezone.utc).strftime("%Y_%m_%d_%H_%M_%S")
    backup_path = os.path.join(backup_path, '{}_{}'.format(date_time,new_cfg_name))
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(cfg_object, f, ensure_ascii=False, indent=4)

def prepare_vehicle_cfg(cfg_path):
    logger = logging.getLogger('avrs')
    #print('preparing config for transmission: {}'.format(cfg_path))

    if not os.path.isfile(cfg_path):
        return (False, '{} is not a valid file'.format(cfg_path), None, None, None)

    cfg_object = {}
    with open(cfg_path, 'r', encoding='utf-8') as f:
        cfg_object = json.load(f)


    # obtain desired CAN names to start cannelloni
    eav24 = get_payload(cfg_object, 'Eav24Initializer')
    if eav24 is None:
        return (False, 'no eav24 payload found', None, None, None)



    bsu_vcan = eav24['body'].get('primaryCanName', '')
    if bsu_vcan == '':
        logger.info('primaryCanName key not found, trying old bsuCanName')
        bsu_vcan = eav24['body'].get('bsuCanName', '')
    kistler_vcan = eav24['body'].get('secondaryCanName', '')
    if kistler_vcan == '':
        logger.info('secondaryCanName key not found, trying old kistlerCanName')
        kistler_vcan = eav24['body'].get('kistlerCanName', '')
    badenia_vcan = 'unused'

    if bsu_vcan == '':
        logger.error('could not find either primaryCanName or bsuCanName')
    if kistler_vcan == '':
        logger.error('could not find either secondaryCanName or kistlerCanName')

    logger.info('detected vcan names from sent config: bsu {}, kistler {}, badenia {}'.format(
        bsu_vcan, kistler_vcan, badenia_vcan))

    cfg_data = base64.b64encode(json.dumps(cfg_object).encode('utf-8')).decode('utf-8')
    return (True, cfg_data, bsu_vcan, kistler_vcan, badenia_vcan)

