import unittest
from unittest import TestCase
import os
import datetime
from datetime import timedelta

import daily, model, app_config
from model import Model

current_time = datetime.datetime.now()
yesterday = current_time - timedelta(days=1)


class Test(TestCase):

    def setUp(self):
        self.db_obj = Model('test_db')

    def test_store_temp(self):
        self.db_obj.store_temp([22.2, current_time])
        result = self.db_obj.get_all_readings()
        self.assertEqual(result[0], (22.2, current_time))

    def test_last_24hrs(self):
        self.db_obj.store_temp([22.2, current_time])
        self.db_obj.store_temp([33.3, yesterday - timedelta(seconds=1)])
        result = self.db_obj.last_24hrs()
        self.assertEqual(result, [(22.2, current_time)])

    def test_get_last_reading(self):
        self.db_obj.store_temp([22.2, current_time])
        self.db_obj.store_temp([22.2, yesterday])
        result = self.db_obj.get_last_reading()
        self.assertEqual(result, (22.2, current_time))

    def test_min_max_mean(self):
        self.db_obj.store_temp([22.2, current_time])
        self.db_obj.store_temp([22.4, current_time])
        rows = self.db_obj.last_24hrs()
        result = daily.min_max_mean(rows)
        self.assertEqual(result, (22.2, 22.4, 22.3))

    def test_delete_readings(self):
        self.db_obj.store_temp([22.2, current_time])
        self.db_obj.store_temp([33.3, yesterday])
        self.db_obj.delete_readings(yesterday.strftime('%Y-%m-%d'))
        result = self.db_obj.get_all_readings()
        self.assertEqual(result, [(22.2, current_time)])

    def test_insert_day(self):
        values = [yesterday.date(), 20.0, 21.0, 20.2]
        self.db_obj.insert_day(values)
        result = self.db_obj.get_all_days()

        self.assertEqual(result[0][0], yesterday.date())
        self.assertEqual(list(result[0][1:4]), [20.0, 21.0, 20.2])

    def test_get_all_days(self):
        test_date = datetime.date(2016, 3, 24)
        values1 = [test_date, 19.0, 22.0, 20.5]
        self.db_obj.insert_day(values1)
        values2 = [datetime.date(1900, 1, 24), 0, 0, 0]
        self.db_obj.insert_day(values2)
        self.db_obj.remove_days('1900-01')
        result = self.db_obj.get_all_days()

        self.assertEqual(result[0][0], test_date)
        self.assertEqual(list(result[0][1:4]), [19.0, 22.0, 20.5])

    def test_get_month(self):
        test_date = datetime.date(2016, 3, 24)
        values1 = [test_date, 19.0, 22.0, 20.5]
        self.db_obj.insert_day(values1)

        result = self.db_obj.get_month('2016-03')
        self.assertEqual(result[0][0], test_date)
        self.assertEqual(list(result[0][1:4]), [19.0, 22.0, 20.5])

    def test_daily(self):
        self.db_obj.store_temp([9, current_time])
        self.db_obj.store_temp([20, yesterday])

        daily.run(self.db_obj, yesterday)
        in_days = self.db_obj.get_all_days()
        readings = self.db_obj.get_all_readings()
        print(in_days)
        self.assertEqual(in_days[0][0], yesterday.date())
        self.assertEqual(readings[0][1], current_time)

    def test_daily_nodata(self):
        result = daily.run(self.db_obj, yesterday)
        self.assertEqual(result[0][1], 'no data')

    def tearDown(self):
        self.db_obj.delete()
        os.remove(os.getcwd() + '/test_db')

if __name__ == '__main__':
    unittest.main()
