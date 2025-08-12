import can
import argparse
import socket
import struct
import logging

BUFFER_SIZE = 512

CAN_FRAME_FORMATS = [
    '=H', # 0 bytes should never happen
    '=HB',
    '=HBB',
    '=HBBB',
    '=HBBBB',
    '=HBBBBB',
    '=HBBBBBB',
    '=HBBBBBBB',
    '=HBBBBBBBB'
]

class UdpTxCanListener(can.Listener):
    def __init__(self, target_port, target_ip):
        self.target_port = target_port
        self.target_ip = target_ip
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def on_message_received(self, msg):
        #print('l got m {}'.format(msg))

        # we are getting data that is not 8 bytes (dlc probably not 8) so 
        # we need to zero-bad or something
        data = struct.pack(CAN_FRAME_FORMATS[len(msg.data)], msg.arbitration_id, *msg.data)
        self.s.sendto(data, (self.target_ip, self.target_port))

def can_bridge_loop(args):
    logger = logging.getLogger('avrs')
    logger.info('starting can bridge tx on {} to {}:{} (listen on {})'.format(
        args.vcan_name, args.peer_ip, args.peer_port, args.local_port))
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #s.settimeout(0.1)
        s.bind(('', args.local_port))
        with can.interface.Bus(args.vcan_name, interface='socketcan') as bus:
            l = UdpTxCanListener(args.peer_port, args.peer_ip)
            can.Notifier(bus, [l])
            while True:
                try:
                    data, server = s.recvfrom(BUFFER_SIZE)

                    l = len(data)

                    # ensure data is expected size
                    if l > 10 or l < 2:
                        continue

                    #print('got udp data {}'.format(data))
                    up = struct.unpack(CAN_FRAME_FORMATS[l - 2], data)

                    tx_msg = can.Message(
                        arbitration_id=up[0], 
                        data=up[1:], 
                        is_extended_id=False, 
                        dlc=l - 2) # len is rx size - 1 bc we add id to front

                    bus.send(tx_msg)
                except Exception as e:
                    logger.error('can bridge error: {}'.format(e))
                    break
    except Exception as e:
        logger.error('can bridge setup error: {}'.format(e))
        return

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='canbridge',
        description='can bridge')

    vcan_name_psr = parser.add_argument(
        'vcan_name')

    peer_ip_psr = parser.add_argument(
        'peer_ip')

    peer_port_psr = parser.add_argument(
        'peer_port',
        type=int)

    peer_port_psr = parser.add_argument(
        'local_port',
        type=int)

    version_psr = parser.add_argument(
        '--peer_ip', 
        help='')

    parser.set_defaults(func=bridge_loop)

    args = parser.parse_args()
    args.func(args)