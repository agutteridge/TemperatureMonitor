import os
import unittest
import datetime
from datetime import timedelta
import json
from unittest.mock import patch

import view
import app_config

current_time = datetime.datetime.now().replace(microsecond=0)


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        view.app.debug = True
        view.db.__init__('test_db')
        self.app = view.app.test_client()

    def tearDown(self):
        view.db.delete()
        if os.path.isfile(
                os.path.join(app_config.output_path, '1970-01_log.pdf')):
            print('removing file')
            os.remove(os.path.join(app_config.output_path, '1970-01_log.pdf'))

    def test_empty_db(self):
        rv = self.app.get('/')
        self.assertTrue(
            b'Uh-oh, the database appears to be empty..?!' in rv.data)

    def test_index(self):
        view.db.store_temp([-22.2, current_time])
        rv = self.app.get('/')
        self.assertFalse(
            b'Uh-oh, the database appears to be empty..?!' in rv.data)

    def test_post(self):
        r = self.app.post('/data', data=json.dumps({
            'temp': -20,
            'ts': current_time.strftime('%Y-%m-%d %H:%M:%S')}))
        self.assertEqual(r.status_code, 200)
        # Testing entry into db
        result = view.db.get_all_readings()
        self.assertEqual(result[0], (-20, current_time))

    @patch('view.send_email')
    def test_alert(self, email):
        r = self.app.post('/data', data=json.dumps({
            'temp': 20,
            'ts': current_time.strftime('%Y-%m-%d %H:%M:%S')}))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(b'"success": true' in r.data)
        self.assertTrue(email.called)

    @patch('view.send_email')
    def test_alert_no_email(self, email):
        view._last_alert = current_time  # manually changing time of last alert
        r = self.app.post('/data', data=json.dumps({
            'temp': 20,
            'ts': current_time.strftime('%Y-%m-%d %H:%M:%S')}))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(email.called)

    def test_batch(self):
        rows = list()
        for f in range(0, 10):
            t = (current_time - timedelta(hours=f)).strftime('%Y-%m-%d %H:%M:%S')
            rows.append({
                'temp': f,
                'ts': t})
        r = self.app.post('/batch', data=json.dumps(rows))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(b'"success": true' in r.data)
        # Testing entry into db
        result = view.db.get_all_readings()
        self.assertEqual(len(result), 10)

    def test_report_no_data(self):
        r = self.app.get('/reports/1970-01')
        self.assertTrue(b'Not a month we have data for!' in r.data)

    def test_report_one_reading(self):
        test_date = datetime.datetime(1970, 1, 1, 12, 0, 0)
        date_str = test_date.strftime('%Y-%m-%d %H:%M:%S')
        r = self.app.post('/data', data=json.dumps({
            'temp': -20,
            'ts': date_str}))

        r = self.app.get('/reports/1970-01')
        self.assertEqual(r.mimetype, 'application/pdf')

if __name__ == '__main__':
    unittest.main()
