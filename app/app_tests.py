import unittest
from unittest import TestCase
import datetime
from datetime import timedelta
import model, daily, monthly

current_time = datetime.datetime.now()


class Test(TestCase):

    def setUp(self):
        self.test_db = model.init_db('test_db')

    def test_store_temp(self):
        model.store_temp(self.test_db, [22.2, current_time])
        c = self.test_db.cursor()
        c.execute('''SELECT * FROM Readings''')
        result = c.fetchone()
        assert(result == (22.2, current_time))

    def test_last_24hrs(self):
        model.store_temp(self.test_db, [22.2, current_time])
        model.store_temp(
            self.test_db, [
                22.2,
                current_time - timedelta(hours=25)])
        result = model.last_24hrs(self.test_db)
        assert(result == [(22.2, current_time)])

    def test_last_24hrs_empty(self):
        model.store_temp(
            self.test_db, [
                22.2,
                current_time - timedelta(hours=25)])
        result = model.last_24hrs(self.test_db)
        assert(result == [])

    def test_get_last_reading(self):
        model.store_temp(self.test_db, [22.2, current_time])
        model.store_temp(
            self.test_db, [
                22.2,
                current_time - timedelta(hours=25)])
        result = model.get_last_reading(self.test_db)
        assert(result == (22.2, current_time))

    def test_min_max_mean(self):
        model.store_temp(self.test_db, [22.2, current_time])
        model.store_temp(self.test_db, [22.4, current_time])
        rows = model.last_24hrs(self.test_db)
        result = daily.min_max_mean(rows)
        assert(result == [22.2, 22.4, 22.3])

    def test_insert_day(self):
        yesterday = (
            datetime.date.today() -
            timedelta(days=1)).strftime('%Y-%m-%d')
        values = [yesterday, 20.0, 21.0, 20.2]
        daily.insert_day(self.test_db, values)
        c = self.test_db.cursor()
        c.execute('''SELECT * FROM Days''')
        result = c.fetchone()
        c.close()
        assert(result[0].strftime('%Y-%m-%d') == yesterday)
        assert(list(result[1:4]) == [20.0, 21.0, 20.2])

    def test_remove_dby(self):
        model.store_temp(self.test_db, [22.2, current_time])
        model.store_temp(
            self.test_db, [
                22.2,
                current_time - timedelta(days=2)])
        daily.remove_dby(self.test_db)
        c = self.test_db.cursor()
        c.execute('''SELECT * FROM Readings''')
        result = c.fetchall()
        assert(result == [(22.2, current_time)])

    # This test might fail on the first few days of some months!
    def test_prev_month(self):
        dt = (datetime.date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
        data1 = [dt, 20.0, 21.0, 20.3]
        daily.insert_day(self.test_db, data1)

        today = datetime.date.today().strftime('%Y-%m-%d')
        data2 = [today, 20.0, 21.0, 20.3]
        daily.insert_day(self.test_db, data2)

        b = (datetime.date.today() - timedelta(days=300)).strftime('%Y-%m-%d')
        data3 = [b, 20.0, 21.0, 20.3]
        daily.insert_day(self.test_db, data3)

        result = monthly.prev_month(self.test_db)
        assert(result[0][0].strftime('%Y-%m-%d') == dt)
        assert(list(result[0][1:4]) == [20.0, 21.0, 20.3])

    def test_minus_month(self):
        self.assertRaises(ValueError, monthly.minus_month, 99)

    def test_remove_mbl(self):
        dt = (datetime.date.today() - timedelta(days=60)).strftime('%Y-%m-%d')
        data1 = [dt, 20.0, 21.0, 20.3]
        daily.insert_day(self.test_db, data1)

        today = datetime.date.today().strftime('%Y-%m-%d')
        data2 = [today, 20.0, 21.0, 20.3]
        daily.insert_day(self.test_db, data2)

        result = monthly.remove_mbl(self.test_db)
        c = self.test_db.cursor()
        c.execute('''SELECT * FROM Days''')
        result = c.fetchall()
        assert(result[0][0].strftime('%Y-%m-%d') == today)
        assert(list(result[0][1:4]) == [20.0, 21.0, 20.3])

    def tearDown(self):
        c = self.test_db.cursor()
        c.execute('''DROP TABLE IF EXISTS Readings''')
        c.execute('''DROP TABLE IF EXISTS Days''')
        self.test_db.commit()
        self.test_db.close()


if __name__ == '__main__':
    unittest.main()
