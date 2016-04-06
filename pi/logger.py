# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Temperature Logger for a Raspberry Pi
# Reads temperature from a sensor and sends to an external source
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import datetime
import config
import sendgrid

# Global var for timestamp
timestamp = datetime.datetime.now()


def read_temp_file():
    # Set sensor ID in config file
    tfile = open('/sys/bus/w1/devices/' +
                 config.sensor_id +
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
            recipient_list = [config.recipient1]
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
    sg = sendgrid.SendGridClient(config.sendgrid_key)
    message = sendgrid.Mail()

    for r in recipient_list:
        message.add_to(r)

    message.set_subject(subject)
    message.set_html(text)
    message.set_text(text)
    # Set sender address in config file. Format:
    # 'Santa <mrclaus@northpole.com>'
    message.set_from(config.sender)
    status, msg = sg.send(message)


def send_data(temp):
    try:
        raise Exception()
    # If temperature is not successfully sent, it is recorded in logfile
    # An email is also sent
    except Exception:
        log_temp(temp)
        # Set recipient addresses in config file. Format:
        # 'Santa <mrclaus@northpole.com>'
        recipient_list = [config.recipient1]
        subject = 'RASPBERRY PI ERROR'
        text = ('The Raspberry Pi could not complete a temperature read.')

        trigger_email(recipient_list,
                      subject,
                      text)


def log_temp(temp):
    with open('/home/pi/TemperatureLogger/output/templog.txt', 'a') as logfile:
        # example: 1999-12-31 23:59:59    -20.2
        timestamp_string = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        logfile.write(timestamp_string +
                      '\t' +
                      str(temp) +
                      '\n')
        logfile.close()


def main():
    temp = read_temp()
    send_data(temp)

if __name__ == '__main__':
    main()
