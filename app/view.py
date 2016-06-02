import os
import json
import datetime
from datetime import timedelta
import re
import random

from flask import Flask, request, jsonify, render_template
from flask_mail import Mail, Message

import daily
import monthly
import app_config
from model import Model

app = Flask(__name__,
            template_folder='./templates',
            static_folder='./static')
app.debug = True
app.config.update(dict(
    DEBUG=True,
    MAIL_SERVER=app_config.MAIL_SERVER,
    MAIL_PORT=app_config.MAIL_PORT,
    MAIL_USE_TLS=False,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=app_config.MAIL_USERNAME,
    MAIL_PASSWORD=app_config.MAIL_PASSWORD,
))
db = Model('pi_temps')
_last_alert = datetime.datetime(1970, 1, 1)  # default when app starts


@app.route('/')
def index():
    last_reading = db.get_last_reading()

    if last_reading:
        data = {
            'date': last_reading[1].strftime('%H:%M %d-%m-%Y'),
            'temp': str(last_reading[0])}
        return render_template('index.html', data=data)
    else:
        return render_template('index.html', data=None)


@app.route('/data', methods=['POST'])
def data():
    timestamp = datetime.datetime.now()

    if request.method == 'POST':
        try:
            decoded_data = json.loads(request.data.decode('utf-8'))
            temp = float(decoded_data['temp'])
            last_reading = db.get_last_reading()
            last_day = db.get_last_day()

            if last_reading:
                if last_reading[1].day != timestamp.day:
                    daily.run(db)

            if last_day:
                if last_day[0].month != timestamp.month:
                    monthly.run(db)

            db.store_temp([temp, decoded_data['ts']])

            global _last_alert
            if temp > -10 and timestamp - timedelta(hours=1) > _last_alert:
                    subject = 'ALERT'
                    body = ('The temperature is at ' + str(temp) + '\'C')
                    send_email(subject, body)
                    _last_alert = timestamp  # replaces time of last alert

        except Exception as e:
            with open(os.path.join(os.getcwd() + 'errorlog.txt'), 'a') as f:
                f.write('exception: ' + str(e) + '\n')
                f.close()

    return jsonify({'success': True})


@app.route('/batch', methods=['POST'])
def batch():
    if request.method == 'POST':
        try:
            decoded_data = json.loads(request.data.decode('utf-8'))
            for r in decoded_data:
                temp = float(r['temp'])
                db.store_temp([temp, r['ts']])

        except Exception as e:
            with open(os.path.join(os.getcwd() + 'errorlog.txt'), 'a') as f:
                f.write('exception: ' + str(e) + '\n')
                f.close()

    return jsonify({'success': True})


@app.route('/daygraph', methods=['GET'])
def twentyfour():
        data = db.last_24hrs()
        x = list()
        y = list()

        for d in data:
            x.append(d[1].strftime('%Y-%m-%d %H:%M:%S'))
            y.append(d[0])

        formatted_data = {
            'x': x,
            'y': y,
            'type': 'scatter'
        }
        return jsonify(formatted_data)


@app.route('/report/<month_year>', methods=['GET'])
def reports(month_year):
    pattern = re.compile(r'\A\d\d-\d\d\Z')
    if pattern.match(month_year):
        print('yay')
    else:
        print('boo')


def send_email(subject, body):
    mail_ext = Mail(app)
    mail_to_be_sent = Message(
        subject=subject,
        recipients=app_config.recipients,
        sender=app_config.sender)
    mail_to_be_sent.body = body
    mail_ext.send(mail_to_be_sent)


# Teardown function for when app context closes
def teardown_appcontext(e):
    if db is not None:
        db.close()

if app.debug:
    db = Model('test_db')
    db.store_temp([random.uniform(-30, 30), datetime.datetime.now()])
    db.insert_day([datetime.date.today(),
                   random.uniform(-30, 30),
                   random.uniform(-30, 30),
                   random.uniform(-30, 30)])
else:
    db = Model('pi_temps')
    import logging
    from logging import FileHandler
    file_handler = FileHandler('app.log')
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)

if __name__ == '__main__':
    app.run()
