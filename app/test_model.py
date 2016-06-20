import unittest
from unittest import TestCase
import os
import datetime
from datetime import timedelta

import day_data, model, app_config
from model import Model
from month_data import Month_data

current_time = datetime.datetime.now().replace(microsecond=0)
yesterday = current_time - timedelta(days=1)


class Test(TestCase):

    def setUp(self):
        self.db_obj = Model('test_db')

    def tearDown(self):
        self.db_obj.delete()

    # MODEL #
    def test_store_temp(self):
        self.db_obj.store_temp([22.2, current_time])
        result = self.db_obj.get_all_readings()
        self.assertEqual(result[0], (22.2, current_time))

    def test_last_24hrs(self):
        self.db_obj.store_temp([22.2, current_time])
        self.db_obj.store_temp([33.3, yesterday - timedelta(seconds=1)])
        result = self.db_obj.get_readings(yesterday, current_time)
        self.assertEqual(result, [(22.2, current_time)])

    def test_get_last_reading(self):
        self.db_obj.store_temp([22.2, current_time])
        self.db_obj.store_temp([22.2, yesterday])
        result = self.db_obj.get_last_reading()
        self.assertEqual(result, (22.2, current_time))

    def test_delete_readings(self):
        self.db_obj.store_temp([22.2, current_time])
        self.db_obj.store_temp([33.3, yesterday])
        (start, end) = day_data.first_last(yesterday, yesterday)
        self.db_obj.delete_readings(start, end)
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
        result = self.db_obj.get_all_days()

        self.assertEqual(result[1][0], test_date)
        self.assertEqual(list(result[1][1:4]), [19.0, 22.0, 20.5])

    def test_get_month(self):
        month_obj = Month_data('2016-03')
        test_date = datetime.date(2016, 3, 24)
        values1 = [test_date, 19.0, 22.0, 20.5]
        self.db_obj.insert_day(values1)
        result = self.db_obj.get_days(month_obj.start, month_obj.end)
        self.assertEqual(result[0][0], test_date)
        self.assertEqual(list(result[0][1:4]), [19.0, 22.0, 20.5])

    # DAY_DATA #
    def test_condense(self):
        self.db_obj.store_temp([9, current_time])
        self.db_obj.store_temp([20, yesterday])

        day_data.condense(self.db_obj, yesterday.date())
        in_days = self.db_obj.get_all_days()
        readings = self.db_obj.get_all_readings()
        self.assertEqual(in_days[0][0], yesterday.date())
        self.assertEqual(readings[0][1], current_time)

    def test_condense_nodata(self):
        result = day_data.condense(self.db_obj, yesterday.date())
        self.assertEqual(result[0][1], 'no data')

    def test_min_max_mean(self):
        self.db_obj.store_temp([22.2, current_time])
        self.db_obj.store_temp([22.4, current_time])
        rows = self.db_obj.get_readings(yesterday, current_time)
        result = day_data.min_max_mean(rows)
        self.assertEqual(result, [22.2, 22.4, 22.3])

    # MONTH_DATA #
    def test_check_days(self):
        test_date = datetime.datetime(1970, 1, 1)
        self.db_obj.store_temp([22.2, test_date])
        month_obj = Month_data(test_date.strftime('%Y-%m'))
        result = month_obj._check_days(self.db_obj)
        self.assertEqual(len(result), month_obj.num_days)

    def test_get_days(self):
        test_date = datetime.datetime(1970, 1, 1)
        self.db_obj.store_temp([22.2, test_date])
        month_obj = Month_data(test_date.strftime('%Y-%m'))
        result = month_obj.get_days(self.db_obj)
        self.assertEqual(len(result), month_obj.num_days)

if __name__ == '__main__':
    unittest.main()
