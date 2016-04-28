from flask import Flask
from flask import request
import datetime
import sys
import json
import daily
import monthly
from model import Model

app = Flask(__name__)
app.debug=True
db = Model('pi_temps')


@app.route('/')
def splash():
    last_reading = db.get_last_reading()
    if last_reading:
        return str([last_reading[1].strftime('%H:%M %d-%m-%Y'), str(last_reading[0])])
    else:
        return 'empty db!'


@app.route('/data', methods=['POST'])
def data():
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
                if last_day[1].month != timestamp.month:
                    monthly.run(db)

            db.store_temp([temp, decoded_data['ts']])

        except Exception:
            print(sys.exc_info(), file=sys.stderr)

    return splash()


# Teardown function for when app context closes
def teardown_appcontext(e):
    if db is not None:
        db.close()

if __name__ == '__main__':
    app.run(debug=True)
