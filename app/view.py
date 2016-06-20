import os
import json
import datetime
from datetime import timedelta
import re

from flask import Flask, request, jsonify, render_template, send_file
from flask_mail import Mail, Message
from weasyprint import HTML
from jinja2 import Environment, PackageLoader
from apscheduler.schedulers.background import BackgroundScheduler

import app_config
from model import Model
from month_data import Month_data

app = Flask(__name__,
            template_folder='./templates',
            static_folder='./static')
app.debug = True
app.config.update(dict(
    TESTING=app.debug,
    MAIL_SERVER=app_config.MAIL_SERVER,
    MAIL_PORT=app_config.MAIL_PORT,
    MAIL_USE_TLS=False,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=app_config.MAIL_USERNAME,
    MAIL_PASSWORD=app_config.MAIL_PASSWORD,
))
loader = PackageLoader('view', 'templates')
jinja_env = Environment(loader=loader)
_last_alert = datetime.datetime(1970, 1, 1)  # default when app starts


@app.route('/')
def index():
    last_reading = db.get_last_reading()

    if last_reading:
        data = {
            'date': last_reading[1],
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
            raise Exception

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
    current_time = datetime.datetime.now()
    yesterday = current_time - timedelta(days=1)
    data = db.get_readings(yesterday, current_time)
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


@app.route('/monthgraph/data', methods=['GET'])
def monthgraph():
    this_month = Month_data(datetime.date.today().strftime('%Y-%m'))
    data = this_month.get_days(db)
    dates = list()
    mins = list()
    maxs = list()
    means = list()

    for d in data:
        dates.append(d[0])
        mins.append(d[1])
        maxs.append(d[2])
        means.append(d[3])

    formatted_data = {
        'dates': dates,
        'mins': mins,
        'maxs': maxs,
        'means': means
    }
    return jsonify(formatted_data)


@app.route('/monthgraph', methods=['GET'])
def pic():
    return render_template('monthgraph.html')


@app.route('/reports', methods=['GET'])
def reports_main():
    data = {
        'year': datetime.date.today().year
    }
    return render_template('reports.html', data=data)


@app.route('/reports/<year_month>', methods=['GET'])
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
            else:
                raise Exception('no pdf')

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


# # Checks to see if it is the first day of the month
def check_monthly():
    today = datetime.date.today()

    if today.day == 1:
        monthly()


# # Sends monthly report
def monthly():
    this_month = Month_data(datetime.date.today().strftime('%Y-%m'))
    last_month = this_month.timedelta(1)
    last_month.get_days(db)

    # month_before_last = last_month.timedelta(1)
    # month_before_last.spring_clean(db)

    create_pdf(data, last_month.string)
    path = '%s/%s_log.pdf' % (app_config.output_path, last_month.string)
    send_email('Monthly report', last_month.string, attach_pdf=path)


# # Teardown function for when app context closes
def teardown_appcontext(e):
    if app.debug:
        db.delete()
    if db is not None:
        db.close()

if app.debug:
    db = Model('test_db')
else:
    db = Model('pi_temps')
    import logging
    from logging import FileHandler
    file_handler = FileHandler('app.log')
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)

    # # Schedules check_monthly to be executed once per day
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_monthly, 'interval', days=1)
    scheduler.start()

if __name__ == '__main__':
    app.run()
