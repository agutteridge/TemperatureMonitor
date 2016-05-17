import os
import json
import datetime
import re
# Flask imports
from flask import Flask, request, jsonify, render_template
# module imports
import daily
import monthly
import app_config
from model import Model

app = Flask(__name__,
            template_folder='./templates',
            static_folder='./static')
db = Model('pi_temps')


@app.route('/')
def index():
    last_reading = db.get_last_reading()
    if last_reading:
        data = {
            'date': last_reading[1].strftime('%H:%M %d-%m-%Y'),
            'temp': str(last_reading[0])}
        return render_template('index.html', data=data)
    else:
        return 'empty db!'


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

        except Exception as e:
            with open(os.path.join(app_config.output_path + 'errorlog.txt'), 'a') as f:
                f.write('exception: ' + str(e) + '\n')
                f.close()

    return jsonify({'success': True})


@app.route('/report/<month_year>', methods=['GET'])
def reports(month_year):
    pattern = re.compile(r'\A\d\d-\d\d\Z')
    if pattern.match(month_year):
        print('yay')
    else:
        print('boo')


# Teardown function for when app context closes
def teardown_appcontext(e):
    if db is not None:
        db.close()

if not app.debug:
    import logging
    from logging import FileHandler
    file_handler = FileHandler('app.log')
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)

if __name__ == '__main__':
    app.run(debug=True)
