import unittest
from unittest.mock import patch
from unittest import TestCase
import os
import json
import datetime
from datetime import timedelta

import logger, pi_db, pi_config


class FakeResponse:

    def __init__(self):
        text = dict()
        text['success'] = True
        self.text = json.dumps(text)


class Test(TestCase):

    def setUp(self):
        self.db_obj = pi_db.Pidb('pi_db')

    @patch('logger.read_temp_file',
           return_value=('67 01 4b 46 7f ff 09 10 3b : crc=3b YES\n' +
                         '67 01 4b 46 7f ff 09 10 3b t=22000'))
    def test_read_temp_success(self, read_temp_input):
        self.assertEqual(logger.read_temp(), 22.0)

    @patch('logger.read_temp_file')
    def test_read_temp_fail(self, read_temp_input):
        read_temp_input.side_effect = Exception()
        self.assertEqual(logger.read_temp(), 'nodata')

    @patch('logger.requests.post', return_value=FakeResponse())
    @patch('logger.log_error')
    def test_single_success(self, post_input, error_input):
        logger.send_data(-25.0)
        result = self.db_obj.get_all_readings()
        self.assertEqual(logger.log_error.call_count, 0)
        self.assertEqual(logger.requests.post.call_count, 1)
        self.assertEqual(result, [])

    @patch('logger.requests.post', return_value=False)
    @patch('logger.log_error')
    def test_single_fail(self, post_input, error_input):
        logger.send_data(-25.0)
        self.assertEqual(logger.log_error.call_count, 1)
        result = self.db_obj.get_all_readings()
        self.assertEqual(result[0][0], -25.0)

    @patch('logger.requests.post', return_value=FakeResponse())
    @patch('logger.log_error')
    def test_multi_success(self, post_input, error_input):
        fake_date = (datetime.datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        self.db_obj.store_temp([-18.0, fake_date])
        result = self.db_obj.get_all_readings()
        self.assertEqual(result[0][0], -18.0)

        logger.send_data(-25.0)
        self.assertEqual(logger.requests.post.call_count, 2)
        result = self.db_obj.get_all_readings()
        self.assertEqual(logger.log_error.call_count, 0)
        self.assertEqual(result, [])

    def tearDown(self):
        self.db_obj.delete()
        os.remove(os.getcwd() + '/pi_db')


if __name__ == '__main__':
    unittest.main()
