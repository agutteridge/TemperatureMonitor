import requests_mock

import unittest
from unittest.mock import patch
from unittest import TestCase

import logger
import pi_config


class Test(TestCase):

    @patch('logger.read_temp_file', return_value=-20)
    def test_read_temp(self, read_temp_input):
        self.assertEqual(logger.read_temp(), -20)

    @patch('logger.read_temp_file')
    def test_read_temp_nodata(self, read_temp_input):
        read_temp_input.side_effect = Exception()
        self.assertEqual(logger.read_temp(), 'nodata')

    @patch('logger.log_temp')
    def test_log_temp_called(self, log_temp_input, pidb):
        with requests_mock.Mocker() as m:
            m.post(pi_config.post_single, text=False)
            logger.send_data(-20)
            self.assertEqual(logger.log_temp.call_count, 1)

if __name__ == '__main__':
    unittest.main()
