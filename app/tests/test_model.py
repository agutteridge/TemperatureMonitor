import unittest
from unittest import TestCase
import os
import datetime
from datetime import timedelta

from app import daily, model, monthly, app_config
from app.model import Model

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
        self.assertEqual(result, [22.2, 22.4, 22.3])

    def test_remove_old_readings(self):
        self.db_obj.store_temp([22.2, current_time])
        self.db_obj.store_temp([33.3, current_time - timedelta(days=2)])
        self.db_obj.remove_old_readings()
        result = self.db_obj.get_all_readings()
        self.assertEqual(result, [(22.2, current_time)])

    def test_insert_day(self):
        values = [yesterday.date(), 20.0, 21.0, 20.2]
        self.db_obj.insert_day(values)
        result = self.db_obj.get_all_days()

        self.assertEqual(result[0][0], yesterday.date())
        self.assertEqual(list(result[0][1:4]), [20.0, 21.0, 20.2])

    def test_remove_days(self):
        test_date = datetime.date(2016, 3, 24)
        values1 = [test_date, 19.0, 22.0, 20.5]
        self.db_obj.insert_day(values1)
        values2 = [datetime.date(1900, 1, 24), 0, 0, 0]
        self.db_obj.insert_day(values2)
        self.db_obj.remove_days('1900-01')
        result = self.db_obj.get_all_days()

        self.assertEqual(result[0][0], test_date)
        self.assertEqual(list(result[0][1:4]), [19.0, 22.0, 20.5])

    def test_prev_month(self):
        test_date = datetime.date(2016, 3, 24)
        values1 = [test_date, 19.0, 22.0, 20.5]
        self.db_obj.insert_day(values1)

        result = self.db_obj.get_month('2016-03')
        self.assertEqual(result[0][0], test_date)
        self.assertEqual(list(result[0][1:4]), [19.0, 22.0, 20.5])

    def test_minus_month(self):
        self.assertRaises(ValueError, monthly.minus_month, 99)

    def test_daily(self):
        self.db_obj.store_temp([-99, current_time])
        self.db_obj.store_temp([20, yesterday])
        self.db_obj.store_temp([21, yesterday])
        self.db_obj.store_temp([22, yesterday])
        self.db_obj.store_temp([99, current_time - timedelta(days=2)])

        daily.run(self.db_obj)
        in_days = self.db_obj.get_all_days()
        readings = self.db_obj.get_all_readings()
        self.assertEqual(in_days[0][0], yesterday.date())
        self.assertEqual(len(readings), 4)

    def test_monthly(self):
        for day in range(1, 30):
            values1 = [datetime.date(2016, 4, day), day, 22.0, 20.5]
            self.db_obj.insert_day(values1)

        monthly.run(self.db_obj)

    def tearDown(self):
        self.db_obj.delete()
        os.remove(os.getcwd() + '/test_db')

if __name__ == '__main__':
    unittest.main()
