import os
import json
import http.client
import logging
from avrs.util import *

BASH_KILL_PROCESS_SCRIPT = '''
    PROC_NAME={pname}
    I=0
    TRIES=20
    while [ $I -le $TRIES ]; do

        pkill $PROC_NAME
        PROC_RUNNING=$(ps -A | grep $PROC_NAME)
        if [[ ! -z $PROC_RUNNING ]]; then
            echo process $PROC_NAME is still running
            if [ $I == $(( TRIES - 1 )) ]; then
                echo process is resisting. crushing its dreams with sigkill
                pkill -SIGKILL $PROC_NAME
            fi
        else
            echo process $PROC_NAME is not running
            break
        fi
        I=$(( I + 1 ))
        sleep 1
    done
'''

BASH_KILL_BY_LAUNCH_SCRIPT = '''
    ps -x | grep "{launch_phrase}" | awk '{{ print $1 }}' | xargs -L1 kill
'''

DEFAULT_RMW_QOS = '''
<?xml version="1.0" encoding="UTF-8" ?>
<profiles xmlns="http://www.eprosima.com/XMLSchemas/fastRTPS_Profiles">
    <transport_descriptors>
        <transport_descriptor>
            <transport_id>morepeers</transport_id> <!-- string -->
            <type>UDPv4</type> <!-- string -->
            <maxInitialPeersRange>100</maxInitialPeersRange> <!-- uint32 -->
        </transport_descriptor>
    </transport_descriptors>
    <participant profile_name="participant_profile_ros2" is_default_profile="true">
        <rtps>
            <builtin>
                <metatrafficUnicastLocatorList>
                    <locator/>
                </metatrafficUnicastLocatorList>
                <initialPeersList>
                    <locator> <udpv4> <address>127.0.0.1</address> </udpv4> </locator>
                    <!--<locator> <udpv4> <address>PEER_0</address> </udpv4> </locator>PEER0-->
                    <!--<locator> <udpv4> <address>PEER_1</address> </udpv4> </locator>PEER1-->
                    <!--<locator> <udpv4> <address>PEER_2</address> </udpv4> </locator>PEER2-->
                    <!--<locator> <udpv4> <address>PEER_3</address> </udpv4> </locator>PEER3-->
                    <!--<locator> <udpv4> <address>PEER_4</address> </udpv4> </locator>PEER4-->
                    <!--<locator> <udpv4> <address>PEER_5</address> </udpv4> </locator>PEER5-->
                    <!--<locator> <udpv4> <address>PEER_6</address> </udpv4> </locator>PEER6-->
                    <!--<locator> <udpv4> <address>PEER_7</address> </udpv4> </locator>PEER7-->
                    <!--<locator> <udpv4> <address>PEER_8</address> </udpv4> </locator>PEER8-->
                    <!--<locator> <udpv4> <address>PEER_9</address> </udpv4> </locator>PEER9-->
                    <!--<locator> <udpv4> <address>PEER_10</address> </udpv4> </locator>PEER10-->
                    <!--<locator> <udpv4> <address>PEER_11</address> </udpv4> </locator>PEER11-->
                    <!--<locator> <udpv4> <address>PEER_12</address> </udpv4> </locator>PEER12-->
                </initialPeersList>
            </builtin>
            <userTransports>
            <transport_id>morepeers</transport_id>
            </userTransports>
            <useBuiltinTransports>false</useBuiltinTransports>
        </rtps>
    </participant>
</profiles>
'''

DEFAULT_RMW_CYCLONE = '''
    <?xml version="1.0" encoding="UTF-8" ?>
      <CycloneDDS>
        <Domain id="any">
            <Discovery>
                <ParticipantIndex>auto</ParticipantIndex>
                <Peers>
                        <Peer address='127.0.0.1'/>
                        <!--<Peer address='PEER_0'/>PEER0-->
                        <!--<Peer address='PEER_1'/>PEER1-->
                        <!--<Peer address='PEER_2'/>PEER2-->
                        <!--<Peer address='PEER_3'/>PEER3-->
                        <!--<Peer address='PEER_4'/>PEER4-->
                        <!--<Peer address='PEER_5'/>PEER5-->
                        <!--<Peer address='PEER_6'/>PEER6-->
                        <!--<Peer address='PEER_7'/>PEER7-->
                        <!--<Peer address='PEER_8'/>PEER8-->
                        <!--<Peer address='PEER_9'/>PEER9-->
                        <!--<Peer address='PEER_10'/>PEER10-->
                        <!--<Peer address='PEER_11'/>PEER11-->
                        <!--<Peer address='PEER_12'/>PEER12-->
                </Peers>
            </Discovery>
        </Domain>
    </CycloneDDS>
'''

