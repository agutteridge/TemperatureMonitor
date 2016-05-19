import datetime
from datetime import timedelta
import sendgrid

from model import Model
import app_config

db = Model('pi_temps')


def trigger_email(recipient_list,
                  subject,
                  text):
    # Set SendGrid API Key in config file
    sg = sendgrid.SendGridClient(app_config.sendgrid_key)
    message = sendgrid.Mail()

    for r in recipient_list:
        message.add_to(r)

    message.set_subject(subject)
    message.set_html(text)
    message.set_text(text)
    # Set sender address in config file. Format:
    # 'Santa <mrclaus@northpole.com>'
    message.set_from(app_config.sender)
    status, msg = sg.send(message)

if __name__ == '__main__':
    last_reading = db.get_last_reading()
    if last_reading:
        if last_reading[1] < datetime.datetime.now() - timedelta(hours=1):
            trigger_email([app_config.recipient1],
                          'ALERT: No reads in the last hour',
                          'Last read was %s\'C at %s' %
                          (str(last_reading[0]),
                           last_reading[1].strftime('%H:%M%p')))
