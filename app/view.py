import os
import json
import datetime
from datetime import timedelta
import re
import random

from flask import Flask, request, jsonify, render_template, send_file
from flask_mail import Mail, Message
from weasyprint import HTML
from jinja2 import Environment, PackageLoader

import daily, app_config
from model import Model
from month_data import Month_data

app = Flask(__name__,
            template_folder='./templates',
            static_folder='./static')
# app.debug = True
app.config.update(dict(
    MAIL_SERVER=app_config.MAIL_SERVER,
    MAIL_PORT=app_config.MAIL_PORT,
    MAIL_USE_TLS=False,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=app_config.MAIL_USERNAME,
    MAIL_PASSWORD=app_config.MAIL_PASSWORD,
))
jinja_env = Environment(loader=PackageLoader('view', 'templates'))
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
                    daily.run(db, last_reading, delete=True)

            if last_day:
                if last_day[0].month != timestamp.month:
                    monthly(last_day.strftime('%Y-%m'), db)

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


@app.route('/report/<year_month>', methods=['GET'])
def reports(year_month):
    pattern = re.compile(r'\A\d\d\d\d-\d\d\Z')
    if pattern.match(year_month):
        month_obj = Month_data(year_month)
        data = month_obj.get_days(db)
        if data:
            create_pdf(data, year_month)

            path = '%s/%s_log.pdf' % (app_config.output_path, year_month)
            if os.path.isfile(path):
                return send_file(path)

    return 'Not a month we have data for!'


def send_email(subject, body, pdf_path=""):
    mail_ext = Mail(app)
    mail_to_be_sent = Message(
        subject=subject,
        recipients=app_config.recipients,
        sender=app_config.sender)
    mail_to_be_sent.body = body

    if pdf_path:
        with app.open_resource(pdf_path) as fp:
            mail_to_be_sent.attach(pdf_path, "application/pdf", fp.read())

    mail_ext.send(mail_to_be_sent)


def create_pdf(data, year_month):
    template = jinja_env.get_template('log_template.html')
    pretty_month = datetime.datetime.strptime(
        year_month, '%Y-%m').strftime('%B %Y')
    html_out = template.render(data=data, month=pretty_month)
    HTML(string=html_out).write_pdf(
        '%s/%s_log.pdf' % (app_config.output_path, year_month))
    return True


def monthly(db, year_month):
    month_obj = Month_data(year_month)
    month_obj.get_days(db)
    create_pdf(data, year_month)
    path = '%s/%s_log.pdf' % (app_config.output_path, year_month)
    send_email('Monthly report', str(year_month), attach_pdf=path)


# Teardown function for when app context closes
def teardown_appcontext(e):
    if app.debug:
        db.delete()
    if db is not None:
        db.close()

if app.debug:
    db = Model('test_db')
    db.store_temp([random.uniform(-30, 30), datetime.datetime.now()])
else:
    db = Model('pi_temps')
    import logging
    from logging import FileHandler
    file_handler = FileHandler('app.log')
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)

if __name__ == '__main__':
    app.run()