DISABLE_PEER_QOS_SCRIPT = '''
    QOS_FILE_PATH={qos_path}
    CYCLONE_PATH={cyclone_path}
    PEER_ID={peer_id}

    # for the origin rmw qos file
    sed -i -E "s,(<locator> <udpv4> <address>)(.+)(</address> </udpv4> </locator>)<!--(PEER$PEER_ID-->),<!--\\1PEER$PEER_ID\\3\\4,g" $QOS_FILE_PATH

    # for the cyclone file
    sed -i -E "s,(<Peer address=')(.+)('/>)<!--(PEER$PEER_ID-->),<!--\\1PEER$PEER_ID\\3\\4,g" $CYCLONE_PATH

    VCAN_NAME=vcan$PEER_ID
    if [[ -e $VCAN_NAME.vcanlock ]]; then
        echo "stopping existing cannelloni connection with pid $(cat $VCAN_NAME.vcanlock)"
        kill $(cat $VCAN_NAME.vcanlock)
        rm $VCAN_NAME.vcanlock
    fi
'''

ENABLE_PEER_QOS_SCRIPT = '''
    QOS_FILE_PATH={qos_path}
    CYCLONE_PATH={cyclone_path}
    PEER_ID={peer_id}
    PEER_ADDRESS={peer_ip}

    # for the origin rmw qos file
    sed -i -E "s,(<!--?)(<locator> <udpv4> <address>)(.+)(</address> </udpv4> </locator>)(PEER$PEER_ID-->),\\2$PEER_ADDRESS\\4<!--\\5,g" $QOS_FILE_PATH

    # for the cyclone file
    sed -i -E "s,(<!--?)(<Peer address=')(.+)('/>)(PEER$PEER_ID-->),\\2$PEER_ADDRESS\\4<!--\\5,g" $CYCLONE_PATH
'''

CONNECT_PEER_VCAN_SCRIPT = '''
    PEER_ID={peer_id}
    PEER_ADDRESS={peer_ip}
    REMOTE_PORT={remote_port}
    LOCAL_PORT={local_port}
    VCAN_NAME={vcan_name}
    LOCK_FILE="$HOME/.$VCAN_NAME.vcanlock"
    LOG_FILE="$HOME/.$VCAN_NAME.vcanlog"
    if [[ -z $VCAN_NAME ]]; then
        VCAN_NAME=vcan$PEER_ID
    fi
    echo "connecting peer id $PEER_ID using local port $LOCAL_PORT and remote port $REMOTE_PORT and vcan name $VCAN_NAME" > "$LOG_FILE" 2>&1

    if [[ -e $LOCK_FILE ]]; then
        echo "stopping existing can_bridge connection with pid $(cat $LOCK_FILE)"
        kill $(cat $LOCK_FILE)
    fi

    # https://stackoverflow.com/questions/29142/getting-ssh-to-execute-a-command-in-the-background-on-target-machine
    # nohup to avoid SSH issues, send stdout to loni.log, send stderr to stdout, dont expect input, and background with "&"
    nohup avrs race-cloud bridge-can fg $VCAN_NAME $PEER_ADDRESS $REMOTE_PORT $LOCAL_PORT >>"$LOG_FILE" 2>&1 < /dev/null &
    echo "$!" > $LOCK_FILE
'''

CHECK_VCAN_EXISTS_SCRIPT = '''
    if [[ -z $(ip addr show | grep {vcan_name}) ]]; then
        echo -n "no"
    else
        echo -n "yes"
    fi
'''

CREATE_VCANS_SCRIPT = '''
    sudo modprobe vcan
    sudo ip link add name "{a}" type vcan
    sudo ip link set dev "{a}" up
    sudo ip link add name "{b}" type vcan
    sudo ip link set dev "{b}" up
    sudo ip link add name "{c}" type vcan
    sudo ip link set dev "{c}" up
'''

