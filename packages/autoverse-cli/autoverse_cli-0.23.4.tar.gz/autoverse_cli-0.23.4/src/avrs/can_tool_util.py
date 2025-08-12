import can
import cantools
import time
import os
import datetime
import threading
import queue
import json
import math
import statistics

def get_eav24_hl0(throttle, gear, brake):
    return {
        "HL_TargetThrottle": throttle,
        "HL_TargetGear": gear,
        "HL_TargetPressure_RR": brake,
        "HL_TargetPressure_RL": brake,
        "HL_TargetPressure_FR": brake,
        "HL_TargetPressure_FL": brake,
        "HL_Alive_01": 0
    }

def get_eav24_hl2(steer):
    return {
        "HL_Alive_02": 0, 
        "HL_PSA_Profile_Vel_rad_s": 0,
        "HL_PSA_Profile_Dec_rad_s2": 0,
        "HL_PSA_Profile_Acc_rad_s2": 0,
        "HL_TargetPSAControl": steer,
        "HL_PSA_ModeOfOperation": 0
    }

def get_eav24_msigs(dbc, throttle, gear, brake, steer):
    return {
        dbc.get_message_by_name('HL_Msg_01'): get_eav24_hl0(throttle, gear, brake),
        dbc.get_message_by_name('HL_Msg_02'): get_eav24_hl2(steer)
    }

def send_eav24_can_values(can_name, dbc, throttle, gear, brake, steer, duration, rate = 100):
    with can.interface.Bus(can_name, bustype='socketcan') as bus:
        message_1 = dbc.get_message_by_name('HL_Msg_01')
        message_2 = dbc.get_message_by_name('HL_Msg_02')
        print('sending EAV24 CAN inputs on {} with throttle {}, gear {}, brake {}, steer {}, for {} seconds'.format(can_name, throttle, gear, brake, steer, duration))
        signals_1 = get_eav24_hl0(throttle, gear, brake)
        signals_2 = get_eav24_hl2(steer)

        msigs = get_eav24_msigs(dbc, throttle, gear, brake, steer)
        send_eav24_can_signals(bus, msigs, rate, duration)

def send_eav24_can_signals(bus, message_signals, rate, duration):
    start_time = time.time()
    while time.time() - start_time < duration:
        for msg, sig in message_signals.items():
            bus.send(can.Message(arbitration_id=msg.frame_id, data=msg.encode(sig), is_extended_id=False))
        time.sleep(1.0 / rate)

def test_eav24_can_latency(can_name, dbc, nsamples, send_rate, duration, save_report_as):
    with can.interface.Bus(can_name, bustype='socketcan') as bus:
        delays = []
        times = []

        for i in range(nsamples):
            print('test {}'.format(i))
            start_time = time.time()
            last_throttle_time = time.time()
            last_throttle_value = 50;

            msigs = get_eav24_msigs(dbc, last_throttle_value, 1, 0, 0)
            
            send_thread = threading.Thread(target=send_eav24_can_signals, args=(bus, msigs, send_rate, duration))
            send_thread.start()
            
            is_back_to_zero = False
            while not is_back_to_zero:
                message = bus.recv()
                if message is not None:
                    decoded = decode_can_message(dbc, message)
                    if decoded and decoded['name'] == 'ICE_Status_01':
                        ack_value = decoded['data']['ICE_TargetThrottle_ACK']
                        if math.isclose(ack_value, last_throttle_value):
                            t = time.time()
                            #print('got throttle ack matching command at t{}'.format(t - last_throttle_time))
                            delay = t - last_throttle_time
                            delays.append(delay)
                            times.append(t)
                            print('got throttle ack for command {} after {} seconds'.format(last_throttle_value, delay))
                            if last_throttle_value == 0:
                                is_back_to_zero = True
                                send_thread.join()
                            else:
                                last_throttle_value = 0
                                msigs = get_eav24_msigs(dbc, last_throttle_value, 1, 0, 0)
                                send_thread.join()
                                send_thread = threading.Thread(target=send_eav24_can_signals, args=(bus, msigs, send_rate, duration))
                                send_thread.start()
                            last_throttle_time = time.time()

        # Plot results
        avg_delay = statistics.mean(delays)
        print('avg delay {}, min delay {}, max dealy {}'.format(avg_delay, min(delays), max(delays)))

        if save_report_as != '':
            print('saving report to {}'.format(save_report_as))
            report = {
                'average_delay': avg_delay,
                'min_delay': min(delays),
                'max_delay': max(delays),
                'num_samples': nsamples
            }
            with open(save_report_as, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=4)


def echo_can(can_names, dbcs, duration, isolate, do_rates, save_report_as):
    start_time = time.time()
    report = {}
    rates = {}
    print_interval = 1.0
    last_print = start_time

    jobs = []
    print_lock = threading.Lock()
    for n in can_names:
        echo_thread = threading.Thread(target=echo_can_job, args=(n, dbcs, duration, isolate, do_rates, rates, print_lock))
        echo_thread.start()
        jobs.append(echo_thread)

    while time.time() - start_time < duration:
        t = time.time()
        if do_rates and t - last_print > print_interval:
            last_print = t
            for r in rates:
                print('{} rate: {}hz ({} samples)'.format(r, 1.0 / rates[r]['rate'], rates[r]['ct']))
            print('=' * 15)

    for j in jobs:
        j.join()
    
    if do_rates and save_report_as != '':
        print('saving report to {}'.format(save_report_as))
        with open(save_report_as, 'w', encoding='utf-8') as f:
            json.dump(rates, f, ensure_ascii=False, indent=4)

def echo_can_job(can_name, dbcs, duration, isolate, do_rates, out_rate_data, print_lock):
    start_time = time.time()
    with can.interface.Bus(can_name, bustype='socketcan') as bus:
        while time.time() - start_time < duration:
            message = bus.recv()
            if message is not None:
                for db in dbcs:
                    decoded = decode_can_message(db, message)
                    if decoded is not None and (len(isolate) == 0 or decoded['name'] in isolate):
                        update_can_rate_stats(decoded, out_rate_data, start_time)
                        if not do_rates and print_lock.acquire(True):
                            print(decoded)
                            print_lock.release()

def decode_can_message(dbc, message):
    try:
        decoded_message = dbc.decode_message(message.arbitration_id, message.data)
        message_name = dbc.get_message_by_frame_id(message.arbitration_id).name
        timestamp = datetime.datetime.now().isoformat()
        return {'timestamp': timestamp, 'name': message_name, 'data': decoded_message}
    except KeyError:
        return None
    
def update_can_rate_stats(message, rates, start_time):
    if not message['name'] in rates:
        rates[message['name']] = {
            'prev_t': start_time,
            'rate': time.time() - start_time,
            'ct': 0,
            'min': 100000000,
            'max': 0.0000001
        }
    r = rates[message['name']]['rate']
    t = rates[message['name']]['prev_t']
    ct = rates[message['name']]['ct'] + 1
    dt = time.time() - t
    rate_diff = dt - r
    rates[message['name']]['rate'] = r + (1.0 / ct) * rate_diff
    rates[message['name']]['ct'] = ct
    rates[message['name']]['prev_t'] = time.time()

    this_rate = 1.0 / dt
    if this_rate > rates[message['name']]['max']:
        rates[message['name']]['max'] = this_rate
    elif this_rate < rates[message['name']]['min']:
        rates[message['name']]['min'] = this_rate

