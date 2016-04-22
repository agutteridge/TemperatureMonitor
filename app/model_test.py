import unittest
from unittest import TestCase
import datetime
from datetime import timedelta
import model
import daily

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

    def test_fetch_24hrs(self):
        model.store_temp(self.test_db, [22.2, current_time])
        model.store_temp(
            self.test_db, [
                22.2,
                current_time - timedelta(hours=25)])
        result = model.fetch_24hrs(self.test_db)
        assert(result == [(22.2, current_time)])

    def test_fetch_24hrs_empty(self):
        model.store_temp(
            self.test_db, [
                22.2,
                current_time - timedelta(hours=25)])
        result = model.fetch_24hrs(self.test_db)
        assert(result == [])

    def test_get_last_reading(self):
        model.store_temp(
            self.test_db, [
                22.2,
                current_time - timedelta(hours=25)])
        model.store_temp(self.test_db, [22.2, current_time])
        result = model.get_last_reading(self.test_db)
        assert(result == (22.2, current_time))

    def test_min_max_mean(self):
        model.store_temp(self.test_db, [22.2, current_time])
        model.store_temp(self.test_db, [22.4, current_time])
        rows = model.fetch_24hrs(self.test_db)
        result = daily.min_max_mean(rows)
        assert(result == [22.2, 22.4, 22.3])

    def test_insert_day(self):
        values = [20.0, 21.0, 20.2]
        daily.insert_day(self.test_db, values)
        yesterday = (
            datetime.date.today() -
            timedelta(days=1)).strftime('%Y-%m-%d')
        c = self.test_db.cursor()
        c.execute('''SELECT * FROM Days''')
        result = c.fetchone()
        c.close()
        assert(result[0].strftime('%Y-%m-%d') == yesterday)
        assert(list(result[1:4]) == values)

    def test_remove_yesterday(self):
        model.store_temp(self.test_db, [22.2, current_time])
        model.store_temp(
            self.test_db, [
                22.2,
                current_time - timedelta(days=1)])
        daily.remove_yesterday(self.test_db)
        c = self.test_db.cursor()
        c.execute('''SELECT * FROM Readings''')
        result = c.fetchall()
        assert(result == [(22.2, current_time)])

    def tearDown(self):
        c = self.test_db.cursor()
        c.execute('''DROP TABLE IF EXISTS Readings''')
        c.execute('''DROP TABLE IF EXISTS Days''')
        self.test_db.commit()
        self.test_db.close()


if __name__ == '__main__':
    unittest.main()
