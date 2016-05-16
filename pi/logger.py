# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Temperature Logger for a Raspberry Pi
# Reads temperature from a sensor and sends to an external source
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import datetime
import pi_config
import sendgrid
import requests
import argparse
import json

# Global var for timestamp
timestamp = datetime.datetime.now()
timestamp_string = timestamp.strftime('%Y-%m-%d %H:%M:%S')


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

        if temp > -10:  # Change this value as required
            # Set recipient addresses in config file. Format:
            # 'Santa <mrclaus@northpole.com>'
            recipient_list = [pi_config.recipient1]
            subject = 'ALERT'
            text = ('The temperature is at ' + str(temp) + '\'C')

            trigger_email(recipient_list,
                          subject,
                          text)

        return temp

    except Exception:
        return 'nodata'


def trigger_email(recipient_list,
                  subject,
                  text):
    # Set SendGrid API Key in config file
    sg = sendgrid.SendGridClient(pi_config.sendgrid_key)
    message = sendgrid.Mail()

    for r in recipient_list:
        message.add_to(r)

    message.set_subject(subject)
    message.set_html(text)
    message.set_text(text)
    # Set sender address in config file. Format:
    # 'Santa <mrclaus@northpole.com>'
    message.set_from(pi_config.sender)
    status, msg = sg.send(message)


def send_data(temp):
    try:
        r = requests.post(
            pi_config.server_ip,
            data=(json.dumps({'temp': temp, 'ts': timestamp_string})))
    # If temperature is not successfully sent, it is recorded in logfile
    # An email is also sent
    except Exception as e:
        log_temp(temp, e)
        # Set recipient addresses in config file. Format:
        # 'Santa <mrclaus@northpole.com>'
        recipient_list = [pi_config.recipient1]
        subject = 'RASPBERRY PI ERROR'
        text = ('The Raspberry Pi could not complete a temperature read.\n' +
                str(e) + '\n' +
                'The last recorded temperature was ' + str(temp) + '.')

        trigger_email(recipient_list,
                      subject,
                      text)


def log_temp(temp, e):
    with open('/home/pi/TemperatureMonitor/output/templog.txt', 'a') as logfile:
        # example: 1999-12-31 23:59:59    -20.2
        logfile.write(timestamp_string +
                      '\t' +
                      str(temp) +
                      '\n')
        logfile.close()

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
