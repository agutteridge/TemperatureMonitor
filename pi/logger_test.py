import unittest
from unittest.mock import patch
from unittest import TestCase
import logger


class Test(TestCase):

    @patch('logger.read_temp_file', return_value=-20)
    def test_read_temp(self, read_temp_input):
        self.assertEqual(logger.read_temp(), -20)

    @patch('logger.read_temp_file', return_value=20)
    @patch('logger.trigger_email')
    def test_read_temp_over_maximum(self, read_temp_input, email_input):
        logger.read_temp()
        assert logger.trigger_email.call_count == 1

    @patch('logger.read_temp_file')
    def test_read_temp_nodata(self, read_temp_input):
        read_temp_input.side_effect = Exception()
        self.assertEqual(logger.read_temp(), 'nodata')

    @patch('logger.read_temp', return_value=-20)
    @patch('logger.send_data')
    def test_main(self, read_temp_input, send_data_input):
        logger.main()
        assert logger.read_temp.call_count == 1
        assert logger.send_data.call_count == 1

    @patch('logger.log_temp')
    def test_log_temp_called(self, log_temp_input):
        logger.send_data(-20)
        # make sure send_data doesn't send after Exception removed
        assert logger.log_temp.call_count == 1


if __name__ == '__main__':
    unittest.main()
