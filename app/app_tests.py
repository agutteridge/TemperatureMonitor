import unittest
from unittest import TestCase

import datetime
from datetime import timedelta

import daily
import monthly
from model import Model

current_time = datetime.datetime.now()


class Test(TestCase):

    def setUp(self):
        self.db_obj = Model('test_db')

    def test_store_temp(self):
        self.db_obj.store_temp([22.2, current_time])
        result = self.db_obj.get_all_readings()
        assert(result[0] == (22.2, current_time))

    def test_last_24hrs(self):
        self.db_obj.store_temp([22.2, current_time])
        self.db_obj.store_temp(
            [22.2,
             current_time - timedelta(hours=25)])
        result = self.db_obj.last_24hrs()
        assert(result == [(22.2, current_time)])

    def test_last_24hrs_empty(self):
        self.db_obj.store_temp(
            [22.2,
             current_time - timedelta(hours=25)])
        result = self.db_obj.last_24hrs()
        assert(result == [])

    def test_get_last_reading(self):
        self.db_obj.store_temp([22.2, current_time])
        self.db_obj.store_temp(
            [22.2,
             current_time - timedelta(hours=25)])
        result = self.db_obj.get_last_reading()
        assert(result == (22.2, current_time))

    def test_min_max_mean(self):
        self.db_obj.store_temp([22.2, current_time])
        self.db_obj.store_temp([22.4, current_time])
        rows = self.db_obj.last_24hrs()
        result = daily.min_max_mean(rows)
        assert(result == [22.2, 22.4, 22.3])

    def test_insert_day(self):
        yesterday = (
            datetime.date.today() -
            timedelta(days=1)).strftime('%Y-%m-%d')
        values = [yesterday, 20.0, 21.0, 20.2]
        self.db_obj.insert_day(values)
        result = self.db_obj.get_all_days()
        assert(result[0][0].strftime('%Y-%m-%d') == yesterday)
        assert(list(result[0][1:4]) == [20.0, 21.0, 20.2])

    def test_remove_dby(self):
        self.db_obj.store_temp([22.2, current_time])
        self.db_obj.store_temp(
            [22.2,
             current_time - timedelta(days=2)])
        self.db_obj.remove_dby()
        result = self.db_obj.get_all_readings()
        assert(result == [(22.2, current_time)])

    # This test might fail on the first few days of some months!
    def test_prev_month(self):
        dt = (datetime.date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
        data1 = [dt, 20.0, 21.0, 20.3]
        self.db_obj.insert_day(data1)

        today = datetime.date.today().strftime('%Y-%m-%d')
        data2 = [today, 20.0, 21.0, 20.3]
        self.db_obj.insert_day(data2)

        b = (datetime.date.today() - timedelta(days=300)).strftime('%Y-%m-%d')
        data3 = [b, 20.0, 21.0, 20.3]
        self.db_obj.insert_day(data3)

        result = self.db_obj.prev_month(monthly.minus_month(1))
        assert(result[0][0].strftime('%Y-%m-%d') == dt)
        assert(list(result[0][1:4]) == [20.0, 21.0, 20.3])

    def test_minus_month(self):
        self.assertRaises(ValueError, monthly.minus_month, 99)

    def test_remove_mbl(self):
        dt = (datetime.date.today() - timedelta(days=60)).strftime('%Y-%m-%d')
        data1 = [dt, 20.0, 21.0, 20.3]
        self.db_obj.insert_day(data1)

        today = datetime.date.today().strftime('%Y-%m-%d')
        data2 = [today, 20.0, 21.0, 20.3]
        self.db_obj.insert_day(data2)

        self.db_obj.remove_mbl(monthly.minus_month(2))
        result = self.db_obj.get_all_days()
        assert(result[0][0].strftime('%Y-%m-%d') == today)
        assert(list(result[0][1:4]) == [20.0, 21.0, 20.3])

    def tearDown(self):
        del self.db_obj

if __name__ == '__main__':
    unittest.main()