START_FWD_API_SCRIPT = '''
    nohup avrs race-cloud fwd-api fg {source_port} {target_port} >> ~/fwd_api.log 2>&1 < /dev/null &
    echo "$!" > ~/fwd_api_pid
'''

STOP_FWD_API_SCRIPT = '''
    if [[ -e ~/fwd_api_pid ]]; then
        kill $(cat ~/fwd_api_pid)
    fi
    rm ~/fwd_api_pid
'''

GET_EC2_LOCAL_IP_SCRIPT = '''
    echo -n $(ec2metadata --local-ipv4)
'''

# kill a process with a given name
def bash_kill_process(pname):
    return run_process(['bash', '-c', 
        BASH_KILL_PROCESS_SCRIPT.format(**{'pname': pname})])

def bash_kill_process_by_launch_command(launch_command):
    return run_process(['bash', '-c',
        BASH_KILL_BY_LAUNCH_SCRIPT.format(**{'launch_phrase': launch_command})])

# start an exectuable in the background, sending output to a file
# stored at root with its name
def start_exe(exe_path):
    logger = logging.getLogger('avrs')
    logger.info('running {} and saving under {}'.format(exe_path, os.path.basename(exe_path).replace(' ', '')))
    return run_process(['bash', '-c',
        'nohup {} > ~/{}_output.log 2>&1 < /dev/null &'.format(exe_path, os.path.basename(exe_path).replace(' ', ''))])

def get_sim_install_path():
    sim_path = os.environ.get('AVRS_INSTALL_PATH', 
        os.path.join(os.environ['HOME'], 'autoverse-linux'))
    return sim_path

def get_sim_exe_path():
    exe_path = os.environ.get('AVRS_EXE_PATH',
        os.path.join(os.environ['HOME'], 'autoverse-linux', 'Linux', 'utils', 'run_autoverse.sh'))
    return exe_path

def get_rmw_qos_path():
    return os.path.join(os.environ['HOME'], '.rmw_qos.xml')

def get_rmw_cyclone_qos_path():
    return os.path.join(os.environ['HOME'], '.cyclone.xml')

def reset_rmw_qos():
    with open(get_rmw_qos_path(), 'w', encoding='utf-8') as f:
        f.write(DEFAULT_RMW_QOS)

def reset_rmw_cyclone_qos():
    with open(get_rmw_cyclone_qos_path(), 'w', encoding='utf-8') as f:
        f.write(DEFAULT_RMW_CYCLONE)

def disable_peer_qos(peer_id):
    if not os.path.isfile(get_rmw_qos_path()):
        reset_rmw_qos()
    if not os.path.isfile(get_rmw_cyclone_qos_path()):
        reset_rmw_cyclone_qos()
    pargs = {
        'qos_path': get_rmw_qos_path(),
        'cyclone_path': get_rmw_cyclone_qos_path(),
        'peer_id': peer_id
    }
    return run_process(['bash', '-c',
        DISABLE_PEER_QOS_SCRIPT.format(**pargs)])

def enable_peer_qos(peer_id, peer_ip):
    disable_peer_qos(peer_ip) # disable first
    pargs = {
        'qos_path': get_rmw_qos_path(),
        'cyclone_path': get_rmw_cyclone_qos_path(),
        'peer_id': peer_id,
        'peer_ip': peer_ip
    }
    return run_process(['bash', '-c',
        ENABLE_PEER_QOS_SCRIPT.format(**pargs)])

def check_vcan_exists(vcan_name):
    pargs = {
        'vcan_name': vcan_name
    }
    pres = run_process(['bash', '-c',
        CHECK_VCAN_EXISTS_SCRIPT.format(**pargs)])
    return pres.out == 'yes'

def setup_vcans(vcan0, vcan1, vcan2):
    pargs = {
        'a': vcan0,
        'b': vcan1,
        'c': vcan2
    }
    pres = run_process(['bash', '-c',
        CREATE_VCANS_SCRIPT.format(**pargs)])
    return pres.out + ' ' + pres.err

def start_fwd_api(source_port, target_port):
    pargs = {
        'source_port': source_port,
        'target_port': target_port
    }
    pres = run_process(['bash', '-c', START_FWD_API_SCRIPT.format(**pargs)])
    return pres.out

