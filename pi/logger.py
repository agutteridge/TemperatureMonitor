# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Temperature Logger for a Raspberry Pi
# Reads temperature from a sensor and sends to an external source
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import datetime
import requests
import argparse
import json

from pi_db import Pidb
import pi_config

# Global var for timestamp
timestamp = datetime.datetime.now()
timestamp_string = timestamp.strftime('%Y-%m-%d %H:%M:%S')
db = Pidb('pi_db')


def read_temp_file():
    # Set sensor ID in config file
    tfile = open('/sys/bus/w1/devices/' +
                 pi_config.sensor_id +
                 '/w1_slave')
    temp_data = tfile.read()
    tfile.close()
    # Example format (t=temp):
    # 67 01 4b 46 7f ff 09 10 3b : crc=3b YES
    # 67 01 4b 46 7f ff 09 10 3b t=22437
    second_line = temp_data.split('\n')[1]
    temp_value = second_line.split(' ')[9]
    temp = float(temp_value[2:]) / 1000
    return temp


def read_temp():
    temp = 999

    try:
        temp = read_temp_file()
        return temp

    except Exception:
        return 'nodata'


def send_data(temp):
    try:
        # send most recent reading
        single_r = requests.post(
            pi_config.post_single,
            data=(json.dumps({'temp': temp, 'ts': timestamp_string})))

        if not single_r.data.decode('utf-8')['success']:
            raise Exception('success not received (single)')

        # rows in db that need to be sent
        rows = db.get_all_readings()
        if rows:
            multi_r = requests.post(
                pi_config.post_multiple,
                data=(json.dumps(rows)))

            # Data sent successfully
            if multi_r.data.decode('utf-8')['success']:
                db.delete()
            else:
                raise Exception('success not received (multi)')

    # If temperature is not successfully sent, it is stored in local db
    # an error log is also written to
    except Exception as e:
        log_temp(temp, e)


def log_temp(temp, e):
    db.store_temp([temp, timestamp_string])

    with open('/home/pi/TemperatureMonitor/output/errorlog.txt', 'a') as ef:
        # example: 1999-12-31 23:59:59    -20.2
        ef.write(str(e) + '\n')
        ef.close()


def main(shell_args):
    if shell_args.debug:
        send_data(-18.0)
    else:
        temp = read_temp()
        send_data(temp)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="--debug to supply dummy temp.")
    parser.add_argument("--debug", required=False,
                        action='store_true')
    args = parser.parse_args()
    main(args)