def stop_fwd_api():
    pres = run_process(['bash', '-c', STOP_FWD_API_SCRIPT])
    return pres.out

def start_can_bridge(args):
    pargs = {
        'peer_ip': args.peer_ip,
        'peer_port': args.peer_port,
        'local_port': args.local_port
    }
    pres = run_process(['bash', 'c', START_CAN_BRIDGE_SCRIPT.format(**pargs)])
    return pres.out

def stop_can_brdige():
    pres = run_process(['bash'], '-c', STOP_CAN_BRIDGE_SCRIPT)
    return pres.out

def get_auto_vcan_name(peer_id, vcan_id):
    return 'vcan{}_{}'.format(peer_id, vcan_id)

def connect_peer_vcan(peer_id, peer_ip, vcan_id, vcan_name=''):
    logger = logging.getLogger('avrs')
    pargs = {
        'peer_id': peer_id,
        'peer_ip': peer_ip,
        'remote_port': 20000 + peer_id * 3 + vcan_id, # three ports per peer_id
        'local_port': 20000 + peer_id * 3 + vcan_id,
        'vcan_name': vcan_name if vcan_name != '' else get_auto_vcan_name(peer_id, vcan_id)
    }
    logger.info('connecting vcan with args: {}'.format(pargs))
    return run_process(['bash', '-c',
        CONNECT_PEER_VCAN_SCRIPT.format(**pargs)])

def get_local_instance_ip():
    try:
        pres = run_process(['bash', '-c', GET_EC2_LOCAL_IP_SCRIPT])
        if pres.out == '':
            return '127.0.0.1'
        return pres.out
    except:
        return '127.0.0.1'

def reset_race_cloud_connection():
    logger = logging.getLogger('avrs')
    logger.info('resetting connection')
    reset_rmw_qos()
    reset_rmw_cyclone_qos()
    logger.info('removing vcanlog and vcanlock files')
    run_process(['bash', '-c', 'rm ~/.simslot*']) # remove slot reservations
    run_process(['bash', '-c', 'rm ~/.*.vcanlog*']) # remove slot reservations
    run_process(['bash', '-c', 'rm ~/.*.vcanlock']) # remove lock files
    logger.info('stopping race-cloud bridge-can')
    bash_kill_process_by_launch_command('avrs race-cloud bridge-can')

def try_get_open_slot(team_name, ip):
    logger = logging.getLogger('avrs')
    slot_file_dir = os.environ['HOME']
    logger.info('finding a slot for team {}'.format(team_name))
    for i in range(12):
        slot_file_path = os.path.join(slot_file_dir, '.simslot_{}'.format(i))

        if os.path.isfile(slot_file_path):
            with open(slot_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if content == ip:
                    logger.info('slot {} already reserved by team {}'.format(i, team_name))
                    return (True, 'slot {} is already reserved by you'.format(i), i)
        else:
            with open(slot_file_path, 'w', encoding='utf-8') as f:
                f.write(ip)
                logger.info('slot {} successfuly reserved by team {}'.format(i, team_name))
                return (True, 'reserved slot {}'.format(i), i)
    logger.info('no open slot found for team {}'.format(team_name))
    return (False, 'no open slots', i)

def call_race_cloud_api(body):
    logger = logging.getLogger('avrs')
    logger.info('calling race-cloud api with body: {}'.format(body))

    api_url = 'gitzels0l7.execute-api.us-east-1.amazonaws.com'

    connection = http.client.HTTPSConnection(api_url)
    headers = {
        'Content-type': 'application/json',
        'x-api-key': '7aQ83sJ89Q2DZ8NdIi9aUTBuUS2uyix5QoDwrl1j'
    }
    body = json.dumps(body).encode('utf-8')
    connection.request('POST', '/beta/connect', body, headers)
    response = connection.getresponse()
    if response.status != 200:
        return (False, 'response had status code {}'.format(response))
    return (True, response.read().decode('utf-8'))

def get_api_script_response(raw):
    decoded = json.loads(raw)['body']
    logger = logging.getLogger('avrs')
    logger.info('race cloud api response: {}'.format(decoded))
    if decoded['script_response']['statusCode'] != 200:
        return (False, 'inner response had bad status code {}'.format(decoded))
    #print(decoded)
    return (True, json.loads(decoded['script_response']['body']), decoded['sim_private_ip'])